#!/bin/bash
# ================= OpenClaw 远程助手安装脚本 =================
# 运行方式: curl -s https://raw.githubusercontent.com/xrs-b/PocketLedger/main/scripts/remote-helper.sh | bash
# ============================================================

set -e

echo "🔧 正在安装 OpenClaw 远程助手..."

# 创建目录
mkdir -p ~/.openclaw/mcp-server

# 创建 MCP Server
cat > ~/.openclaw/mcp-server/mcp-server.js << 'MCP_EOF'
const http = require('http');

const PORT = 18790;
const ALLOWED_COMMANDS = [
  'openclaw gateway restart',
  'openclaw gateway status',
  'date',
  'uptime',
  'ps aux | grep openclaw',
  'docker ps',
  'docker-compose ps',
  'docker-compose logs --tail=20',
];

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const { command } = JSON.parse(body);
        
        // 安全检查：只允许白名单命令
        const isAllowed = ALLOWED_COMMANDS.some(cmd => 
          command.startsWith(cmd)
        );
        
        if (!isAllowed) {
          res.writeHead(403);
          res.end(JSON.stringify({ error: '命令未授权' }));
          return;
        }
        
        // 执行命令
        const { execSync } = require('child_process');
        const output = execSync(command, { encoding: 'utf8', timeout: 30000 });
        
        res.writeHead(200);
        res.end(JSON.stringify({ result: output }));
      } catch (error) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: error.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`🔧 MCP Server running on http://localhost:${PORT}`);
});
MCP_EOF

echo "✅ MCP Server 已创建"

# 创建开机自启配置
cat > ~/Library/LaunchAgents/com.openclaw.mcp.plist << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.openclaw.mcp</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/node</string>
    <string>/Users/oink/.openclaw/mcp-server/mcp-server.js</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
PLIST_EOF

echo "✅ 开机自启配置已创建"

# 加载开机自启
launchctl load ~/Library/LaunchAgents/com.openclaw.mcp.plist 2>/dev/null || echo "⚠️ 可能需要管理员权限加载自启"

# 立即启动 MCP Server
node ~/.openclaw/mcp-server/mcp-server.js &
echo "🚀 MCP Server 已启动"

# 验证
sleep 2
echo ""
echo "========== 安装完成 =========="
echo ""
echo "🔧 验证 MCP Server:"
curl -s http://localhost:18790 -d '{"command":"date"}'
echo ""
echo "================================"
echo ""
echo "📝 常用命令:"
echo "   - 查看 OpenClaw 状态: curl -s http://localhost:18790 -d '{\"command\":\"openclaw gateway status\"}'"
echo "   - 重启 OpenClaw: curl -s http://localhost:18790 -d '{\"command\":\"openclaw gateway restart\"}'"
echo "   - 查看 Docker: curl -s http://localhost:18790 -d '{\"command\":\"docker ps\"}'"
echo ""
echo "✅ 远程助手安装完成！"
