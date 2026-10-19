# Project map

这里记录项目与工作领域的入口。最新进度、业务记录和详细上下文留在原处；开始工作前从入口读取。路径与会话 ID 是定位线索，不保证每台设备都能访问。

## 个人 Skill Hub

- 用途：维护个人信息、偏好、工作流与本地图。
- 主库：https://github.com/WORMMMMMM/personal-agent-pack （私有）
- 本地位置：当前克隆目录；不固定某台设备的绝对路径。
- 工作约定：[AGENTS.md](AGENTS.md)；维护方式：[维护技能](skills/maintain-personal-hub/SKILL.md)。

## 工作领域与资料入口

### AI 空间（SER8）

- 用途：AI 服务器与个人 NAS；AI 团队的常驻执行锚点（角色分工见 [TEAM.md](TEAM.md)）。
- 入口：实验室内的固定 IP 主机 SER8；实验室外经 WireGuard 接入内网后访问。
- NAS：`C:\Users\ziming\NAS`（SER8 个人工作空间内；SMB 共享名 `NAS`；Mac 挂载于 `/Volumes/NAS`，手机经 WireGuard 接入。2026-10-16 从 `C:\NAS` 迁入工作空间）。
- NAS 分区按用户在做的事情：`Robomaster`、`辅导员`、`学校课程`、`科研`、`生活`、`阅读`；课程资料在 `学校课程`、论文与书在 `阅读`，Mac 本地对应资料已于 2026-10-15 迁入。
- lookup: 部署与运行现状以主机实际状态为准，不在主库记录进度。
- 主机身份：本机 Windows 台式机（DESKTOP-7F43U5M）提供 SMB 共享 `NAS`（`C:\Users\ziming\NAS`），即 SER8 工作空间所在的那台常开主机（2026-10-18 核实）。

### GLM（TsingYun 中转站）

- 用途：给批量、重复、可并行的工程活与常驻任务提供便宜额度；对应 [TEAM.md](TEAM.md) 的中级工程师。
- service: OpenAI 兼容中转站，`https://39.96.77.156/v1`。联网即可直连，不绑定某台机器。
- models: `glm-5.2`、`glm-5.3`、`glm-5.3-flash`。三者都是推理模型，正文可能只出现在 `reasoning_content`；调用要给足 `max_tokens`，并同时读取 `content` 与 `reasoning_content`。
- 已接入: Windows/SER8 主机的 Command Code —— BYOK provider id `tsingyunglm`，定义在 `~/.commandcode/providers.json`；密钥存在 `~/.commandcode/auth.json` 的 `tsingyunglm.key`（0600），不进主库。
- lookup: 在 Command Code 里用 `/connect` 查看该 provider、用 `/model` 选用 `tsingyunglm/*`。切成 BYOK 模型后，会话内的压缩、子代理、标题生成也一并走它，不会回落到主计划额度。脚本或其他 agent 直接按 OpenAI 兼容调用：

  ```bash
  curl -s https://39.96.77.156/v1/chat/completions \
    -H "Authorization: Bearer $GLM_API_KEY" -H "Content-Type: application/json" \
    -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"..."}],"max_tokens":2048}'
  ```

- 派活（其他 agent 让 GLM 动手改文件、跑命令）：先切到任务目录，再无头启动 Command Code，`--local-only` 保证只走中转站、不耗 Command Code 额度：

  ```powershell
  commandcode --no-auto-update --local-only --skip-onboarding --trust --no-session -m tsingyunglm/glm-5.3-flash --yolo --max-turns 10 -p "<任务>"
  ```

  `-p` 无头模式默认扣下写文件与 shell 工具，不加 `--yolo` 只能读不能写（accept-edits 加 `--tools-all` 也不行）；`--no-auto-update` 防止调用时自行升级。yolo 下它可在当前目录随意读写执行，工作目录只给任务文件夹。Claude Code 侧在 `~/.claude/settings.json` 用一条匹配上述命令前缀（到 `-m tsingyunglm/` 为止）的 PowerShell allow 规则免确认（2026-10-18 用户确认采用 yolo）。
- caution: 第三方中转站，提示词与回复都经过它。辅导员资料里的学生个人信息、涉密科研数据不得经此发送。
- verified_on: 2026-10-18
- verification: `GET /v1/models` 返回上述三个模型；`POST /v1/chat/completions`（`glm-5.3-flash`）实测正常返回；Claude Code 经上述无头命令调起 `tsingyunglm/glm-5.3-flash`，在临时目录完成读文件、求和、写文件并回读核对（2026-10-18）。

### RoboMaster 哨兵导航

- 用途：TsingYun 战队哨兵的感知与导航。
- 仓库：https://github.com/TsingYun-RoboMaster/RM_Vision_Sentry
- local: Mac 上 `~/Robomaster/Navigation/`（RM_Vision_Sentry、仿真器、learning、maintenance 等）；战队其他资料在 `~/Robomaster/`。
- 硬件：Jetson Thor 与 NUC，在实验室内网（见 [个人信息](profile/about.md)）。
- lookup: 先读仓库内的 AGENTS.md／AI_CONTEXT.md 等上下文文件，以仓库和实机现状为准。

### 课程

- local: Mac 上 `~/School/<课程名>/`，每门课一个文件夹。
- lookup: 用户给出课程或文件夹时先读其中资料；作业要求以资料原文为准。

### 辅导员事务

- 用途：所带本科班级与学生事务。目录即事务分类：成绩与排名、学生信息（班级名单、摸排与搬家统计）、奖学金评选、发展对象、助学金谈话材料、全球胜任力涵评、心理危机重点案例汇报。
- local: 本机 `C:\Users\ziming\NAS\辅导员`（NAS 同步目录）。
- lookup: 用户问及某位同学、某个班级或辅导员相关事务时，先遍历该目录定位文件，读原文再作答；同一主题常同时有原始版与"已填写／整理"版，按文件名与日期取最新；答案要能指出依据的文件。
- tooling: xlsx 用 openpyxl、旧版 xls 用 xlrd、docx 用 python-docx、pdf 用 pypdf（本机 Python312 已装）。m4a 谈话录音本机无转写能力，需要时如实说明。
- freshness: 以目录内文件实际内容为准；学生个人信息不回写到主库。
- verified_on: 2026-10-16
- verification: 已列出目录树（深度 3）；成功读取 `学生信息\无45班级名单_待定.xlsx`（31 人、10 字段），确认可读。

### 视频 → 文字稿 → 报告

- 用途：给一个视频链接（B 站、YouTube 等 yt-dlp 支持的站点），产出带时间戳文字稿，再据此写报告。
- local: `C:\Users\ziming\workspace\video-pipeline`（SER8 本机）。
- 用法: `powershell -ExecutionPolicy Bypass -File pipe.ps1 -Url "<链接>"`；术语密集内容加 `-Model medium`；无视平台字幕强制转写加 `-ForceAsr`。
- 产物: `jobs\<BV号>[_p分P]\` 下的 `metadata.info.json`、`audio.wav`、`transcript.srt`、`transcript.timed.txt`、`transcript.json`、`report.md`。
- 策略: 平台中文字幕优先（不占 CPU）；没有字幕才下载音频并本地转写。
- tooling: yt-dlp（Python 模块）、ffmpeg（WinGet 包目录，不在 PATH）、faster-whisper 1.2.1 + PyAV 18（**PyAV 19 会报 `metadata_errors` 错，需 `<19`**）；模型走 `HF_ENDPOINT=https://hf-mirror.com`，CPU int8。
- 报告: 按 `report_template.md` 的九段结构写，逐条附时间戳；只在幻灯片里的图表/代码需要按时间抽帧另看。
- verified_on: 2026-10-19
- verification: `BV1i88A65E7r`（25:08）实测跑通：下载音频 → 16k 单声道 wav → 转写 395 段，RTF 0.149（225 秒）。同一音频换 `medium`：432 段、RTF 0.448（676 秒），「哨兵 / Mid-360 / 仿真」等同音错误消失，但专业术语（闭式求解、麦轮）仍会错；术语密集的内容可再给 `asr.py --initial-prompt` 塞领域词表。产出 SRT/时间戳文本/JSON，并生成 `report.md`。

### 阅读

- local: Mac 上 `~/Readings`（论文、书籍与批注整理）；阅读笔记见下方 My readings。

### 发票与报销

- local: Mac 上 `~/发票`。
- lookup: 按 [个人偏好](preferences/core.md) 的报销规则整理；明细不进主库。

### calendar

- service: Google Calendar（主日历，唯一真相源；2026-10-13 起）
- calendar_id: zzm3312@outlook.com
- timezone: Asia/Shanghai
- access: 当前环境有 Google Calendar 连接器就用连接器（如 claude.ai，用户本人账户授权）；没有就用服务账号 calendar-bot@my-calendar-509705.iam.gserviceaccount.com，已被授予该日历“更改活动”权限，密钥在各设备 `~/.config/gcal-service-account.json`。两者都没有时如实说明尚未读写。
- tooling: 服务账号方式用各设备的 my-calendar 技能 `scripts/gcal.py`（list / add / delete / free；默认走 127.0.0.1:7897 代理）。该脚本不在主库，只有没有连接器的设备需要。
- lookup: 用当前可用的方式按绝对日期查询与写入；写入前先查冲突，写入后回读核对。
- freshness: 以日历实时内容为准；旧会话只帮助消歧，不能证明事件仍存在。
- sync: 写入后自动同步到手机系统日历与 Notion Calendar（用户侧已连接同一账户）。
- retired: 旧 Notion「日程」库（database_id 8ee00760-8cab-4ee3-afba-39d5ad76725b）同日退役，勿再写入。
- verified_on: 2026-10-13
- verification: 服务账号在 Mac 与 SER8 两端完成读写实测（测试条目写入 + 回读）；claude.ai 连接器 2026-10-14 只读核实主日历与时区，尚未做写入实测。

### Diary

- service: Notion
- title: Diary
- url: https://www.notion.so/7045a496edab4b9b896586b6aff25a53
- data_source: collection://34a17deb-ccf7-4166-a1c1-b95246357d1a
- action_view: view://3701d33e-29f7-817a-ae1f-000c1f8f6563
- fields: title: 标题；datetime: 时间；date: 日期；type: 类型；original: 原文
- lookup: 读取 schema，按行动发生日期查询；读取原文和起止时间查重、校正。
- freshness: 以 Notion 实时记录和视图过滤为准；导航只保存定位信息。
- verified_on: 2026-10-09
- verification: 本会话成功读取数据源 schema；未读取或复制日记条目。
- source_thread: 019e7913-0c15-7082-8813-681ebd27d93e

### 目标和工作计划

- service: Notion
- title: 目标和工作计划
- url: https://app.notion.com/p/1f21d33e29f780f5ae6dfeef083cf174
- data_source: collection://1f21d33e-29f7-801c-98a3-000b951aed27
- lookup: 读取当前 schema，查询目标状态和目标页，再找相应子页面、每日记录及提醒约定。
- freshness: 活跃目标、目标数值、周期起点和提醒资格均从目标页读取；不在 Hub 固定。
- verified_on: 2026-10-09
- verification: 本会话成功读取数据源 schema。
- source_thread: 019e9d92-b463-7eb3-b29e-195acdc0507a

### 减脂每日记录

- service: Notion
- title: 减脂每日记录
- data_source: collection://6780d0cf-4f44-4204-9d8f-78e8cb218cac
- lookup: 从当前目标页核实子数据库关联，按当地日期查询；一个目标一天一条结构化记录。
- freshness: 此位置来自现有技能，运行时重新核实。当前体重、目标值和饮食周期不复制进 Hub。

### 思维场

- service: Notion
- title: 思维场
- url: https://app.notion.com/p/15cc3a98bd1a4c9d93d37127ff308a05
- lookup: 先读取页面原文，再讨论其中的认知点、思维链、信任边界和现实锚点。
- freshness: 以页面最新内容为准；区分用户模型、外部理论与助手建议。
- verified_on: 2026-10-09
- verification: 成功读取页面；正文仍在 Notion。
- source_thread: 019fd6b7-4d63-7ef1-b5f3-612293aa522c

### My readings

- service: Notion
- title: My readings
- data_source: collection://1dd1d33e-29f7-80b4-9078-000bc143de98
- lookup: 按论文或主题查询现有阅读笔记；保留作者摘录与用户批注的来源。
- verified_on: 2026-10-09
- verification: 成功读取数据源 schema。

### 文章输出

- source_thread: 01a08b48-481b-7d91-858e-59d23efe5365
- title: 文章输出
- lookup: 优先用本次提供的原文、论文和批注；历史文章按会话或本地路径检索，仅在相关时读取。
- local_readings: /Volumes/NAS/阅读（SER8 NAS，Mac 经 SMB 挂载；原 ~/Readings 已迁入）
- freshness: 当前任务的资料优先，旧文不作为新论文事实证据。

### 早报

- source_thread: 019ffe20-06b3-7713-b445-5b09f664db15
- title: 早报
- scheduler: Claude Code 定时任务「每日早报」https://claude.ai/code/routines/trig_015TtYfBYzcHZvpD8uUQsprR ，每天北京时间 06:00（含周六），只跑每日简报分支；Claude Code 定时任务「每周深读」https://claude.ai/code/routines/trig_01WzcV6oCZPsqdoFvujFNcye ，每周六北京时间 12:00，只跑每周深读分支。结果都在当次会话里并推送手机（2026-10-14 起；Codex automation-2 已由用户停用）。
- lookup: 用网络一手来源核实新闻；每个分支按周期只触发一次，不需查找往期去重。
- freshness: 调度时间以 routine 页面为准，修改时同步本条。

### 每周回顾

- source_thread: 019fff53-320a-75e2-aa55-132bff7dfc8c
- title: 每周回顾
- scheduler: Claude Code 定时任务「每周回顾」https://claude.ai/code/routines/trig_01UYtkwK8LGvMFqoYbzGpvhv ，每周五北京时间 21:00，只读不写，结果在当次会话里（2026-10-14 起；Codex automation 已由用户停用，不再做周六兜底）。
- lookup: 读当前 Notion 目标、本周 Diary 与日历；读不到的会话来源在结果中说明。
- freshness: 按自然周；配置变更、讨论或失败运行不算完成回顾。

### daily_review

- scheduler: Claude Code 定时任务「每晚回顾」https://claude.ai/code/routines/trig_01Dhnv9iKwT9Nir1tsZ47pmr ，每天北京时间 23:00，按 schedule-and-diary 第三节执行，结果在当次会话里，补充直接回复该会话（2026-10-14 起；Codex automation-3 已由用户停用）。
- context_reference: ~/Documents/Dariy/AI_CONTEXT.md
- lookup: 日历预约为输入，Notion Diary 为输出；按所回顾日期读取当天事件与现有记录。
- freshness: 被明确要求回顾或上述定时任务触发时才执行。

## 添加项目

发现用户明确的新项目，或已知项目入口发生变化时，补充：项目名称、用途、仓库或页面入口、最新状态／上下文文件位置。只写已经核实的内容；不要从旧会话推断项目仍活跃，也不要复制任务日志。
