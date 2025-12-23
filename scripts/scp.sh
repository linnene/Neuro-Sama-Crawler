#!/usr/bin/env bash
set -euo pipefail

# ========= 配置区 =========
LOCAL_USER="localuser"

# 反向隧道对应的端口（必须和本地脚本一致）
TUNNEL_PORT=2222

REMOTE_DIR="/app/output/"
LOCAL_DIR=""

# ========= 日志 =========
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/push_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"

echo "===== Push started: $(date) =====" | tee -a "$LOG_FILE"

# ========= 推送数据 =========
rsync -avz \
  --human-readable \
  -e "ssh -p ${TUNNEL_PORT}" \
  ${REMOTE_DIR} \
  ${LOCAL_USER}@localhost:${LOCAL_DIR} >> "$LOG_FILE" 2>&1

echo "===== Push finished: $(date) =====" | tee -a "$LOG_FILE"
