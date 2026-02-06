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
# 3. 自动化操作主流程
# ==========================================
target_url = "https://justrunmy.app/"
panel_url = "https://justrunmy.app/panel/application/4683/"
OUTPUT_DIR = Path("/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_auto_operations():
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    
    with SB(uc=True, xvfb=True) as sb:
        try:
            # Step 1: Navigate to the main site and log in
            logger.info(f"正在访问目标网站: {target_url}")
            sb.open(target_url)

            # Step 2: Wait for login form, fill out and submit
            sb.wait_for_element_visible("#email", timeout=25)
            sb.type("#email", email)
            sb.type("#password", password)
            sb.click('button[type="submit"]')

            # Step 3: Wait for the login process to complete
            logger.info("登录完成，跳转至面板页面...")
            sb.sleep(5)  # Wait for the page to load

            # Step 4: Navigate to the panel application page
            sb.open(panel_url)
            sb.wait_for_element_visible(".reset-timer-button", timeout=25)
            
            # Step 5: Click on "reset timer" and "Just Reset"
            logger.info("点击重置计时器按钮...")
            sb.click(".reset-timer-button")
            sb.wait_for_element_visible(".just-reset-button", timeout=25)
            sb.click(".just-reset-button")
            
            # Step 6: Wait and capture screenshot of the result
            sb.sleep(5)  # Wait for the reset to complete
            final_img = str(OUTPUT_DIR / "final_result.png")
            sb.save_screenshot(final_img)
            send_tg_notification("操作成功 ✅", f"计时器已成功重置！", final_img)

        except Exception as e:
            error_img = str(OUTPUT_DIR / "error.png")
            sb.save_screenshot(error_img)
            logger.error(f"任务异常: {str(e)}")
            send_tg_notification("执行异常 ❌", f"错误详情: `{str(e)}`", error_img)
            raise e

if __name__ == "__main__":
    run_auto_operations()
