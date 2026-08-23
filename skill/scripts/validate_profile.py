#!/usr/bin/env python3
"""Validate the stable normalized resume-profile interface."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "schema_version", "status", "source", "candidate", "education",
    "graduation_cohort", "certified_major", "skills", "courses", "projects",
    "research_outputs", "awards", "work_experience", "target_preferences",
    "profile_summary", "evidence_map", "quality",
]
SKILL_KEYS = ["programming", "data", "ai_ml", "gis_remote_sensing", "software_tools", "languages"]
PREFERENCE_KEYS = ["regions", "cities", "role_keywords", "prefer_no_written_exam"]


def fail(message: str) -> int:
    print(json.dumps({"status": "error", "code": "PROFILE_INVALID", "message": message}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        return fail("Usage: validate_profile.py PROFILE.json")
    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.is_file():
        return fail(f"Profile does not exist: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"Invalid JSON: {exc}")
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        return fail(f"Missing top-level fields: {', '.join(missing)}")
    if data["schema_version"] != 1 or data["status"] != "success":
        return fail("schema_version must be 1 and status must be success")
    source = data.get("source") or {}
    if not source.get("file_name") or not re.fullmatch(r"[0-9a-f]{64}", str(source.get("sha256", ""))):
        return fail("source.file_name and a valid source.sha256 are required")
    if not isinstance(data.get("candidate"), dict) or not isinstance(data.get("education"), list):
        return fail("candidate must be an object and education must be an array")
    skills = data.get("skills") or {}
    if any(key not in skills or not isinstance(skills[key], list) for key in SKILL_KEYS):
        return fail("skills must contain all stable array fields")
    preferences = data.get("target_preferences") or {}
    if any(key not in preferences for key in PREFERENCE_KEYS):
        return fail("target_preferences is missing stable fields")
    if not isinstance(data.get("evidence_map"), list):
        return fail("evidence_map must be an array")
    for index, item in enumerate(data["evidence_map"]):
        if not isinstance(item, dict) or item.get("source_type") not in {"resume", "user_override"} or not item.get("claim") or not item.get("evidence"):
            return fail(f"Invalid evidence_map item at index {index}")
    print(json.dumps({"status": "success", "profile": str(path), "source_sha256": source["sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
