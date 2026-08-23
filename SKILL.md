---
name: screen-state-owned-jobs
description: Parse a user-uploaded resume into a source-grounded candidate profile, screen jobs of any employer type from the configured Feishu cloud recruitment table, preserve the fixed six-sheet Excel layout, and compare daily changes. Use when the user asks to screen or monitor cloud-table jobs from state-owned enterprises, public institutions, private companies, foreign-funded companies, listed companies, or other employers; prioritize no-written-exam roles; or regenerate the established job workbook. Supports PDF, DOCX, TXT, and Markdown resumes; never use a hardcoded candidate profile or assume a state-owned-only scope.
---

# Screen Cloud Recruitment Jobs

## Skill package

This repository root is the direct Skill installation directory.

Required runtime folders:

- `agents/`
- `assets/`
- `references/`
- `scripts/`

Use the current uploaded resume as the only candidate source. Never use hardcoded candidate information, previous candidates, filenames, or conversation memory as a resume profile.

Read:

- `references/profile-schema.md`
- `references/workbook-spec.md`

before parsing resumes or generating workbooks.

The Skill supports:

- PDF/DOCX/TXT/Markdown resume parsing
- dynamic candidate profile generation
- all employer types in recruitment tables
- no-written-exam priority screening
- fixed six-sheet Excel generation
- daily job change comparison

Resume source priority:

1. Current uploaded resume
2. Explicit current `RESUME_FILE`
3. Reusable profile only when explicitly allowed
4. Otherwise request a resume before screening
