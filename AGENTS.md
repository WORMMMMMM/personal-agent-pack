# Personal Skill Hub project

## Purpose
User-owned profile, preferences, skill workflows and resource navigation with small Codex/Claude adapters. Do not import per-task business records or credentials. Do not create scheduler jobs as a side effect of installation.

## Sources and generated files
- profile/, preferences/, navigation/, skills/: canonical personal content.
- manifest.json: skill catalog, required capabilities and resource selectors.
- adapters/: connector guidance and plugin metadata.
- hub.py: standard-library manager; bounded global instructions, generated self-contained skills, install ledger and original-file backups.
- exports/ and user client folders: generated output, not canonical edits.

## Invariants
Preserve explicit user corrections and their scope. Do not promote suggestions into confirmed preferences. Keep resource IDs as routing hints and read live schemas and records before action. Reconcile sources before changing old rules. User-owned global settings outside the managed block must survive updates and uninstall. Modified managed files must block overwrite. No broad filesystem deletions.

## Verification
Run python3 -m unittest discover -s tests -v after manager changes. Validate generated skills and plugins when altering those formats. check verifies files only; do not describe it as proof of model behavior or service authentication. Document material limitations in VALIDATION.md.

## Current stage
v0.1 implements seven workflows extracted from the user's named pinned chats, four content areas, native adapters, updates, checks, backup/restore and plugin export. See VALIDATION.md for exact installation and test status. Keep this context updated after meaningful architecture changes.
