import streamlit as st
import json
import os
import subprocess
import time
from datetime import datetime, timedelta

# 配置文件路径
CONFIG_FILE = "/app/output/tasks_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [{"name": "Katabump自动续期", "script": "katabump_renew.py", "mode": "SB增强模式", "email": "", "password": "", "freq": 3, "active": True, "last_run": None}]

def save_config(tasks):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# --- 页面配置 ---
st.set_page_config(page_title="MATRIX 自动化控制中心", layout="wide", initial_sidebar_state="expanded")

# 自定义高科技感 CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ffc8; }
    .stButton>button { background-color: #00ffc8; color: black; border-radius: 5px; border: none; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff00ff; color: white; box-shadow: 0 0 15px #ff00ff; }
    .stExpander { border: 1px solid #00ffc8 !important; background-color: #1a1c24 !important; }
    code { color: #ff00ff !important; }
    .status-lamp { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .lamp-on { background-color: #00ffc8; box-shadow: 0 0 10px #00ffc8; }
    .lamp-off { background-color: #555; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ MATRIX 自动化续期内核")
st.caption("核心版本: 2026.01.29 | 环境: Zeabur Cloud")

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_config()

# --- 侧边栏 ---
with st.sidebar:
    st.header("🧬 终端接入")
    new_name = st.text_input("项目识别码", placeholder="例如: Katabump_01")
    if st.button("➕ 注入新进程"):
        st.session_state.tasks.append({
            "name": new_name, "script": "katabump_renew.py", 
            "mode": "SB增强模式", "email": "", "password": "", "freq": 3, "active": True, "last_run": None
        })
        save_config(st.session_state.tasks)
        st.rerun()

# --- 主界面 ---
updated_tasks = []
st.subheader("🛰️ 实时任务轨道")

for i, task in enumerate(st.session_state.tasks):
    # 状态灯显示
    lamp_class = "lamp-on" if task.get('active') else "lamp-off"
    with st.expander(f"PROJECT: {task['name']}", expanded=True):
        st.markdown(f'<div><span class="status-lamp {lamp_class}"></span> 进程状态: {"ACTIVE" if task.get("active") else "STANDBY"}</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 1, 0.5])
        
        # 1. 启用开关
        task['active'] = c1.checkbox("激活序列", value=task.get('active', True), key=f"active_{i}")
        
        # 2. 模式选择 (这决定了 katabump_renew.py 第四步调用哪个逻辑)
        mode_list = ["单浏览器模式", "SB增强模式", "并行竞争模式"]
        curr_mode = task.get('mode', "SB增强模式")
        task['mode'] = c2.selectbox("核心绕过算法 (步骤4驱动)", mode_list, index=mode_list.index(curr_mode) if curr_mode in mode_list else 1, key=f"mode_{i}")
        
        # 3. 凭据输入
        task['email'] = c3.text_input("ACCESS_EMAIL", value=task.get('email', ''), key=f"email_{i}")
        task['password'] = c4.text_input("ACCESS_PASS", type="password", value=task.get('password', ''), key=f"pw_{i}")
        
        # 4. 删除按钮
        if c5.button("❌", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            save_config(st.session_state.tasks)
            st.rerun()

        # 频率与时间显示
        t1, t2, t3 = st.columns([1, 2, 2])
        task['freq'] = t1.number_input("同步周期(天)", 1, 30, task.get('freq', 3), key=f"freq_{i}")
        
        last = task.get('last_run', "NEVER")
        next_date = "N/A"
        if last != "NEVER":
            next_date = (datetime.strptime(last, "%Y-%m-%d %H:%M:%S") + timedelta(days=task['freq'])).strftime("%Y-%m-%d")
        
        t2.info(f"📅 上次同步: {last}")
        t3.warning(f"⏳ 预计下次下行: {next_date}")

        updated_tasks.append(task)

if st.button("💾 写入持久化内存"):
    save_config(updated_tasks)
    st.success("数据已存入二进制扇区")

st.divider()

# --- 执行区 ---
if st.button("🚀 启动全域自动化同步"):
    log_area = st.empty()
    with st.status("正在建立神经链接...", expanded=True) as status:
        for task in updated_tasks:
            if task['active']:
                st.write(f"📡 正在呼叫项目: **{task['name']}**")
                
                # 注入环境变量
                env = os.environ.copy()
                env["EMAIL"] = task['email']
                env["PASSWORD"] = task['password']
                env["BYPASS_MODE"] = task['mode']  # 关键：传给脚本模式名称
                env["PYTHONUNBUFFERED"] = "1"
                
                # 执行脚本
                cmd = ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "python", "katabump_renew.py"]
                
                process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                full_log = ""
                for line in process.stdout:
                    full_log += line
                    # 只显示最新的 15 行日志，保持科技感
                    display_log = "\n".join(full_log.splitlines()[-15:])
                    log_area.code(f"USER@MATRIX:~$ \n{display_log}")
                
                process.wait()
                if process.returncode == 0:
                    task['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_config(updated_tasks)
                    st.success(f"✔ 项目 {task['name']} 同步完成")
                else:
                    st.error(f"✖ 项目 {task['name']} 链接中断")
        
        status.update(label="🛰️ 所有任务轨道同步完毕", state="complete", expanded=False)
