import streamlit as st
import json
import os
import subprocess
import time

# 配置文件存放在持久化目录
CONFIG_FILE = "/app/output/tasks_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 默认初始项目
    return [{"name": "Katabump续期", "script": "katabump_renew.py", "email": "", "password": "", "freq": 3, "active": True}]

def save_config(tasks):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="自动化任务管理器", layout="wide")
st.title("🤖 多项目自动化续期管理中心")

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_config()

# --- 侧边栏：添加新脚本 ---
with st.sidebar:
    st.header("➕ 添加新项目")
    new_name = st.text_input("项目备注名称")
    # 自动识别你截图里的那些文件名
    available_scripts = ["katabump_renew.py", "bypass.py", "bypass_seleniumbase.py", "simple_bypass.py"]
    new_script = st.selectbox("关联脚本文件", available_scripts)
    
    if st.button("添加至列表"):
        st.session_state.tasks.append({"name": new_name, "script": new_script, "email": "", "password": "", "freq": 3, "active": True})
        save_config(st.session_state.tasks)
        st.success("已添加！")

# --- 主界面：配置区 ---
updated_tasks = []
st.subheader("📋 任务列表 (配置自动保存)")

for i, task in enumerate(st.session_state.tasks):
    with st.expander(f"项目: {task['name']} (调用 {task['script']})", expanded=True):
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
        task['active'] = col1.checkbox("启用", value=task.get('active', True), key=f"active_{i}")
        task['email'] = col2.text_input("账号", value=task.get('email', ''), key=f"email_{i}")
        task['password'] = col3.text_input("密码", type="password", value=task.get('password', ''), key=f"pw_{i}")
        task['freq'] = col4.number_input("周期(天)", value=task.get('freq', 3), key=f"freq_{i}")
        if col5.button("🗑️ 删除", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            save_config(st.session_state.tasks)
            st.rerun()
        updated_tasks.append(task)

if st.button("💾 保存所有配置"):
    save_config(updated_tasks)
    st.success("✅ 配置已持久化保存！即使重启服务也不会丢失。")

st.divider()

# --- 执行区 ---
if st.button("🚀 统一点执行 (一键跑通所有流程)"):
    with st.status("正在依次执行已启用的任务...", expanded=True) as status:
        for task in updated_tasks:
            if task['active']:
                st.write(f"正在运行: {task['name']}...")
                env = os.environ.copy()
                env["EMAIL"] = task['email']
                env["PASSWORD"] = task['password']
                
                # 严格调用原始脚本
                cmd = ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "python", task['script']]
                process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                
                out_box = st.empty()
                full_out = ""
                for line in process.stdout:
                    full_out += line
                    out_box.code(full_out)
                process.wait()
        status.update(label="✨ 所有流程已跑完，请检查 TG 截图！", state="complete")
