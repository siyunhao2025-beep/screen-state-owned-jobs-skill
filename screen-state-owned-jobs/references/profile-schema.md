# Dynamic resume profile schema

## Contents

1. Source contract
2. Normalized profile schema
3. Extraction rules
4. Error states
5. Storage contract

## 1. Source contract

Accept one current resume in PDF, DOCX, TXT, or Markdown format. The parser writes `resume_parse.json` and `resume_text.txt`. Treat the parse JSON as the only resume text source for semantic normalization.

`resume_parse.json` contains:

```json
{
  "schema_version": 1,
  "status": "success | needs_ocr | error",
  "source": {
    "file_name": "string",
    "extension": ".pdf | .docx | .txt | .md | .markdown",
    "sha256": "string",
    "size_bytes": 0,
    "parsed_at_utc": "ISO-8601 string",
    "parser": "string",
    "page_count": 0
  },
  "stats": {
    "character_count": 0,
    "non_whitespace_count": 0,
    "line_count": 0
  },
  "contacts": {
    "emails": [],
    "phones": [],
    "urls": []
  },
  "section_hints": {},
  "warnings": [],
  "raw_text": "string",
  "error": null
}
```

## 2. Normalized profile schema

Write `resume_profile.json` with exactly these top-level fields:

```json
{
  "schema_version": 1,
  "status": "success",
  "source": {
    "file_name": "string",
    "sha256": "string",
    "parsed_at_utc": "ISO-8601 string"
  },
  "candidate": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "current_location": "string"
  },
  "education": [],
  "graduation_cohort": "string",
  "certified_major": {
    "value": "string",
    "source_type": "resume | user_override | unknown",
    "evidence": "string"
  },
  "skills": {
    "programming": [],
    "data": [],
    "ai_ml": [],
    "gis_remote_sensing": [],
    "software_tools": [],
    "languages": []
  },
  "courses": [],
  "projects": [],
  "research_outputs": [],
  "awards": [],
  "work_experience": [],
  "target_preferences": {
    "regions": [],
    "cities": [],
    "role_keywords": [],
    "prefer_no_written_exam": null
  },
  "profile_summary": "string",
  "evidence_map": [],
  "quality": {
    "missing_critical_fields": [],
    "warnings": []
  }
}
```

Each `education` item uses:

```json
{
  "school": "string",
  "degree": "string",
  "major": "string",
  "start_date": "string",
  "end_date": "string",
  "evidence": "exact resume excerpt"
}
```

Each project, publication, award, or work item must include an `evidence` field containing an exact excerpt. Each `evidence_map` item uses:

```json
{
  "claim": "normalized claim",
  "source_type": "resume | user_override",
  "evidence": "exact resume excerpt or exact user override"
}
```

## 3. Extraction rules

1. Preserve facts, dates, scores, software names, publication status, authorship, award level, and units exactly.
2. Do not convert a research direction into a formal degree major.
3. Leave `certified_major.value` empty unless the resume or the current user explicitly states an equivalence or certification.
4. Derive graduation cohort only from an explicit graduation/end date. If ambiguous, leave it empty and add `graduation_cohort` to `missing_critical_fields`.
5. Derive job keywords only from demonstrated education, skills, projects, research, and current-request preferences.
6. Keep target preferences empty when neither the resume nor the current request supplies them.
7. Apply current-request overrides after resume extraction and label them `user_override`.
8. Never insert the prior candidate's identity or evidence.

## 4. Error states

- Missing file: `RESUME_REQUIRED`.
- Unsupported extension: `UNSUPPORTED_FORMAT`.
- Empty file: `EMPTY_FILE`.
- Password-protected or unreadable PDF: `PDF_UNREADABLE`.
- Corrupted DOCX: `DOCX_UNREADABLE`.
- Extracted text below threshold: `OCR_REQUIRED` with status `needs_ocr`.
- Profile missing a required top-level field or source hash: `PROFILE_INVALID`.

Do not silently reuse an earlier profile after any current-upload error.

## 5. Storage contract

Store files under:

```text
outputs/job-screening/{RUN_DATE}/resume/
├── resume_parse.json
├── resume_text.txt
└── resume_profile.json
```

Store the generated workbook beside the `resume/` directory. Preserve the SHA-256 hash so daily runs can detect a changed resume. A different hash requires reparsing and rebuilding the profile.
