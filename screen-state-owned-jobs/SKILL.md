---
name: screen-state-owned-jobs
description: Parse a user-uploaded resume into a source-grounded candidate profile, screen jobs of any employer type from the configured Feishu cloud recruitment table, preserve the fixed six-sheet Excel layout, and compare daily changes. Use when the user asks to screen or monitor cloud-table jobs from state-owned enterprises, public institutions, private companies, foreign-funded companies, listed companies, or other employers; prioritize no-written-exam roles; or regenerate the established job workbook. Supports PDF, DOCX, TXT, and Markdown resumes; never use a hardcoded candidate profile or assume a state-owned-only scope.
---

# Screen Cloud Recruitment Jobs

## Required references

Read [references/profile-schema.md](references/profile-schema.md) before parsing a resume. Read [references/workbook-spec.md](references/workbook-spec.md) before screening jobs or generating the workbook. These files define stable interfaces; do not rename their fields.

## Runtime inputs

Preserve these public inputs for backward compatibility:

- `RESUME_FILE`: current user-uploaded resume path or attachment reference.
- `FEISHU_URL`: recruitment table URL.
- `RUN_DATE`: `YYYY-MM-DD`.
- `PREVIOUS_RESULT`: previous structured result or workbook; optional on the first run.
- `DAILY_MODE`: boolean.
- `JOB_NATURE_SCOPE`: employer-nature filter; a string or list whose values must match the cloud table, default `全部`.
- `PREVIOUS_RESUME_PROFILE`: previously saved normalized profile; optional.
- `ALLOW_PROFILE_REUSE`: boolean, default `false`.
- `PROFILE_OVERRIDES`: user-supplied corrections such as target regions or a verified major-equivalence statement; optional.

Keep the original defaults for `FEISHU_URL` and workbook behavior from `references/workbook-spec.md`. Derive every candidate-specific value at runtime.

Interpret `JOB_NATURE_SCOPE=全部`, an empty value, or an omitted value as all employer types in the cloud table. Apply a narrower employer-nature filter only when the current user explicitly requests it. Examples include `央国企`, `事业单位`, `民企`, `外企`, and `上市公司`; preserve the exact values found in the cloud table rather than forcing these examples onto its schema.

## Resume source priority

Resolve the candidate data source in this strict order:

1. Use the resume attached to the current request.
2. Otherwise use an explicit `RESUME_FILE` supplied in the current request.
3. Otherwise reuse `PREVIOUS_RESUME_PROFILE` only when `ALLOW_PROFILE_REUSE=true` and its source hash and parse status are present.
4. Otherwise stop before job screening and ask the user to upload a PDF, DOCX, TXT, or Markdown resume.

Never use conversation memory, a bundled example, a previous candidate's details, a filename-derived identity, or hardcoded education, skills, projects, locations, graduation year, or professional preferences as a candidate profile.

If several resume-like uploads are present and the user did not identify one, ask which file to use. Do not merge several resumes automatically.

## Resume ingestion and storage

1. Resolve the selected upload to a readable local path.
2. Create a run directory outside the skill directory: `outputs/job-screening/{RUN_DATE}/resume/`.
3. Run:

   ```bash
   python3 scripts/parse_resume.py "$RESUME_FILE" \
     --output "outputs/job-screening/$RUN_DATE/resume/resume_parse.json" \
     --text-output "outputs/job-screening/$RUN_DATE/resume/resume_text.txt"
   ```

4. Inspect `status` in `resume_parse.json`:
   - `success`: continue.
   - `needs_ocr`: use the PDF/OCR capability if available, then rerun or construct the parsed-text input from the OCR result. If OCR is unavailable, ask for a text-searchable PDF or DOCX.
   - `error`: stop, report `error.code` and `error.message`, and request a supported, readable file.
5. Convert the extracted text into `resume_profile.json` using `references/profile-schema.md`.
6. Ground every normalized claim in an exact resume excerpt under `evidence_map`. Do not infer an unlisted degree, school, major equivalence, graduation year, skill, project, publication, award, location preference, or target role.
7. Apply `PROFILE_OVERRIDES` after parsing. Label every override with `source_type: user_override`; never alter `raw_text` or pretend an override came from the resume.
8. Run:

   ```bash
   python3 scripts/validate_profile.py \
     "outputs/job-screening/$RUN_DATE/resume/resume_profile.json"
   ```

9. Store the validated profile beside the workbook. When persistent file storage is available, save both the workbook and `resume_profile.json`; do not store the uploaded resume itself unless the user asks.

## Parse failure and missing-field policy

- Reject nonexistent, empty, password-protected, corrupted, or unsupported files with a specific error.
- Treat fewer than 80 non-whitespace extracted characters as `needs_ocr`; do not build a profile from them.
- If the name is absent, use `候选人` only in titles and filenames; do not guess a name.
- If graduation cohort, degree, major, target region, or major equivalence is absent, retain an empty/unknown value and mark the related job qualification `待确认`.
- Do not reuse a stale profile after the current upload fails.
- Do not continue job ranking when profile validation fails.

## Cloud-table scope policy

- Treat the configured Feishu cloud recruitment table as the primary job source.
- Include every employer type by default; do not infer a state-owned-only filter from the legacy technical skill name.
- Apply `JOB_NATURE_SCOPE` or a current-request employer preference after reading the table's actual nature values.
- Do not penalize or reject a private, foreign-funded, listed, or other company solely because it is not state-owned.
- When the user requests only one or more employer types, keep excluded records out of ranked sheets and state the active scope in the workbook.
- Preserve the cloud table's raw employer-nature value in each job record. Use official sources only to verify or clarify it.

## Job screening workflow

Execute the existing workflow in order and preserve its interfaces:

1. Build the candidate profile from the current uploaded resume.
2. Open the configured Feishu cloud recruitment table and record its latest modification time.
3. Read all employer types, then apply `JOB_NATURE_SCOPE` only when the user requested a narrower scope; preserve the rule `/ = 无笔试` and `有笔试 = 有笔试`.
4. Derive employer nature, region, cohort, education, major, and role filters from `resume_profile.json` plus explicit current-request preferences.
5. Read each matching record into the 26-field job schema in `references/workbook-spec.md`.
6. Match each job against the profile and cite resume evidence; never cite data absent from the profile.
7. Classify and rank jobs with the unchanged status and action-score logic.
8. Generate the unchanged six-sheet workbook.
9. Validate formulas, tables, formatting, links, and error cells.
10. In daily mode, compare by `company + role + location` and report additions, deadline changes, status changes, and link changes.

Official sources may verify whether a job remains open, its cohort, education, location, major eligibility, and enterprise type. They must not overwrite the Feishu written-exam field.

## Compatibility guarantees

- Keep all six worksheet names, order, headers, formulas, colors, widths, heights, freeze panes, and table names from `references/workbook-spec.md`.
- Keep the 26-field internal job record schema unchanged.
- Keep `strict_state_owned` for backward compatibility; set it from verified employer nature and never use it as a default exclusion rule.
- Replace only candidate-profile acquisition: hardcoded candidate fields become values derived from `resume_profile.json`.
- Populate `简历匹配口径` dynamically from profile categories while retaining its six columns and formatting.
- Keep `RESUME_FILE`, `FEISHU_URL`, `RUN_DATE`, `PREVIOUS_RESULT`, and `DAILY_MODE` compatible with earlier callers.
- Add `JOB_NATURE_SCOPE` without changing earlier callers; omitted means `全部`.
- Prefer the current upload over any reusable profile.

## Final response

Return the generated workbook link, the saved profile JSON link when available, the active employer-nature scope, counts by employer nature, the priority-job table, and daily differences when `DAILY_MODE=true`. If execution stops for a resume problem, return only the actionable resume error and the required next step; do not emit a misleading job result.
