# 个人主库入口

这是用户自己的个人信息、偏好、技能与项目导航。当前明确要求和宿主权限优先。

开始协作时读取 [个人信息](profile/about.md)、[个人偏好](preferences/core.md) 与 [团队与派单](TEAM.md)。涉及项目先查 [PROJECT_MAP.md](PROJECT_MAP.md)，再去原系统读最新状态。按需读取以下技能，不必一次加载全部。

| 场景 | 技能 |
|---|---|
| 日程与生活记录 | [schedule-and-diary](skills/schedule-and-diary/SKILL.md) |
| 目标跟踪 | [goal-progress-assistant](skills/goal-progress-assistant/SKILL.md) |
| 早报 | [fact-first-briefing](skills/fact-first-briefing/SKILL.md) |
| 每周回顾 | [weekly-review](skills/weekly-review/SKILL.md) |
| 文章输出 | [personal-article-writing](skills/personal-article-writing/SKILL.md) |
| 记住偏好、修改流程、更新项目入口 | [maintain-personal-hub](skills/maintain-personal-hub/SKILL.md) |

完成相关工作前，按维护技能检查是否有用户明确要求沉淀的变化；直接维护适用原件，避免只留在会话记忆里。用户明确陈述的个人事实和长期习惯写入主库，不只存进各 agent 自己的记忆（2026-10-14）。推测不升级为事实。业务明细留在原系统。

Claude Code 通过根目录 CLAUDE.md 读取本文件；`.claude/skills/` 下是指向上表原件的技能入口，只含 name、description 和一行指引。

用户要求技能完整安装在各个 agent 里，同时主库保持最新（2026-10-14）。原则：主库是唯一原件，只改主库；各 agent 的技能从主库单向获得，不在副本上改。
- 能读本机文件的 agent 直接用原件：MacBook Air 上 Claude Code 与 Codex 的用户级技能目录（`~/.claude/skills/`、`~/.codex/skills/`）是指向 `skills/` 各目录的软链接，Command Code 在其设置里直接登记了主库的 `skills/` 目录；DeepSeek Harness 的用户级技能目录 `~/.dsh/skills/` 也是指向 `skills/` 各目录的软链接，用户级记忆写在 `~/.dsh/AGENTS.md`（2026-10-27 建立）。Windows 台式机（DESKTOP-7F43U5M）的 `~/.claude/skills/` 是只含 name、description 和一行指引的入口，指向该机主库 `C:\Users\ziming\workspace\personal-agent-pack`，由 `scripts/sync-windows.ps1` 按主库原件生成并刷新；`~/.codex/skills/` 存放指向主库各技能目录的目录连接；该机只保留这一份克隆，Command Code 设置里的 `skills` 也指向它的 `skills/`（2026-10-14 合并掉了一份重复克隆）。这些都不在 Git 里，只能在对应机器上改。
- claude.ai 读不到本机文件，用 `scripts/build-claude-ai-skills.sh` 打包的副本（输出到不入库的 `exports/`），由用户在 claude.ai 上传；主库技能或共享文件变化后需重新打包上传。
- 主库更新：`scripts/auto-pull.sh`（macOS）与 `scripts/sync-windows.ps1`（Windows）都只在工作区干净且能快进时拉取，不提交不推送，可由本机定时任务调用。改动仍按维护技能提交并推送。
- Windows 台式机已注册计划任务 `PersonalAgentPack-Sync`：每 3 小时运行一次 `scripts/sync-windows.ps1`，除快进拉取外还会刷新 Claude Code 入口与 Codex 连接，日志在 `~/.commandcode/logs/hub-sync.log`（2026-10-17 建立）。

增删技能或改名称、description 时，同步 `.claude/skills/` 入口和各机器的用户级安装，并提醒用户重新上传 claude.ai 副本。不同设备路径、授权与会话可访问性需单独核实。保持结构简单，除上述脚本外不引入安装器或适配框架。历史来源见 [SOURCES.md](SOURCES.md)。
