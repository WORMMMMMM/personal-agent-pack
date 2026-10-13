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

完成相关工作前，按维护技能检查是否有用户明确要求沉淀的变化；直接维护适用原件，避免只留在会话记忆里。推测不升级为事实。业务明细留在原系统。

Claude Code 通过根目录 CLAUDE.md 读取本文件；`.claude/skills/` 下是指向上表原件的技能入口，只含 name、description 和一行指引。Windows 台式机（DESKTOP-7F43U5M）的 `~/.claude/skills/` 另有一套同样的用户级入口，指向该机主库 `C:\Users\ziming\workspace\personal-agent-pack`，让任何目录的 Claude Code 会话都能用（2026-10-14 用户要求）。改技能名称或 description 时两处都同步；用户级入口不在 Git 里，只能在那台机器上改。

当前第一版为纯文件主库：没有安装器、生成副本或自动同步服务。跨设备通过 Git 获取同一份原件；不同设备路径、授权与会话可访问性需单独核实。保持结构简单，未经用户要求不重新引入适配框架。历史来源见 [SOURCES.md](SOURCES.md)。
