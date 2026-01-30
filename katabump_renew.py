import os
import time
import json
import random
from datetime import datetime
from pathlib import Path
import requests
from seleniumbase import SB

def send_tg_notification(message, photo_path=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id): return
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data={'chat_id': chat_id, 'caption': message}, files={'photo': f})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={'chat_id': chat_id, 'text': message})
    except Exception as e: print(f"TG通知失败: {e}")

def run_auto_renew():
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    ui_mode = os.environ.get("BYPASS_MODE", "SB增强模式")
    
    login_url = "https://dashboard.katabump.com/login"
    target_url = "https://dashboard.katabump.com/servers/edit?id=177688"
    OUTPUT_DIR = Path("/app/output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] 针对 2026-01-29 结构启动流程")

    with SB(uc=True, xvfb=True) as sb:
        try:
            # ---- 步骤 1: 登录 (处理 <font>登录</font>) ----
            print(">>> [1/5] 正在打开登录页...")
            sb.uc_open_with_reconnect(login_url, 10)
            sb.uc_gui_click_captcha() # 入场过盾
            
            sb.wait_for_element("#email", timeout=20)
            sb.type("#email", email)
            sb.type("#password", password)
            
            print(">>> 正在点击 <font>登录</font>...")
            # 使用 XPath 确保能点到被 font 标签包裹的文字
            sb.click('//button[contains(., "登录")]') 
            sb.sleep(5)

            # ---- 步骤 2: 进入编辑页 ----
            print(">>> [2/5] 正在跳转至 See 页面...")
            sb.uc_open_with_reconnect(target_url, 10)
            sb.sleep(3)

            # ---- 步骤 3: 触发续期弹窗 ----
            print(">>> [3/5] 点击 Renew 按钮...")
            sb.scroll_to('button[data-bs-target="#renew-modal"]')
            sb.js_click('button[data-bs-target="#renew-modal"]') # JS点击防止遮挡
            sb.sleep(4) 

            # ---- 步骤 4: 核心人机验证 (UI模式调用) ----
            print(f">>> [4/5] 触发验证码，执行 [{ui_mode}] 破解算法...")
            if "增强" in ui_mode:
                sb.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
            
            # 模拟物理点击“我是真人”
            sb.uc_gui_click_captcha() 
            print("    [OK] 人机校验已尝试过盾")
            sb.sleep(5)

            # ---- 步骤 5: 最终点击 <font>更新</font> ----
            print(">>> [5/5] 正在点击最终的 <font>更新</font> 按钮...")
            # 同样使用 XPath 定位 font 包裹的更新文字
            sb.click('//button[contains(., "更新")]')
            sb.sleep(8)

            # 保存成功截图
            success_img = str(OUTPUT_DIR / "success_final.png")
            sb.save_screenshot(success_img)
            print(">>> [完成] 2026-01-29 完整流程跑通")
            send_tg_notification(f"✅ 续期同步成功！模式: {ui_mode}", success_img)

        except Exception as e:
            error_img = str(OUTPUT_DIR / "error_font_issue.png")
            sb.save_screenshot(error_img)
            print(f"❌ 流程中断: {e}")
            send_tg_notification(f"❌ 续期失败\n错误详情: {str(e)}", error_img)
            raise e

if __name__ == "__main__":
    run_auto_renew()
