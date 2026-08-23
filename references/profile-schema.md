# Dynamic resume profile schema

## Contents

1. Source contract
2. Normalized profile schema
3. Extraction rules
4. Error states
5. Storage contract

## 1. Source contract

Accept one current resume in PDF, DOCX, TXT, or Markdown format. The parser writes `resume_parse.json` and `resume_text.txt`. Treat the parse JSON as the only resume text source for semantic normalization.

`resume_parse.json` contains the parsed resume metadata, extracted text, statistics, warnings and errors.

## 2. Normalized profile schema

Write `resume_profile.json` using the schema defined in the original skill package. Preserve all fields including education, certified major, skills, projects, work experience, target preferences, evidence_map and quality.

Every normalized claim must include exact resume evidence or a clearly marked user override.

## 3. Extraction rules

1. Preserve facts, dates, scores, software names, publication status, authorship, award level, and units exactly.
2. Do not convert a research direction into a formal degree major.
3. Leave fields empty when information is absent.
4. Never insert previous candidate information or inferred identity.

## 4. Error states

Missing files, unsupported formats, unreadable documents and invalid profiles must stop screening with an actionable error.

## 5. Storage contract

Store parsed resume files under `outputs/job-screening/{RUN_DATE}/resume/` and preserve source hashes for reproducibility.
