#!/bin/bash
# 为 claude.ai 等读不到本机主库的 agent 打包技能副本：exports/claude-ai/<技能名>.zip
# 每个包含技能原件，以及技能引用的主库共享文件快照（放在 hub/ 下，链接改指向它）。
# 副本不会自动更新：主库变化后重新运行本脚本并重新上传。
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HUB/exports/claude-ai"
REV="$(git -C "$HUB" log -1 --format='%h %cs')"
DIRTY=""; [ -n "$(git -C "$HUB" status --porcelain)" ] && DIRTY="（含未提交修改）"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
rm -rf "$OUT"; mkdir -p "$OUT"

for SKILL in "$HUB"/skills/*/; do
  N="$(basename "$SKILL")"
  D="$WORK/$N"
  cp -R "$SKILL" "$D"
  mkdir -p "$D/hub"
  cp "$HUB"/{AGENTS.md,PROJECT_MAP.md,TEAM.md,SOURCES.md} "$D/hub/"
  cp -R "$HUB/profile" "$HUB/preferences" "$D/hub/"
  # 主库相对链接改指向包内快照
  sed -i.bak 's#](\.\./\.\./#](hub/#g' "$D/SKILL.md"
  [ -d "$D/references" ] && find "$D/references" -name '*.md' -exec sed -i.bak 's#](\.\./\.\./\.\./#](../hub/#g' {} +
  find "$D" -name '*.bak' -delete
  # frontmatter 之后插入副本说明
  NOTE="> 本技能是个人主库（GitHub WORMMMMMM/personal-agent-pack）在 $REV$DIRTY 的副本，供读不到主库的环境使用；hub/ 是主库共享文件的同时快照，先读 hub/AGENTS.md。需要沉淀的变化直接改主库：能接入该 GitHub 仓库就修改、提交、推送并重新打包；接不到时才把具体改动交给用户。"
  awk -v note="$NOTE" 'NR>1 && !done && /^---$/ {print; print ""; print note; done=1; next} {print}' "$D/SKILL.md" > "$D/SKILL.md.tmp" && mv "$D/SKILL.md.tmp" "$D/SKILL.md"
  (cd "$WORK" && zip -qr -X "$OUT/$N.zip" "$N" -x '*.DS_Store')
  echo "$OUT/$N.zip"
done
