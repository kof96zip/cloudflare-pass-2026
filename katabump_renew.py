import os
import time
import json
import random
from datetime import datetime
from pathlib import Path
import requests
from seleniumbase import SB

def send_tg_notification(message, photo_path=None):
    """发送 Telegram 消息和截图"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[!] 未配置 TG 变量，跳过通知")
        return

    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", 
                              data={'chat_id': chat_id, 'caption': message}, 
                              files={'photo': photo})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          data={'chat_id': chat_id, 'text': message})
        print("[+] Telegram 通知发送成功")
    except Exception as e:
        print(f"[!] TG 通知发送失败: {e}")

def run_auto_renew():
    # 从 Zeabur 环境变量读取
    url = "https://dashboard.katabump.com/login"
    target_id_url = "https://dashboard.katabump.com/servers/edit?id=177688"
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    
    # 确保输出目录存在
    OUTPUT_DIR = Path("/app/output")
    COOKIE_DIR = OUTPUT_DIR / "cookies"
    os.makedirs(COOKIE_DIR, exist_ok=True)

    print(f"[*] [{datetime.now().strftime('%H:%M:%S')}] 脚本启动，准备执行续期流程...")

    # 启动带有虚拟显示器的反检测浏览器
    with SB(uc=True, xvfb=True) as sb:
        
        # 内部 Cookie 保存函数
        def save_cookies_safe(label=""):
            try:
                cookies = sb.get_cookies()
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = COOKIE_DIR / f"cookies_{label}_{ts}.json"
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"    [OK] 步骤进度 Cookie 已备份: {label}")
            except Exception as e:
                print(f"    [!] Cookie 备份失败: {e}")

        try:
            # ---- 第一步 ----
            print(">>> [步骤 1/6] 正在打开登录页并处理 Cloudflare 验证...")
            sb.uc_open_with_reconnect(url, 5)
            time.sleep(random.uniform(2, 4))
            sb.uc_gui_click_captcha() # 点击首页可能存在的 CF 验证
            
            # ---- 第二步 ----
            print(f">>> [步骤 2/6] 正在输入账号并登录 (Email: {email})...")
            sb.wait_for_element("#email", timeout=15) # 增加等待时间确保页面加载
            sb.type("#email", email)
            sb.type("#password", password)
            sb.click('button:contains("登录")') 
            sb.sleep(4)
            save_cookies_safe("post_login")

            # ---- 第三步 ----
            print(">>> [步骤 3/6] 登录成功，正在跳转到服务器编辑页面...")
            sb.uc_open_with_reconnect(target_id_url, 5)
            sb.sleep(2)
            
            # ---- 第四步 ----
            print(">>> [步骤 4/6] 正在滚动页面并触发续期弹窗...")
            sb.scroll_to('button[data-bs-target="#renew-modal"]')
            sb.click('button[data-bs-target="#renew-modal"]')
            sb.sleep(2)

            # ---- 第五步 ----
            print(">>> [步骤 5/6] 正在处理弹窗内的人机验证...")
            sb.uc_gui_click_captcha() 
            sb.sleep(2)

            # ---- 第六步 ----
            print(">>> [步骤 6/6] 正在提交更新申请...")
            sb.click('button:contains("更新")')
            sb.sleep(3)
            
            # 结果保存
            print(">>> [完成] 正在保存成功截图并发送通知...")
            success_screenshot = str(OUTPUT_DIR / "success_renew.png")
            sb.save_screenshot(success_screenshot)
            save_cookies_safe("final_success")
            
            success_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ 续期指令已成功发送！"
            print(success_msg)
            
            # 发送 TG 通知
            send_tg_notification(success_msg, success_screenshot)
            
            sb.sleep(2) 

        except Exception as e:
            # 如果中间任何一步报错，拍一张错误截图
            error_img = str(OUTPUT_DIR / "error_step.png")
            sb.save_screenshot(error_img)
            err_msg = f"[!] 脚本运行中断: {str(e)}"
            print(err_msg)
            send_tg_notification(err_msg, error_img)
            raise e # 重新抛出异常让 UI 捕获

if __name__ == "__main__":
    run_auto_renew()
