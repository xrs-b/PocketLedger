#!/bin/bash
# ================= 一键安装 ngrok 并配置 MCP 隧道 =================
# 运行方式: curl -s https://raw.githubusercontent.com/xrs-b/PocketLedger/main/scripts/install-ngrok.sh | bash
# ==============================================================

set -e

echo "🔧 正在安装 ngrok..."

# 1. 安装 ngrok
if ! command -v ngrok &> /dev/null; then
    brew install ngrok
else
    echo "✅ ngrok 已安装"
fi

# 2. 停止旧的 ngrok 进程
pkill -f "ngrok" 2>/dev/null || true

# 3. 启动 ngrok 隧道
echo "🚀 正在启动 ngrok 隧道..."
ngrok http 18790 --log=stdout > ~/.openclaw/ngrok.log 2>&1 &

# 4. 等待 ngrok 启动
echo "⏳ 等待 ngrok 启动 (5秒)..."
sleep 5

# 5. 获取公网 URL
NGROK_URL=$(cat ~/.openclaw/ngrok.log 2>/dev/null | grep -o 'https://[^ ]*\.trycloudflare.com' | head -1)

if [ -n "$NGROK_URL" ]; then
    echo ""
    echo "========== 安装完成 =========="
    echo ""
    echo "🔗 公网 URL: $NGROK_URL"
    echo ""
    echo "把这个 URL 告诉 AI 助手，"
    echo "它就可以帮你执行任何命令了！"
    echo ""
    echo "================================"
    
    # 保存 URL
    echo "$NGROK_URL" > ~/.openclaw/ngrok.url
else
    echo "❌ 未能获取 ngrok URL"
    echo "日志: ~/.openclaw/ngrok.log"
fi
