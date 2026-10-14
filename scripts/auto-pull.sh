#!/bin/bash
# 把本机主库快进到远端最新。只在工作区干净且能快进时拉取；不提交、不推送、不合并。
# 用法：scripts/auto-pull.sh（可由 launchd 等定时调用；日志写到标准输出）
set -u
HUB="$(cd "$(dirname "$0")/.." && pwd)"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

# 定时任务没有 shell 的代理变量；本机代理端口开着时临时补上
if [ -z "${HTTPS_PROXY:-}" ] && [ -n "${AUTO_PULL_PROXY:-}" ] && nc -z -G 1 "${AUTO_PULL_PROXY_HOST:-127.0.0.1}" "${AUTO_PULL_PROXY_PORT:-7897}" 2>/dev/null; then
  export HTTPS_PROXY="$AUTO_PULL_PROXY" HTTP_PROXY="$AUTO_PULL_PROXY"
fi

cd "$HUB" || exit 1
if [ -n "$(git status --porcelain)" ]; then
  echo "$(ts) 跳过：工作区有未提交修改"; exit 0
fi
git fetch -q origin || { echo "$(ts) 失败：fetch 出错（离线？）"; exit 1; }
LOCAL=$(git rev-parse @); REMOTE=$(git rev-parse '@{u}'); BASE=$(git merge-base @ '@{u}')
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "$(ts) 已是最新 $(git log --oneline -1)"
elif [ "$LOCAL" = "$BASE" ]; then
  git merge -q --ff-only '@{u}' && echo "$(ts) 已更新到 $(git log --oneline -1)"
elif [ "$REMOTE" = "$BASE" ]; then
  echo "$(ts) 跳过：本地有未推送提交"
else
  echo "$(ts) 跳过：本地与远端分叉，需要手动合并"
fi
