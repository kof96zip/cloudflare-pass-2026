import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from seleniumbase import SB
from loguru import logger

# ==========================================
# 1. 核心 API 导入 (完全不改)
# ==========================================
try:
    from bypass import bypass_cloudflare as api_core_1
    from simple_bypass import bypass_cloudflare as api_core_2
    from simple_bypass import bypass_parallel as api_core_3
    from bypass_seleniumbase import bypass_logic as api_core_4
    logger.info("📡 核心 API 插件已成功挂载至主程序")
except Exception as e:
    logger.error(f"🚨 API 加载失败: {e}")

# ==========================================
# 2. TG 通知功能 (完全不改)
# ==========================================
def send_tg_notification(status, message, photo_path=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id): return
    
    tz_bj = timezone(timedelta(hours=8))
    bj_time = datetime.now(tz_bj).strftime('%Y-%m-%d %H:%M:%S')
    emoji = "✅" if "成功" in status else "⚠️" if "执行中" in status else "❌"
    
    formatted_msg = (
        f"{emoji} **矩阵自动化续期报告**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 **账户**: `{os.environ.get('EMAIL', 'Unknown')}`\n"
        f"📡 **状态**: {status}\n"
        f"📝 **详情**: {message}\n"
        f"🕒 **北京时间**: `{bj_time}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", 
                              data={'chat_id': chat_id, 'caption': formatted_msg, 'parse_mode': 'Markdown'}, files={'photo': f})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          data={'chat_id': chat_id, 'text': formatted_msg, 'parse_mode': 'Markdown'})
    except Exception as e: logger.error(f"TG通知失败: {e}")

# ==========================================
# 3. 自动化续期主流程 (一步到位版)
# ==========================================
# 直接把目标详情页定义为起始点
target_server_url = "https://betadash.lunes.host/servers/52794"
OUTPUT_DIR = Path("/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_auto_renew():
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    ui_mode = os.environ.get("BYPASS_MODE", "1. 基础单次模式")
    stay_time = int(os.environ.get("STAY_TIME", 10))
    refresh_count = int(os.environ.get("REFRESH_COUNT", 3))
    refresh_interval = int(os.environ.get("REFRESH_INTERVAL", 5))

    with SB(uc=True, xvfb=True) as sb:
        try:
            # 第一步：直接访问详情页，系统会自动带你去登录页
            logger.info(f"正在直接访问目标详情页: {target_server_url}")
            sb.uc_open_with_reconnect(target_server_url, 10)

            # 第二步：填表 (此时页面应该已经自动跳到了登录页)
            logger.info("正在定位登录表单...")
            sb.wait_for_element_visible("#email", timeout=25)
            sb.type("#email", email)
            sb.type("#password", password)
            
            # 第三步：处理验证 (维持你的核心API)
            current_url = sb.get_current_url()
            if "1." in ui_mode: api_core_1(current_url)
            elif "2." in ui_mode: api_core_2(current_url, proxy=os.environ.get("PROXY"))
            elif "4." in ui_mode: api_core_4(sb)
            
            try: sb.uc_gui_click_captcha()
            except: pass
            
            # 第四步：点击登录，登录成功后系统会自动返回到详情页
            logger.info("点击登录，等待系统自动回跳...")
            sb.click('button.submit-btn')
            
            # 暴力等待登录完成和自动回跳
            sb.sleep(15) 

            # 第五步：停留与保活刷新
            logger.info(f"正在详情页执行停留保活 (URL: {sb.get_current_url()})...")
            sb.sleep(stay_time)
            
            for i in range(refresh_count):
                logger.info(f"执行保活刷新 ({i+1}/{refresh_count})...")
                sb.refresh()
                sb.sleep(refresh_interval)

            # 第六步：保存成果并报告
            final_img = str(OUTPUT_DIR / "final_result.png")
            sb.save_screenshot(final_img)
            send_tg_notification("保活成功 ✅", f"服务器续期访问成功！", final_img)

        except Exception as e:
            error_img = str(OUTPUT_DIR / "error.png")
            sb.save_screenshot(error_img)
            logger.error(f"任务异常: {str(e)}")
            send_tg_notification("执行异常 ❌", f"错误详情: `{str(e)}`", error_img)
            raise e

if __name__ == "__main__":
    run_auto_renew()
