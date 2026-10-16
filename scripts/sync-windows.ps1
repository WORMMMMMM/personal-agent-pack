# 把本机主库快进到远端最新，并让本机各 agent 的技能入口与主库保持一致。
# 只做安全操作：工作区干净且能快进时才拉取，不提交、不推送、不合并分叉。
# 由 Windows 计划任务定时调用，也可手动运行：
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sync-windows.ps1

param(
  [string]$Hub = "C:\Users\ziming\workspace\personal-agent-pack",
  [string]$ClaudeSkills = (Join-Path $env:USERPROFILE ".claude\skills"),
  [string]$CodexSkills  = (Join-Path $env:USERPROFILE ".codex\skills"),
  [string]$LogFile = (Join-Path $env:USERPROFILE ".commandcode\logs\hub-sync.log")
)

$ErrorActionPreference = "Continue"
$marker = "本文件由 scripts/sync-windows.ps1 生成"
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Log($m) {
  $line = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
  Write-Output $line
  try {
    $dir = Split-Path -Parent $LogFile
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
  } catch { }
}

function Read-Frontmatter([string]$path) {
  $lines = [System.IO.File]::ReadAllLines($path, [System.Text.Encoding]::UTF8)
  $name = ""; $desc = ""; $inFm = $false
  foreach ($l in $lines) {
    if ($l.Trim() -eq "---") {
      if ($inFm) { break } else { $inFm = $true; continue }
    }
    if ($inFm) {
      if ($l -match '^name:\s*(.+)$') { $name = $Matches[1].Trim() }
      elseif ($l -match '^description:\s*(.+)$') { $desc = $Matches[1].Trim() }
    }
  }
  return @{ name = $name; description = $desc }
}

$git = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $git) { $git = "C:\Program Files\Git\cmd\git.exe" }
if (-not (Test-Path $git)) { Log "错误：找不到 git，退出"; exit 1 }
if (-not (Test-Path (Join-Path $Hub ".git"))) { Log "错误：$Hub 不是主库克隆，退出"; exit 1 }

# 1. 快进拉取主库
Push-Location $Hub
if (& $git status --porcelain) {
  Log "跳过拉取：工作区有未提交修改"
} else {
  & $git fetch -q origin 2>$null
  $local  = (& $git rev-parse HEAD).Trim()
  $remote = (& $git rev-parse "@{u}").Trim()
  $base   = (& $git merge-base HEAD "@{u}").Trim()
  if ($local -eq $remote)     { Log "主库已是最新 " + $local.Substring(0,7) }
  elseif ($local -eq $base)   { & $git merge -q --ff-only "@{u}" 2>$null; Log ("主库已更新到 " + (& $git log --oneline -1)) }
  else                        { Log "跳过拉取：本地与远端分叉或有未推送提交" }
}
Pop-Location

# 2. 主库当前技能清单
$skills = @()
$skillsDir = Join-Path $Hub "skills"
if (Test-Path $skillsDir) {
  $skills = Get-ChildItem $skillsDir -Directory -ErrorAction SilentlyContinue |
            Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }
}
$hubNames = @($skills | ForEach-Object { $_.Name })
Log ("主库技能 " + $hubNames.Count + " 个：" + ($hubNames -join ", "))

# 3. Claude Code 入口（只含 name、description 和一行指引）
$claudeChanged = 0
foreach ($s in $skills) {
  $fm = Read-Frontmatter (Join-Path $s.FullName "SKILL.md")
  $skillName = if ($fm.name) { $fm.name } else { $s.Name }
  $dir = Join-Path $ClaudeSkills $s.Name
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $target = Join-Path $dir "SKILL.md"
  $old = if (Test-Path $target) { [System.IO.File]::ReadAllText($target, [System.Text.Encoding]::UTF8) } else { "" }
  $body = @"
---
name: $skillName
description: $($fm.description)
---

$marker。本文件是本机 Claude Code 的用户级技能入口，规则以个人主库原件为准。主库在本机 ``$Hub``：先读主库根目录的 AGENTS.md，再读取并遵循 ``skills\$($s.Name)\SKILL.md``（其中的相对链接按原件位置解析）。主库不存在或读不到时如实说明，不凭本入口的简介执行。
"@
  if ($old -ne $body) {
    [System.IO.File]::WriteAllText($target, $body, $utf8)
    $claudeChanged++
  }
}
# 清理主库里已不存在的入口（只动本脚本生成的）
foreach ($d in Get-ChildItem $ClaudeSkills -Directory -ErrorAction SilentlyContinue) {
  if ($hubNames -contains $d.Name) { continue }
  if ($d.LinkType) { continue }
  $f = Join-Path $d.FullName "SKILL.md"
  if ((Test-Path $f) -and ([System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8) -like "*$marker*")) {
    Remove-Item -LiteralPath $d.FullName -Recurse -Force
    Log ("移除已失效的 Claude 入口：" + $d.Name)
  }
}
Log ("Claude Code 入口已刷新，更新 " + $claudeChanged + " 个")

# 4. Codex 技能（指向主库原件的目录连接）
if (Test-Path $CodexSkills) {
  $codexChanged = 0
  foreach ($s in $skills) {
    $link = Join-Path $CodexSkills $s.Name
    if (Test-Path $link) { continue }
    New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null
    $codexChanged++
  }
  foreach ($d in Get-ChildItem $CodexSkills -Directory -Force -ErrorAction SilentlyContinue) {
    if (-not $d.LinkType) { continue }
    if ($hubNames -contains $d.Name) { continue }
    $t = @($d.Target) -join ";"
    if ($t -like "*$Hub*") { Remove-Item -LiteralPath $d.FullName -Force -Recurse; Log ("移除已失效的 Codex 连接：" + $d.Name) }
  }
  Log ("Codex 技能连接已同步，新增 " + $codexChanged + " 个")
}

Log "完成"
