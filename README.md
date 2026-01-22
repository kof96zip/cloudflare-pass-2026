# Cloudflare Bypass Tool 2026

基于 SeleniumBase UC Mode 的 Cloudflare Turnstile 验证绕过工具

A Cloudflare Turnstile bypass tool based on SeleniumBase UC Mode

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Windows%20%7C%20Linux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 免责声明 / Disclaimer

本工具仅供学习研究使用，请遵守相关法律法规和目标网站的服务条款。

This tool is for educational purposes only. Please comply with applicable laws and website terms of service.

---

## 测试结果 / Test Results

| 方法 Method | 状态 Status | cf_clearance | 耗时 Time |
|:---:|:---:|:---:|:---:|
| SeleniumBase UC Mode | OK | Yes | ~35s |
| 直连模式 Direct | OK | Yes | ~35s |

---

## 功能特点 / Features

- **SeleniumBase UC Mode** - 操作系统级鼠标模拟，最稳定
- **单浏览器模式** - 简单可靠，推荐使用
- **跨平台支持** - Mac / Windows / Linux
- **Cookie保存** - JSON和Netscape格式

---

## 快速开始 / Quick Start

```bash
# 安装 Install
pip install seleniumbase

# 运行 Run
python bypass.py https://your-target-site.com
```

---

## 安装部署 / Installation

### Mac / Windows

```bash
git clone https://github.com/1837620622/cloudflare-bypass-2026.git
cd cloudflare-bypass-2026
pip install -r requirements.txt
python bypass.py https://example.com
```

### Linux (Ubuntu/Debian)

```bash
# 一键安装 One-click install
git clone https://github.com/1837620622/cloudflare-bypass-2026.git
cd cloudflare-bypass-2026
sudo bash install_linux.sh
python bypass.py https://example.com
```

手动安装 / Manual install:
```bash
sudo apt-get update
sudo apt-get install -y xvfb libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libgbm1 libasound2

# 安装Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Python依赖
pip install seleniumbase pyvirtualdisplay
```

---

## 使用方法 / Usage

### 命令行 / Command Line

```bash
# 基础用法
python bypass.py https://example.com

# 使用代理
python bypass.py https://example.com -p http://127.0.0.1:7890
```

### 参数说明 / Parameters

| 参数 | 说明 | 默认值 |
|:---|:---|:---:|
| `url` | 目标网站URL | 必填 |
| `-p, --proxy` | 代理地址 | 无 |
| `-t, --timeout` | 超时时间(秒) | 60 |
| `--no-save` | 不保存Cookie | 否 |

### Python API

```python
from bypass import bypass_cloudflare

result = bypass_cloudflare("https://example.com")

if result["success"]:
    print(f"cf_clearance: {result['cf_clearance']}")
    print(f"Cookies: {result['cookies']}")
    print(f"User-Agent: {result['user_agent']}")
else:
    print(f"Error: {result['error']}")
```

---

## 项目结构 / Project Structure

```
cloudflare-bypass-2026/
├── bypass.py             # 主程序 (推荐) Main script (recommended)
├── simple_bypass.py      # 完整版 (更多功能) Full version
├── bypass_seleniumbase.py # 详细版 Detailed version
├── install_linux.sh      # Linux安装脚本
├── requirements.txt      # Python依赖
├── proxy.txt             # 代理列表示例
└── README.md
```

---

## 输出文件 / Output Files

Cookie保存到 `output/cookies/` 目录:

- `cookies_*.json` - JSON格式
- `cookies_*.txt` - Netscape格式 (可用于 curl -b)

---

## 常见问题 / FAQ

**Q: 为什么不用无头模式?**

A: Cloudflare可检测无头浏览器，建议保持可视化模式。

**Q: cf_clearance有效期?**

A: 通常30分钟到数小时，建议过期前重新获取。

**Q: Linux报错 "X11 display failed"?**

A: 运行 `sudo bash install_linux.sh` 安装依赖。

---

## 技术参考 / References

- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/)
- [SeleniumBase](https://seleniumbase.com/)

---

## License

MIT License - 2026

---

如果这个项目对你有帮助，请给个 Star!

If this project helps you, please give it a Star!
