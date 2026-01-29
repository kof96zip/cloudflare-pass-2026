import json
import os
import subprocess
from datetime import datetime, timedelta

CONFIG_FILE = "/app/output/tasks_config.json"

def run_scheduler():
    if not os.path.exists(CONFIG_FILE):
        print("[*] 尚未配置任何任务。")
        return

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    now = datetime.now()
    updated = False

    for task in tasks:
        if not task.get('active', True): continue
        
        last_run_str = task.get('last_run')
        freq = task.get('freq', 3)
        
        should_run = False
        if not last_run_str:
            should_run = True
        else:
            last_run_time = datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S")
            if now >= (last_run_time + timedelta(days=freq)):
                should_run = True

        if should_run:
            print(f"[*] 自动执行: {task['name']} | 模式: {task.get('mode', '默认')}")
            env = os.environ.copy()
            env["EMAIL"] = task['email']
            env["PASSWORD"] = task['password']
            env["BYPASS_MODE"] = task.get('mode', '单浏览器模式') # 同步模式设置
            
            try:
                # 统一使用 xvfb 运行，确保验证码点击生效
                subprocess.run([
                    "xvfb-run", "--server-args=-screen 0 1920x1080x24", 
                    "python", task['script']
                ], env=env, check=True)
                task['last_run'] = now.strftime("%Y-%m-%d %H:%M:%S")
                updated = True
            except Exception as e:
                print(f"[!] 执行失败: {e}")

    if updated:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scheduler()
