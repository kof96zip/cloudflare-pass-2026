import os
import time
from datetime import datetime
from pathlib import Path
import requests
from seleniumbase import SB
from loguru import logger

# ==========================================
# 步骤 1: 按照仓库 API 规范导入三个插件
# ==========================================
try:
    # API 1: 来自 bypass.py 的简单模式
    from bypass import bypass_cloudflare as api_bypass_simple
    
    # API 2 & 3: 来自 simple_bypass.py 的完整模式 (单次与并行)
    from simple_bypass import bypass_cloudflare as api_simple_once
    from simple_bypass import bypass_parallel as api_simple_parallel
    
    logger.info("📡 成功加载三大核心绕过 API 接口")
except ImportError as e:
    logger.error(f"🚨 模块导入失败，请检查脚本是否在根目录: {e}")

def send_tg_notification(message, photo_path=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id): return
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", 
                              data={'chat_id': chat_id, 'caption': message}, files={'photo': f})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          data={'chat_id': chat_id, 'text': message})
    except Exception as e: logger.error(f"TG通知失败: {e}")

def run_auto_renew():
    # 从环境变量（UI输入）获取凭据
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    ui_mode = os.environ.get("BYPASS_MODE", "单浏览器模式") # 默认模式
    
    # 2026-01-29 目标地址
    login_url = "https://dashboard.katabump.com/auth/login"
    target_url = "https://dashboard.katabump.com/servers/edit?id=177688"
    OUTPUT_DIR = Path("/app/output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logger.info(f"🚀 启动自动续期流程 | 当前 API 模式: {ui_mode}")

    # 使用集成了 UC 模式的浏览器
    with SB(uc=True, xvfb=True) as sb:
        try:
            # ---- 1. 执行登录 (匹配 id="submit") ----
            logger.info("正在登录 Katabump...")
            sb.uc_open_with_reconnect(login_url, 10)
            sb.wait_for_element("#email", timeout=20)
            sb.type("#email", email)
            sb.type("#password", password)
            sb.click("#submit") 
            sb.sleep(6)

            # ---- 2. 跳转管理页 ----
            logger.info("跳转至服务器配置页面...")
            sb.uc_open_with_reconnect(target_url, 10)
            sb.sleep(3)

            # ---- 3. 触发 Renew 弹窗 ----
            logger.info("触发续期验证弹窗...")
            sb.scroll_to('button[data-bs-target="#renew-modal"]')
            sb.js_click('button[data-bs-target="#renew-modal"]')
            sb.sleep(5) 

            # ---- 4. 核心：根据工作方式调用 API ----
            # 自动提取当前网址作为 API 的输入参数
            current_target_url = sb.get_current_url()
            logger.info(f"🔗 正在为网址调用 API: {current_target_url}")
            
            result = {"success": False}

            if "单浏览器" in ui_mode:
                # 调用 bypass.py 的简单模式接口
                logger.info(">>> 激活 API-1: bypass_cloudflare (来自 bypass.py)")
                result = api_bypass_simple(current_target_url)
                
            elif "单次绕过" in ui_mode:
                # 调用 simple_bypass.py 的单次接口 (支持传代理)
                logger.info(">>> 激活 API-2: bypass_cloudflare (来自 simple_bypass.py)")
                result = api_simple_once(current_target_url, proxy=os.environ.get("PROXY"))
                
            elif "并行模式" in ui_mode:
                # 调用 simple_bypass.py 的并行竞争接口
                logger.info(">>> 激活 API-3: bypass_parallel (来自 simple_bypass.py)")
                result = api_simple_parallel(
                    url=current_target_url, 
                    proxy_file="proxy.txt",
                    batch_size=3
                )

            # ---- 5. 整合 API 结果并提交 ----
            if result.get("success"):
                logger.success(f"✅ API 绕过成功！获取到 Cookie: {result.get('cf_clearance', 'N/A')}")
                # 执行最后的物理模拟点击
                sb.uc_gui_click_captcha()
                sb.sleep(4)
            else:
                logger.warning("⚠️ API 未能直接返回成功，尝试手动物理过盾...")
                sb.uc_gui_click_captcha()

            logger.info("执行最终点击更新...")
            sb.click('//button[contains(., "更新")]') # 适配 <font> 标签
            sb.sleep(8)

            # 结果反馈
            success_img = str(OUTPUT_DIR / "success.png")
            sb.save_screenshot(success_img)
            send_tg_notification(f"✅ 续期任务成功！模式: {ui_mode}", success_img)
            logger.success("全部任务已完成")

        except Exception as e:
            error_img = str(OUTPUT_DIR / "error.png")
            sb.save_screenshot(error_img)
            logger.error(f"❌ 流程出错: {str(e)}")
            send_tg_notification(f"❌ 续期失败\n原因: {str(e)}", error_img)
            raise e

if __name__ == "__main__":
    run_auto_renew()
