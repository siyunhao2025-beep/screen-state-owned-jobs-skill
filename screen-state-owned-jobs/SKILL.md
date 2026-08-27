---
name: screen-state-owned-jobs
description: Parse a user-uploaded resume into a source-grounded candidate profile, screen complementary job sources including the two configured Feishu tables, verify underspecified linked notices, preserve the fixed six-sheet Excel layout, and compare daily changes. Use for resume-based screening across enterprises, public institutions, education, health care, universities, talent-introduction programs, or other employer types; never use a hardcoded candidate profile.
---

# Screen Cloud Recruitment Jobs

## Required references

Read [references/profile-schema.md](references/profile-schema.md) before parsing a resume. Read [references/workbook-spec.md](references/workbook-spec.md) before screening jobs or generating the workbook. These files define stable interfaces; do not rename their fields.

## Runtime inputs

Preserve these public inputs for backward compatibility:

- `RESUME_FILE`: current user-uploaded resume path or attachment reference.
- `FEISHU_URL`: one recruitment table URL; retained for backward compatibility.
- `FEISHU_URLS`: one or more recruitment table URLs; when omitted, use both configured defaults.
- `SOURCE_MODE`: `两表互补` (default), `综合招聘表`, `分类编制表`, or `自定义`.
- `CATEGORY_SCOPE`: classified-table categories/views; default `自动选择`.
- `LINK_VERIFICATION_MODE`: `必要时逐链接核验` (default) or `仅表内信息`.
- `RUN_DATE`: `YYYY-MM-DD`.
- `PREVIOUS_RESULT`: previous structured result or workbook; optional on the first run.
- `DAILY_MODE`: boolean.
- `JOB_NATURE_SCOPE`: employer-nature filter; a string or list whose values must match the cloud table, default `全部`.
- `PREVIOUS_RESUME_PROFILE`: previously saved normalized profile; optional.
- `ALLOW_PROFILE_REUSE`: boolean, default `false`.
- `PROFILE_OVERRIDES`: user-supplied corrections such as target regions or a verified major-equivalence statement; optional.

Keep `FEISHU_URL` and workbook behavior backward compatible. Resolve defaults, aliases, and category routing from `references/workbook-spec.md`. Derive every candidate-specific value at runtime.

If the user does not choose a source mode, briefly explain the choices and use `两表互补`: the comprehensive table contributes broad employer coverage and its explicit written-exam field; the classified table contributes public-institution, talent-introduction, education, medical, university, and classified central/state-owned-enterprise coverage. Ask only when limiting scope or time would materially change the result.

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

## Multi-source and category policy

- Treat the configured Feishu tables as complementary sources, not substitutes.
- In `两表互补`, read both tables, retain source labels and URLs, and merge duplicates only after normalization.
- The classified table exposes `事业单位汇总`, `教育系统(小 初 高 职中)`, `医疗单位、医院招聘`, `高校(高校院所、高职大专)`, and `央国企招聘信息`. Visible subviews include talent-introduction views; the university category also includes `全国院校`, `本科院校`, `高职大专`, `人才引进`, and `行政/助理/工作人员等`.
- With `CATEGORY_SCOPE=自动选择`, map the resume and preferences to likely categories and inspect adjacent categories when roles can cross boundaries. Honor an explicitly limited category scope and record skipped categories.
- Include every employer type by default; do not infer a state-owned-only filter from the legacy technical skill name.
- Apply `JOB_NATURE_SCOPE` or a current-request employer preference after reading the table's actual nature values.
- Do not penalize or reject a private, foreign-funded, listed, or other company solely because it is not state-owned.
- When the user requests only one or more employer types, keep excluded records out of ranked sheets and state the active scope in the workbook.
- Preserve each table's raw employer-nature/category/view values. Use official sources only to verify or clarify them.

## Linked-notice verification

Do not reject or rank a record solely from an abbreviated title when it contains a notice, application, attachment, or official-site link. Open the link when the table does not clearly state any qualification that can change eligibility or priority: position identity, duties, employer/establishment nature, location, deadline, application status, degree, major, graduation cohort, age, political status, certificate, experience, written exam, or application method. Compare the linked requirements with resume evidence and current user overrides.

Use this evidence order for eligibility: official recruitment notice and attachments > official application portal > employer or government recruitment page > table summary. Preserve disagreements instead of silently overwriting them. The comprehensive table's explicit `/ = 无笔试` rule remains source-specific; do not apply it to a blank or absent field in the classified table. If a link is inaccessible, ambiguous, expired, or only an unofficial repost, mark affected fields `待确认`, retain the URL, and state what could not be verified. Never infer eligibility from a link title alone.

## Job screening workflow

Execute the existing workflow in order and preserve its interfaces:

1. Build the candidate profile from the current uploaded resume.
2. Resolve `SOURCE_MODE`, open the selected source(s), record each visible modification time, and enumerate selected categories/views.
3. Read selected employer types and categories, then apply `JOB_NATURE_SCOPE` only when requested. Preserve the comprehensive-table rule `/ = 无笔试` and `有笔试 = 有笔试`; use `待确认` when another source does not state the exam mode.
4. Derive employer nature, region, cohort, education, major, and role filters from `resume_profile.json` plus explicit current-request preferences.
5. Read each matching record into the stable job schema and provenance extension in `references/workbook-spec.md`.
6. Apply linked-notice verification to underspecified and current/high-ranked records. Match against the profile, cite resume evidence, and record checked URL, evidence tier, verification time, unresolved fields, and source conflicts.
7. Classify and rank jobs with the unchanged status and action-score logic.
8. Generate the unchanged six-sheet workbook.
9. Validate formulas, tables, formatting, links, and error cells.
10. Deduplicate and compare by normalized `company + role + location + cohort/batch`. Do not merge distinct locations, cohorts, batches, role codes, or materially different roles. For duplicates, retain every source and flag conflicts.

Official sources may verify whether a job remains open, its cohort, education, location, major eligibility, and enterprise type. They must not overwrite the Feishu written-exam field.

## Compatibility guarantees

- Keep all six worksheet names, order, headers, formulas, colors, widths, heights, freeze panes, and table names from `references/workbook-spec.md`.
- Keep the 26-field internal job record schema and add provenance as an optional extension object so earlier callers remain valid.
- Keep `strict_state_owned` for backward compatibility; set it from verified employer nature and never use it as a default exclusion rule.
- Replace only candidate-profile acquisition: hardcoded candidate fields become values derived from `resume_profile.json`.
- Populate `简历匹配口径` dynamically from profile categories while retaining its six columns and formatting.
- Keep `RESUME_FILE`, `FEISHU_URL`, `RUN_DATE`, `PREVIOUS_RESULT`, and `DAILY_MODE` compatible with earlier callers.
- Treat multi-source inputs as additive; a legacy one-URL call must still work.
- Add `JOB_NATURE_SCOPE` without changing earlier callers; omitted means `全部`.
- Prefer the current upload over any reusable profile.

## Final response

Return the generated workbook link, the saved profile JSON link when available, the active employer-nature scope, counts by employer nature, the priority-job table, and daily differences when `DAILY_MODE=true`. If execution stops for a resume problem, return only the actionable resume error and the required next step; do not emit a misleading job result.
