# 个人 Skill Hub

我自己保存的一份个人主库，让不同 agent 了解我、按我的习惯工作，并知道最新资料去哪里找。

## 第一版只保留六部分

| 内容 | 位置 |
|---|---|
| 个人信息 | [profile/about.md](profile/about.md) |
| 偏好与 taste | [preferences/core.md](preferences/core.md)、[writing.md](preferences/writing.md) |
| 团队与派单 | [TEAM.md](TEAM.md) |
| 工作流技能 | [skills/](skills/)：日程与生活记录、目标跟踪、早报、每周回顾、文章输出 |
| 让 agent 维护主库的技能 | [maintain-personal-hub](skills/maintain-personal-hub/SKILL.md) |
| 项目与资料地图 | [PROJECT_MAP.md](PROJECT_MAP.md) |

[AGENTS.md](AGENTS.md) 是统一阅读入口，[SOURCES.md](SOURCES.md) 仅保留已有规则的出处。日记、任务进度、日程等明细继续留在原系统。

## 怎么用

在新设备登录 GitHub 后克隆私有仓库：

```sh
git clone https://github.com/WORMMMMMM/personal-agent-pack.git
```

告诉 agent：“读取这份主库的 AGENTS.md，按里面的个人信息、偏好和相关技能协作；有明确需要沉淀的变化时按维护技能更新主库。”也可以把这句话和本机主库的绝对路径放进该 agent 的常驻指令中。仅克隆仓库不会让所有 agent 自动读取它。

保持整个仓库在一起：技能直接引用主库中的偏好和 project map。本机 agent 把技能目录软链接到主库原件，不复制；读不到本机文件的 claude.ai 用 `scripts/build-claude-ai-skills.sh` 打包副本上传，主库变化后重新打包。各 agent 的安装方式见 [AGENTS.md](AGENTS.md)。Notion、日历等能力使用各设备已有连接；凭据不进库。

## 多设备协同

开始修改前检查 `git status`，工作区干净时运行 `git pull --ff-only`。修改后核对差异，只提交相关文件，再 `git push`；其他设备拉取即可读取新原件。有冲突先合并，不强推。`scripts/auto-pull.sh` 可由定时任务调用，只做安全的快进拉取，不自动提交或推送；不把业务记录搬进仓库。

可直接说：“记住这个偏好，更新主库并同步 GitHub。”维护技能负责把变化放到合适位置，而不是添加另一套管理系统。

旧版安装器与导出机制已经从当前版本移除，仍可从 Git 历史查看；现在只保留上面两个小脚本。以本仓库原件为准。
