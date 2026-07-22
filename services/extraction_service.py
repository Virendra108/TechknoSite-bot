import json
from datetime import date
from typing import Any

from groq import Groq
from jsonschema import Draft202012Validator


REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "report_id",
        "date",
        "project_name",
        "location",
        "prepared_by",
        "executive_summary",
        "work_summary",
        "resources_used",
        "issues",
        "next_day_plan",
        "overall_progress_percent",
        "overall_status",
        "safety_incidents",
        "additional_remarks",
    ],
    "properties": {
        "report_id": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},
        "project_name": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "prepared_by": {"type": ["string", "null"]},
        "executive_summary": {"type": ["string", "null"]},
        "work_summary": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "area_location",
                    "activity",
                    "progress_percent",
                    "date",
                    "responsible_person",
                    "status",
                    "remarks",
                ],
                "properties": {
                    "area_location": {"type": ["string", "null"]},
                    "activity": {"type": ["string", "null"]},
                    "progress_percent": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                    "responsible_person": {"type": ["string", "null"]},
                    "status": {"type": ["string", "null"]},
                    "remarks": {"type": ["string", "null"]},
                },
            },
        },
        "resources_used": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["resource_type", "description", "quantity"],
                "properties": {
                    "resource_type": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "quantity": {"type": ["string", "null"]},
                },
            },
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["issue", "impact", "action_taken", "responsible_person"],
                "properties": {
                    "issue": {"type": ["string", "null"]},
                    "impact": {"type": ["string", "null"]},
                    "action_taken": {"type": ["string", "null"]},
                    "responsible_person": {"type": ["string", "null"]},
                },
            },
        },
        "next_day_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["area", "planned_activity", "target_completion"],
                "properties": {
                    "area": {"type": ["string", "null"]},
                    "planned_activity": {"type": ["string", "null"]},
                    "target_completion": {"type": ["string", "null"]},
                },
            },
        },
        "overall_progress_percent": {"type": ["string", "null"]},
        "overall_status": {
            "type": ["string", "null"],
            "enum": ["In Progress", "Completed", "Delayed", "On Hold", None],
        },
        "safety_incidents": {"type": ["string", "null"]},
        "additional_remarks": {"type": ["string", "null"]},
    },
}


SYSTEM_PROMPT = """You extract daily construction progress report fields.
Return strict JSON only. Use the transcript as the only source of truth.
Do not invent missing details. Use null for missing scalar fields and [] for
missing lists. Keep values concise and in English."""


class ExtractionService:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = Groq(api_key=api_key)
        self.model = model
        self.validator = Draft202012Validator(REPORT_SCHEMA)

    def extract(self, transcript_en: str, job_id: str, received_date: date) -> dict[str, Any]:
        reminder = ""
        last_error = ""
        for attempt in range(2):
            content = self._call_llm(transcript_en, reminder)
            try:
                data = json.loads(content)
                self.validator.validate(data)
                return self._apply_defaults(data, job_id, received_date)
            except Exception as exc:
                last_error = str(exc)
                reminder = (
                    "Your previous response was invalid. Return only one valid JSON object "
                    "matching the schema exactly; no markdown, no explanations."
                )
        raise ValueError(f"Could not parse valid report JSON after retry: {last_error}")

    def _call_llm(self, transcript_en: str, reminder: str) -> str:
        user_prompt = {
            "schema": REPORT_SCHEMA,
            "transcript_en": transcript_en,
            "reminder": reminder,
        }
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def _apply_defaults(self, data: dict[str, Any], job_id: str, received_date: date) -> dict[str, Any]:
        if not data.get("report_id"):
            data["report_id"] = job_id
        if not data.get("date"):
            data["date"] = received_date.isoformat()
        for list_key in ["work_summary", "resources_used", "issues", "next_day_plan"]:
            data[list_key] = data.get(list_key) or []
        return data
