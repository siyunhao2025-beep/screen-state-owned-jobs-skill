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
- `FEISHU_URL`: default `https://yal2at57cvq.feishu.cn/base/GtSLbyyR3aCENOsJYC6cdlsVnih?table=tblH4au5rnBcqHgJ&view=vewFBnAr4c`.
- `RUN_DATE`: `YYYY-MM-DD`.
- `PREVIOUS_RESULT`: optional on first run.
- `DAILY_MODE`: boolean.

Map dynamic profile values to the earlier interface as follows:

- `CANDIDATE_NAME = resume_profile.candidate.name || "候选人"`
- `GRADUATION_COHORT = resume_profile.graduation_cohort`
- `DEGREE` and `ORIGINAL_MAJOR` come from the most recent relevant education item.
- `CERTIFIED_MAJOR = resume_profile.certified_major.value`; leave empty when unsupported.
- `TARGET_REGIONS`, `TARGET_CITIES`, and `TARGET_KEYWORDS` come from `target_preferences` plus demonstrated profile evidence.
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

`exam` must remain `/` or `有笔试`. Display `/` as `无笔试（云表“/”）`. Never reinterpret it as unknown.

Use only these statuses: `在招`, `待确认`, `条件性`, `属性待核验`, `已截止`, `届次不符`, `不推荐/待核验`, `非央国企`.

Use only these tiers: `S`, `A`, `B`, `C`, with boundaries `S=90–100`, `A=85–89`, `B=70–84`, `C=0–69`.

## 3. Filtering and ranking

1. Filter enterprise nature to `央国企` and `事业单位`.
2. Derive target regions, cities, cohort, degree, major, and role keywords from the dynamic profile and current user preferences.
3. Retain nationwide records but mark that the exact technical-role city requires confirmation.
4. Deduplicate by `company + role + location`; do not merge different roles, locations, or batches.
5. Define `no_exam` as `exam === '/'` and `with_exam` as `exam === '有笔试'`.
6. Define `no_exam_priority` as no-exam records with status in `在招`, `待确认`, or `条件性`, matching dynamic region/cohort requirements, and `match_score >= 65`.
7. Define `no_exam_closed` as no-exam records whose status is outside `在招`, `待确认`, and `条件性`.
8. Compute `action_score = match_score + status_bonus + region_bonus + cohort_bonus`, where `在招=10`, `待确认=4`, other status `=0`, region match `=5`, and cohort match `=4`.
9. Sort `no_exam_priority` by `action_score` descending; sort `no_exam_closed` and `with_exam` by `match_score` descending.
10. Label ranks 1–3 `第一梯队`, 4–7 `第二梯队`, and 8+ `第三梯队`.
11. Map actions: `在招 → 今天投递`; `待确认/条件性 → 先确认入口，开放就投`; others → `不投旧批次/仅关注更新`.

## 4. Workbook structure

Output `央国企无笔试岗位筛选_{CANDIDATE_NAME}_{RUN_DATE}.xlsx` with exactly six worksheets in this order.

### 4.1 `无笔试优先投递`

- Title `A1:R1`: `{CANDIDATE_NAME}｜央国企无笔试优先投递（{dynamic target regions}）`.
- Note `A2:R2`: `本版严格采用云表口径：“是否笔试”栏为“/” = 无笔试；“有笔试” = 有笔试。官网信息只用于判断岗位是否仍开放，不覆盖该字段。`
- Summary groups in rows 3–4: `无笔试相关记录`, `当前优先投递`, `明确在招`, `入口待确认`, `有笔试备选`, `云表复核时间`; each occupies three merged columns.
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
- Note: `云表明确标注“有笔试”的记录独立放置，不与无笔试岗位混排。`
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
- Keep these rows in order: `云表来源`, `动态人选`, `企业范围`, `地区`, `届次`, `岗位关键词`, `笔试字段`, `变化对比`, `提醒优先级`, `人工复核点`.
- `动态人选` must summarize the current profile and source hash; it replaces the prior fixed-person row without changing the four-column interface.
- `笔试字段`: `“/”=无笔试；“有笔试”=有笔试`.
- Compare by `公司+岗位+地区` and report additions, deadline changes, status changes, and link changes.
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

When `DAILY_MODE=true`, compare current and previous results by `company + role + location`. Report new jobs, deadline changes, status changes, application-link changes, and notice-link changes. Put open no-exam jobs first, flag deadlines within seven days, keep written-exam jobs separate, and retain closed records. If no jobs were added, state `今日无新增` while still reporting other changes.
