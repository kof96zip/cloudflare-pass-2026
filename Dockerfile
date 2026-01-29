FROM python:3.10-slim

# 1. 设置系统环境变量，避免安装过程中的交互提醒
ENV DEBIAN_FRONTEND=noninteractive

# 2. 安装系统依赖 (对应你 install_linux.sh 的 [2/5] 步骤)
RUN apt-get update -qq && apt-get install -y -qq \
    xvfb \
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

# 3. 安装 Google Chrome (对应你 install_linux.sh 的 [3/5] 步骤)
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y -qq /tmp/chrome.deb \
    && rm -f /tmp/chrome.deb

WORKDIR /app
COPY . .

# 4. 安装 Python 依赖 (对应你 install_linux.sh 的 [4/5] 步骤)
# 假设你已经准备好了 requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pyvirtualdisplay seleniumbase loguru

# 5. 启动命令
# 在容器中运行必须配合 xvfb-run
# 假设你想运行 simple_bypass.py，目标 URL 可以根据需要修改
CMD ["xvfb-run", "python", "simple_bypass.py", "https://nowsecure.nl"]
