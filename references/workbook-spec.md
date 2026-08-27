# State-owned job workbook specification

## Contents

1. Stable inputs
2. Internal job schema
3. Filtering and ranking
4. Workbook structure
5. Formatting and validation
6. Daily comparison

## 1. Stable inputs

- `RESUME_FILE`: runtime upload; never a bundled or hardcoded profile.
- `FEISHU_URL`: legacy single-source input; default comprehensive table `https://yal2at57cvq.feishu.cn/base/GtSLbyyR3aCENOsJYC6cdlsVnih?table=tblH4au5rnBcqHgJ&view=vewFBnAr4c`.
- `FEISHU_URLS`: multi-source input; default is the comprehensive table above plus classified table `https://my.feishu.cn/base/NJo6biJTEajs6qs8cE3cxWt7nge?table=tblXkeBqqjqJSZaR&view=vew6Yd463E`.
- `SOURCE_MODE`: default `两表互补`; alternatives are `综合招聘表`, `分类编制表`, and `自定义`.
- `CATEGORY_SCOPE`: default `自动选择`; accepts classified-table category/view names.
- `LINK_VERIFICATION_MODE`: default `必要时逐链接核验`.
- `RUN_DATE`: `YYYY-MM-DD`.
- `PREVIOUS_RESULT`: optional on first run.
- `DAILY_MODE`: boolean.
- `JOB_NATURE_SCOPE`: string or list, default `全部`; omitted or empty means all employer types in the cloud table.

Map dynamic profile values to the earlier interface as follows:

- `CANDIDATE_NAME = resume_profile.candidate.name || "候选人"`
- `GRADUATION_COHORT = resume_profile.graduation_cohort`
- `DEGREE` and `ORIGINAL_MAJOR` come from the most recent relevant education item.
- `CERTIFIED_MAJOR = resume_profile.certified_major.value`; leave empty when unsupported.
- `TARGET_REGIONS`, `TARGET_CITIES`, and `TARGET_KEYWORDS` come from `target_preferences` plus demonstrated profile evidence.
- `ACTIVE_JOB_NATURE_SCOPE` comes from the current request; default to `全部`, not `央国企`.
- `NO_EXAM_RAW_VALUE = "/"`.
- `WRITTEN_EXAM_RAW_VALUE = "有笔试"`.

## 2. Internal job schema

Keep these 26 fields unchanged:

1. `record_id`
2. `company`
3. `nature`
4. `industry`
5. `location`
6. `role`
7. `major`
8. `deadline`
9. `cohort`
10. `batch`
11. `education`
12. `source`
13. `notice_url`
14. `apply_url`
15. `exam`
16. `notes`
17. `target_roles`
18. `match_score`
19. `tier`
20. `verified_status`
21. `status_note`
22. `can_apply_now`
23. `exam_verified`
24. `resume_evidence`
25. `strict_state_owned`
26. `official_or_verify_url`

`exam` may be `/`, `有笔试`, or `待确认`. Display `/` as `无笔试（综合表“/”）`. Use `待确认` only when the selected source and linked official material do not state the exam mode; never reinterpret a blank as no exam.

Store optional provenance beside the stable 26 fields: `source_name`, `source_url`, `source_category`, `source_view`, `source_record_id`, `checked_url`, `checked_at`, `evidence_tier`, `unresolved_fields`, and `source_conflicts`. A merged duplicate may use lists so no source is lost.

Use only these statuses: `在招`, `待确认`, `条件性`, `属性待核验`, `已截止`, `届次不符`, `不推荐/待核验`, `范围外`.

Use only these tiers: `S`, `A`, `B`, `C`, with boundaries `S=90–100`, `A=85–89`, `B=70–84`, `C=0–69`.

## 3. Filtering and ranking

1. Read every employer type from the cloud table. When `JOB_NATURE_SCOPE` is `全部`, empty, or omitted, retain all types; otherwise retain only exact requested nature values and label excluded records `范围外` when they must remain in audit data.
2. Derive employer-nature scope, target regions, cities, cohort, degree, major, and role keywords from the dynamic profile and current user preferences.
3. Retain nationwide records but mark that the exact technical-role city requires confirmation.
4. Deduplicate by normalized `company + role + location + cohort/batch`; do not merge different role codes, substantive roles, locations, cohorts, or batches. Retain all provenance and conflicts for merged duplicates.
5. Define `no_exam` as `exam === '/'`, `with_exam` as `exam === '有笔试'`, and `exam_unknown` as `exam === '待确认'`. Keep `exam_unknown` out of no-exam sheets and place it after confirmed written-exam rows in `有笔试备选`, clearly labeled `笔试待确认`.
6. Define `no_exam_priority` as no-exam records within the active employer-nature scope, with status in `在招`, `待确认`, or `条件性`, matching dynamic region/cohort requirements, and `match_score >= 65`.
7. Define `no_exam_closed` as no-exam records whose status is outside `在招`, `待确认`, and `条件性`.
8. Compute `action_score = match_score + status_bonus + region_bonus + cohort_bonus`, where `在招=10`, `待确认=4`, other status `=0`, region match `=5`, and cohort match `=4`.
9. Sort `no_exam_priority` by `action_score` descending; sort `no_exam_closed` and `with_exam` by `match_score` descending.
10. Label ranks 1–3 `第一梯队`, 4–7 `第二梯队`, and 8+ `第三梯队`.
11. Map actions: `在招 → 今天投递`; `待确认/条件性 → 先确认入口，开放就投`; others → `不投旧批次/仅关注更新`.

## 4. Workbook structure

Output `云招聘表岗位筛选_{CANDIDATE_NAME}_{RUN_DATE}.xlsx` with exactly six worksheets in this order. Earlier callers may retain the legacy filename, but workbook contents must state the active employer-nature scope.

### 4.1 `无笔试优先投递`

- Title `A1:R1`: `{CANDIDATE_NAME}｜云招聘表无笔试优先投递（{active employer-nature scope}｜{dynamic target regions}）`.
- Note `A2:R2`: `本版严格采用云表口径：“是否笔试”栏为“/” = 无笔试；“有笔试” = 有笔试。官网信息只用于判断岗位是否仍开放，不覆盖该字段。`
- Summary groups in rows 3–4: `无笔试相关记录`, `当前优先投递`, `明确在招`, `入口待确认`, `有笔试备选`, `云表复核时间`; each occupies three merged columns. Show counts across the active employer-nature scope.
- Header row 6, data from row 7.
- Headers, in order: `序号｜行动优先级｜匹配分｜行动分(公式)｜公司｜建议投递方向｜地区｜届次/批次｜学历｜是否笔试｜当前状态｜截止/状态说明｜建议动作｜简历匹配证据｜专业审核提示｜投递链接｜公告链接｜云表来源`.
- Formula: `=C{row}+IF(K{row}="在招",10,IF(K{row}="待确认",4,0))+5+4`.
- Freeze 6 rows and 5 columns.
- Widths: `7,12,9,12,23,36,22,18,14,20,11,31,20,44,48,32,32,34`.
- Data row height: `72`.
- Table name: `NoExamPriority`.

### 4.2 `无笔试完整清单`

- Title `A1:R1`: `无笔试完整清单｜云表“/”全部按无笔试处理`.
- Header row 4, data from row 5.
- Headers: `记录ID｜匹配档位｜匹配分｜公司｜企业性质｜行业｜目标岗位｜原始岗位｜地点｜届次/批次｜状态｜状态说明｜是否笔试｜当前动作｜专业要求｜投递链接｜公告链接｜云表来源`.
- Freeze 4 rows and 4 columns.
- Widths: `9,9,9,23,12,18,34,46,22,18,12,30,20,22,48,32,32,34`.
- Data row height: `64`.
- Table name: `NoExamAll`.

### 4.3 `无笔试但已截止`

- Title `A1:N1`: `无笔试，但旧批次已截止 / 地区或属性不符`.
- Note: `“无笔试”不等于“现在还能投”。这些记录只用于关注下一批次，不建议继续向旧链接投入时间。`
- Header row 4, data from row 5.
- Headers: `序号｜公司｜岗位方向｜地点｜届次｜匹配分｜是否笔试｜状态｜原因｜表内截止｜建议｜投递链接｜公告链接｜云表来源`.
- Suggestion: `关注{dynamic graduation cohort}秋招/补录，不投旧批次`.
- Freeze 4 rows.
- Widths: `7,23,36,22,15,9,20,14,32,16,30,32,32,34`.
- Data row height: `60`.
- Table name: `NoExamClosed`.

### 4.4 `有笔试备选`

- Title `A1:O1`: `有笔试备选｜仅在无笔试岗位投完后考虑`.
- Note: `云表明确标注“有笔试”的记录独立放置；未说明笔试方式的记录排在其后并标记“笔试待确认”，不得当作无笔试。`
- Header row 4, data from row 5.
- Headers: `序号｜公司｜目标岗位｜地点｜届次/批次｜匹配分｜是否笔试｜状态｜状态说明｜学历｜专业要求｜简历证据｜投递链接｜公告链接｜云表来源`.
- Freeze 4 rows.
- Widths: `7,23,36,22,18,9,12,13,30,14,46,42,32,32,34`.
- Data row height: `62`.
- Table name: `WrittenBackup`.

### 4.5 `简历匹配口径`

- Title `A1:F1`: `简历逐行匹配与网申填写口径`.
- Header row 3.
- Headers: `简历证据｜可投方向｜网申建议写法｜适配单位/场景｜风险｜证明材料`.
- Generate rows dynamically from education/major, courses, skills, projects, research outputs, awards, and work experience. Every row must cite `evidence_map`; omit categories absent from the uploaded resume.
- Freeze 3 rows.
- Widths: `30,34,52,38,34,36`.
- Data row height: `76`.

### 4.6 `每日监测规则`

- Title `A1:D1`: `每日自动复筛规则（供后续每天执行）`.
- Header row 3: `项目｜规则｜输出｜说明`.
- Keep these rows in order: `云表来源`, `来源模式`, `分类范围`, `动态人选`, `企业范围`, `地区`, `届次`, `岗位关键词`, `笔试字段`, `链接核验`, `变化对比`, `提醒优先级`, `人工复核点`.
- `动态人选` must summarize the current profile and source hash; it replaces the prior fixed-person row without changing the four-column interface.
- `企业范围` must show `全部（云表所有单位性质）` by default, or the exact current-request `JOB_NATURE_SCOPE`; never hardcode `央国企/事业单位`.
- `来源模式` must show the active mode and both source URLs when `两表互补` is active.
- `分类范围` must list inspected and explicitly skipped classified-table categories/views.
- `笔试字段`: `综合表“/”=无笔试；“有笔试”=有笔试；其他来源未注明=待确认`.
- `链接核验` must state the trigger fields, evidence order, inaccessible/unresolved links, and verification time.
- Compare by `公司+岗位+地区+届次/批次` and report additions, deadline changes, status changes, and link changes.
- Reminder order: `截止7天内 > 新增无笔试 > 状态由待确认转在招 > 其他变化`.
- Freeze 3 rows.
- Widths: `22,78,42,58`.
- Data row height: `68`.

## 5. Formatting and validation

- Titles: `#183B56`, white bold text.
- Headers: `#147D88`, white bold text, centered and wrapped.
- Borders: thin `#D5DEE5`; vertically center and wrap data.
- `在招`: fill `#DDF3E4`, font `#17663A`.
- `待确认/条件性`: fill `#FFF2CC`, font `#7A4B00`.
- `已截止/届次不符`: fill `#FCE0E0`, font `#9B1C1C`.
- Other status: fill `#EEF1F4`.
- Links: font `#2563EB`, preserve full URL/email text.
- Scan for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, and `#N/A`.
- Render and inspect all six sheets before export.

## 6. Daily comparison

When `DAILY_MODE=true`, compare current and previous results by `company + role + location + cohort/batch`. Report new jobs, deadline changes, status changes, application-link changes, and notice-link changes. Put open no-exam jobs first, flag deadlines within seven days, keep written-exam and exam-unknown jobs separate from no-exam jobs, and retain closed records. If no jobs were added, state `今日无新增` while still reporting other changes.
