#!/bin/bash

# 获取 Git 仓库根目录
REPO_DIR=$(git rev-parse --show-toplevel 2>/dev/null)

# 如果不是 Git 仓库，退出
if [ -z "$REPO_DIR" ]; then
  echo "[`date '+%F %T'`] ❌ 当前目录不在 Git 仓库中" >&2
  exit 1
fi

# 日志文件
LOG_FILE="$REPO_DIR/push_log.txt"

# 进入仓库目录
cd "$REPO_DIR" || {
  echo "[`date '+%F %T'`] ❌ 无法进入目录: $REPO_DIR" >> "$LOG_FILE"
  exit 1
}

echo "[`date '+%F %T'`] ▶️ 启动循环 git push ..." >> "$LOG_FILE"

# 无限循环，每 5 秒执行一次
while true; do

  # 添加并提交
  git add . >> "$LOG_FILE" 2>&1
  git commit -m "Auto commit: `date '+%F %T'`" >> "$LOG_FILE" 2>&1

  # 推送到远程
  git push >> "$LOG_FILE" 2>&1

  sleep 60
done

#  后台执行方式: $sh loop_push.sh &