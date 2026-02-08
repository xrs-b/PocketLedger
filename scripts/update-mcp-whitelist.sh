#!/bin/bash
# ================= 更新 MCP Server 白名单 =================

echo "🔧 正在更新 MCP Server..."

cat > ~/.openclaw/mcp-server/mcp-server.js << 'MCP_EOF'
const http = require('http');

const PORT = 18790;
const ALLOWED_COMMANDS = [
  'openclaw gateway restart',
  'openclaw gateway status',
  'launchctl bootout gui/',
  'launchctl load gui/',
  'launchctl unload gui/',
  'launchctl list',
  'sudo launchctl bootout gui/',
  'sudo launchctl load gui/',
  'sudo launchctl unload gui/',
  'rm ~/Library/LaunchAgents/',
  'rm ~/.openclaw/',
  'date',
  'uptime',
  'ps aux | grep openclaw',
  'docker ps',
  'docker-compose ps',
  'docker-compose logs --tail=20',
  'docker-compose down',
  'docker-compose up -d',
  'docker-compose restart',
];

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const { command } = JSON.parse(body);
        
        const isAllowed = ALLOWED_COMMANDS.some(cmd => 
          command.startsWith(cmd)
        );
        
        if (!isAllowed) {
          res.writeHead(403);
          res.end(JSON.stringify({ error: '命令未授权' }));
          return;
        }
        
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

echo "✅ MCP Server 已更新"

pkill -f "node.*mcp-server" 2>/dev/null
node ~/.openclaw/mcp-server/mcp-server.js &

echo "🚀 MCP Server 已重启"
