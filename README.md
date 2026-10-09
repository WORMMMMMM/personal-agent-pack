# 我的个人 Skill Hub

这是你自己保存的个人配置主库。它包含个人信息、个人偏好、七个工作流及资料导航，配有接入、更新、检查和导出工具。

日记、日程、目标进度、早报正文和每周总结继续保存在原系统。这里保存“我是谁、怎样与我协作、事情怎样做、最新记录去哪里查”。

## 从这里开始

在 macOS 上双击 **管理.command**，可以检查接入状态、同步修改、导出插件包和查看工作流。需要 Python 3.9 或以上；无需安装 Python 第三方库。也可以让当前 agent 使用下述命令管理。

| 你想调整什么 | 修改原件 |
|---|---|
| 身份与背景 | [profile/about.md](profile/about.md) |
| 交流、协作习惯 | [preferences/core.md](preferences/core.md) |
| 写作和配图风格 | [preferences/writing.md](preferences/writing.md) |
| 工作流程 | skills/ 中对应的 SKILL.md 与 references |
| Notion、日历、会话与项目入口 | [navigation/resources.json](navigation/resources.json) |
| 某条约定从哪里来 | [navigation/provenance.md](navigation/provenance.md) |

例如告诉已接入的 agent：“把这个写作习惯更新到我的个人 Skill Hub，并同步。”它应该修改原件、验证，再更新已接入客户端。用户没有要求时，不自动把观察或猜测保存为个人事实。

## 七个工作流

| 会话来源 | 技能 | 核心行为 |
|---|---|---|
| 生活记录 | notion-diary-capture | 感想原文、行动发生时间、日历回顾、查重与核验 |
| 目标跟踪 | goal-progress-assistant | 忠实进度、每日指标合并、目标状态与提醒 |
| 日程预约 | google-calendar-natural-language-scheduling | 北京时间、增量修改、提醒与循环范围 |
| 思维场 | thinking-field | 先读最新原文，通俗比较理论、讨论理解 |
| 早报 | fact-first-briefing | 事实优先、绝对窗口、去重、国际机制解释 |
| 每周回顾 | weekly-review | 目标推进为重点，覆盖其他实质交互 |
| 文章输出 | personal-article-writing | 第一人称理解过程、平实引导、少字配图 |

这些是从指定会话和既有技能提炼的流程，不包含完整历史。思维场中的新整理方法已标为建议；个人身份来自历史陈述，不能当作实时身份核验。

## 接入、更新与检查

在本目录运行：

```sh
python3 hub.py validate
python3 hub.py install codex --dry-run
python3 hub.py install claude --dry-run
python3 hub.py install codex
python3 hub.py install claude
python3 hub.py check codex
python3 hub.py check claude
```

已有同名技能时，先检查预览。确认迁移后使用 `install codex --adopt-existing`，工具会备份原文件再接管。`--adopt-existing` 仅用于首次接管，不会强制覆盖已经接管后的本地修改。

修改原件后的更新：

```sh
python3 hub.py validate
python3 hub.py update codex
python3 hub.py update claude
```

- Codex：在用户级 AGENTS.md 中写入有边界标记的个人配置；新用户使用 ~/.agents/skills。检测到现有同名旧版技能时沿用 ~/.codex/skills，避免重复安装。
- Claude Code：使用用户级 CLAUDE.md 和 ~/.claude/skills。
- 常用信息和核心偏好进入常驻入口；七个技能及它们各自所需导航按需读取。
- 全局入口之外的已有文字保留；更新遇到副本改动会停止并指出文件。将有效修改合并回主库后处理冲突，不盲目覆盖。
- 安装历史与备份位于目标用户目录的 .agentpack/。这是接入工具自己的状态，不是业务记录库。
- 新会话读取新入口。当前对话不保证热更新；如目标客户端仍展示旧技能，重新启动客户端。
- 更换机器时复制整个主库并执行 install；同机移动主库后从新位置执行 update，入口会更新。导航中的本机路径仍需要在新机器核实。

撤销某个客户端的接入：

```sh
python3 hub.py uninstall claude --dry-run
python3 hub.py uninstall claude
```

撤销会恢复最初接管的旧技能，删除本工具新建且仍未被改动的文件，保留其他配置与备份。更新和撤销均拒绝覆盖未合并的本地改动。常规写入失败时回滚本次修改。

## 连接入口

接入个人规则与接通业务工具是两件需要分别检查的事：

| 工作流 | 所需连接 |
|---|---|
| 生活记录、目标跟踪 | Notion；涉及日程或提醒时还需 Google Calendar |
| 日程预约 | Google Calendar |
| 思维场 | Notion；查外部理论时还需网页检索 |
| 早报 | 网页检索与读取；查原有完成结果时需要对应历史入口 |
| 每周回顾 | Notion、相关会话或可读取的项目记录 |
| 文章输出 | 当前材料；使用在线笔记时需要 Notion |

连接器／MCP 由各 agent 配置和授权，工具不会复制凭据。`check` 只核对接入文件与内容版本，明确返回 connections: not_probed。在新 agent 中可说：“只读检查这个 Hub 所需的 Notion 和日历入口能否访问，报告缺失能力，不创建记录。”

保留现有定时任务的原调度器；装到第二个 agent 不会再建一套定时任务。早报时间在历史用户陈述与当前调度提示间有差异，主库只保留调度位置，不据旧记录改时间。

## 可携带插件包

```sh
python3 hub.py export
```

生成 exports/personal-agent-pack，包含 Codex 与 Claude 兼容清单、七个自包含技能及资料。该导出方式不注册插件市场；正式插件安装需要按目标平台完成。技能插件本身不会把个人偏好变成常驻指令，因此本机完整接入优先使用 install。避免同时用两种方式安装同一套技能。

原件永远在本目录四部分中，exports 与客户端技能目录是生成副本。更新只需维护原件。

## 多设备协同

私有主库：https://github.com/WORMMMMMM/personal-agent-pack

新设备先登录自己的 GitHub 账户，然后克隆并接入需要的客户端（macOS/Linux，Python 3.9+）：

```sh
git clone https://github.com/WORMMMMMM/personal-agent-pack.git
cd personal-agent-pack
python3 hub.py validate
python3 hub.py install codex
# 使用 Claude Code 的设备再运行：
python3 hub.py install claude
```

已有同名技能时先预览差异，再按前述迁移流程处理。每台设备独立配置 Notion、Calendar 等账号授权；源会话、自动化与本机路径不保证在其他设备可访问，需要核实或调整导航。

每次修改主库前先检查工作区，再拉取：

```sh
git status --short
git pull --ff-only
```

有未提交修改时先保存、提交并核对差异；遇到分叉或冲突先合并，禁止强制覆盖远端。编辑原件后：

```sh
python3 hub.py validate
# 对本机已接入的客户端分别执行：
python3 hub.py update codex
# python3 hub.py update claude
git add profile preferences navigation skills manifest.json adapters
git diff --cached
git commit -m "Update personal preferences and workflows"
git push
```

如果改动了管理工具或文档，也应检查并提交对应文件；工具改动需先运行测试。在其他设备执行 `git pull --ff-only` 后，运行 `validate` 和已接入客户端的 `update` 才完成应用。GitHub 同步源文件，不自动刷新各设备的配置，也不会后台自动推送。建议一次只在一台设备编辑同一份偏好或技能，切换前推送。

只同步主库；客户端安装状态、原文件备份和凭据留在设备本地。不要把整个 ~/.codex、~/.claude 或 ~/.agentpack 放进仓库。便携 ZIP 是导出快照；多设备长期协同使用 Git 克隆目录。

## 版本与验证

主库使用 Git 保存版本，并由用户授权发布到 GitHub 私有仓库；日常修改不会自动推送。内容摘要会标识当前实际版本，即使尚未更改发布版本号，也能发现待同步修改。日常同步不会自动提交你的编辑，可让 agent 在审核修改后保存一次本地版本。

```sh
python3 -m unittest discover -s tests -v
```

测试覆盖安装／重复安装／更新／撤销、旧文件接管、外部配置保留、本地改动阻止覆盖、写入失败回滚、主库移动、符号链接与重复目录冲突，以及独立导出。具体本机验证结果见 [VALIDATION.md](VALIDATION.md)。

第一版在 macOS 上实现与测试；Linux 路径兼容，未做本机实测。Windows 需要另做文件锁与路径适配。对不能读取本地文件或安装技能的聊天产品，需按其开放能力单独适配。

实现依据：[Codex skills](https://learn.chatgpt.com/docs/build-skills)、[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Claude Code skills](https://code.claude.com/docs/en/skills)、[Claude Code memory](https://code.claude.com/docs/en/memory)、[插件打包](https://developers.openai.com/plugins/build/plugins)。
