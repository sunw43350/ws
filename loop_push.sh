#!/bin/bash

# Git 仓库目录
REPO_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
echo $REPO_DIR
LOG_FILE="$REPO_DIR/log.txt"

# 进入仓库目录
cd "$REPO_DIR" || {
  echo "[`date '+%F %T'`] ❌ 无法进入目录: $REPO_DIR" >> "$LOG_FILE"
  exit 1
}

echo "[`date '+%F %T'`] ▶️ 启动循环 git push ..." >> "$LOG_FILE"

# 无限循环，每 30 秒执行一次
while true; do
  echo "[`date '+%F %T'`] 🔍 检查文件变更..." >> "$LOG_FILE"

  # 检查是否有未提交更改
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "[`date '+%F %T'`] 🔄 检测到变更，执行 push" >> "$LOG_FILE"

    git add . >> "$LOG_FILE" 2>&1

    git commit -m "Auto commit: `date '+%F %T'`" >> "$LOG_FILE" 2>&1

    git push >> "$LOG_FILE" 2>&1

  else
    echo "[`date '+%F %T'`] ✅ 无需 push，代码无更改" >> "$LOG_FILE"
  fi

  sleep 5
done




#  后台执行方式: $