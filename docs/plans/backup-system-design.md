# OpenClaw 备份系统设计

## 需求概述
为 OpenClaw 创建定时备份系统，用于快速恢复环境

## 备份范围

### 核心配置 (必须备份)
1. **~/.openclaw/**
   - `openclaw.json` - 主配置
   - `agents/` - Agent 配置
   - `credentials/` - 凭证配置
   - `identity/` - 身份配置
   - `cron/` - 定时任务配置
   - `subagents/` - Subagent 配置
   - `workspace/` - 工作区 (含 PocketLedger 项目)

2. **MCP 配置**
   - `~/.mcporter/mcporter.json` - MCP Server 配置
   - `~/.config/opencode/superpowers/` - Superpowers 配置

3. **系统配置 (可选)**
   - `~/.ssh/` - SSH 配置 (敏感，只备份公钥)
   - Shell 配置: `.zshrc`, `.bashrc`

### 不备份的内容
- `logs/` - 日志文件
- `media/` - 媒体文件
- `~/.cache/` - 缓存文件
- `node_modules/` - 依赖目录

## 技术方案

### 备份机制
1. **本地备份目录**: `~/.openclaw/backups/`
2. **备份格式**: 压缩包 `.tar.gz`，按时间命名
3. **GitHub 仓库**: 新建私人仓库 `openclaw-backups`

### 保留策略
- 本地: 保留最近 20 个备份
- GitHub: 保留最近 20 个备份
- 超过则自动删除旧备份

### 定时任务
- 频率: 每小时执行一次
- 使用: OpenClaw cron 功能

## 实施步骤

### 1. 创建备份脚本
- `backup-openclaw.sh` - 主备份脚本
- 功能: 打包、压缩、上传 GitHub、清理旧备份

### 2. 创建 GitHub 仓库
- 使用 gh CLI 创建私人仓库
- 配置 SSH remote

### 3. 设置定时任务
- 使用 cron 工具设置每小时执行

## 备份文件命名
```
openclaw-backup-YYYYMMDD-HHMMSS.tar.gz
```
例如: `openclaw-backup-20260205-200000.tar.gz`

## 恢复流程
1. 下载最新备份
2. 解压到对应目录
3. 重启 OpenClaw
