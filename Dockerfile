FROM python:3.10-slim

# 1. 设置系统环境变量，避免安装过程中的交互提醒
ENV DEBIAN_FRONTEND=noninteractive

# 2. 安装系统依赖 (补全了 xauth)
RUN apt-get update -qq && apt-get install -y -qq \
    xvfb \
    xauth \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    wget \
    curl \
    unzip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3. 安装 Google Chrome
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y -qq /tmp/chrome.deb \
    && rm -f /tmp/chrome.deb

WORKDIR /app
COPY . .

# 4. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt
# 在此处增加了 streamlit 依赖，用于实现你要求的可视化 UI
RUN pip install pyvirtualdisplay seleniumbase loguru streamlit

# 5. 启动命令
# 修改说明：根据你的要求，将启动方式改为运行 streamlit 界面，从而实现可视化操作
# 端口设置为 8080 以符合 Zeabur 的默认网络配置
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
