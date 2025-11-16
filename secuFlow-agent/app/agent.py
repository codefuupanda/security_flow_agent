from pathlib import Path
import json
import csv
from collections import Counter
import os
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # handle case where openai isn't installed

load_dotenv()
# Path to the logs JSON we created earlier
LOGS_PATH = Path(r"C:\Users\arusi\projects\secuFlow-agent\logs\windows_logs.json")

# Path to the templates CSV you downloaded
TEMPLATES_PATH = Path(r"C:\Users\arusi\projects\secuFlow-agent\data\Windows_2k.log_templates.csv")
def load_logs():
    """
    Load all logs from the JSON file.
    Returns a list of dicts.
    """
    if not LOGS_PATH.exists():
        raise FileNotFoundError(f"Log file not found at {str(LOGS_PATH)}")

    with LOGS_PATH.open("r", encoding="utf-8") as f:
        logs = json.load(f)

    return logs

def get_templates_for_event(event_id: str) -> dict:
    """
    Given an EventId like 'E36', return its log template(s)
    from the templates CSV.

    It is robust to slight differences in column names such as:
    - EventId / EventID / event_id
    - EventTemplate / Event_Template
    """
    if not TEMPLATES_PATH.exists():
        raise FileNotFoundError(f"Templates file not found at {str(TEMPLATES_PATH)}")

    templates = []

    with TEMPLATES_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Normalize header names (case-insensitive, strip spaces)
        fieldnames = [name.strip() for name in reader.fieldnames]

        # Map original name → normalized lower-case
        norm_map = {orig: orig.strip().lower() for orig in reader.fieldnames}

        # Try to detect the right columns
        eventid_col = None
        template_col = None

        for orig, norm in norm_map.items():
            if norm in ("eventid", "event_id"):
                eventid_col = orig
            if norm in ("eventtemplate", "event_template"):
                template_col = orig

        if eventid_col is None or template_col is None:
            raise ValueError(
                f"Could not detect EventId / EventTemplate columns in {TEMPLATES_PATH}. "
                f"Found columns: {fieldnames}"
            )

        # Collect all templates matching this EventId
        for row in reader:
            if row.get(eventid_col) == event_id:
                templates.append(row.get(template_col))

    # Remove possible duplicates
    templates = sorted(set(t for t in templates if t))

    return {
        "event_id": event_id,
        "templates_found": len(templates),
        "templates": templates,
    }

def analyze_recent_logs(limit: int = 200) -> dict:
    """
    Simple 'agent' logic:
    - Take the last N log entries
    - Count events by event_id and source
    - Return a structured summary
    """
    logs = load_logs()

    if not logs:
        return {
            "total_events_analyzed": 0,
            "top_event_ids": [],
            "top_sources": [],
            "notes": ["No logs available."]
        }

    # Take the last N logs (simulate 'recent' activity)
    recent_logs = logs[-limit:]

    # Count by event_id and source (if missing, use "unknown")
    event_ids = [entry.get("event_id", "unknown") for entry in recent_logs]
    sources = [entry.get("source", "unknown") for entry in recent_logs]

    event_id_counts = Counter(event_ids)
    source_counts = Counter(sources)

    # Prepare sorted lists for output (top 5)
    top_event_ids = [
        {"event_id": eid, "count": count}
        for eid, count in event_id_counts.most_common(5)
    ]

    top_sources = [
        {"source": src, "count": count}
        for src, count in source_counts.most_common(5)
    ]

    notes = []

    # Simple heuristic: if one event type dominates, mention it
    if top_event_ids:
        most_common_eid = top_event_ids[0]
        if most_common_eid["count"] > len(recent_logs) * 0.3:
            notes.append(
                f"EventId {most_common_eid['event_id']} appears frequently "
                f"({most_common_eid['count']} times in the last {len(recent_logs)} events)."
            )

    if not notes:
        notes.append("No dominant event type detected in the recent logs.")

    return {
        "total_events_analyzed": len(recent_logs),
        "top_event_ids": top_event_ids,
        "top_sources": top_sources,
        "notes": notes,
    }

def detect_incidents(summary: dict) -> list[dict]:
    """
    Naive incident detection based on the summary.

    Rules (you can improve later):
    - If the top event_id has > 40% of events -> MEDIUM incident.
    - If top 2 event_ids together have > 70% of events -> HIGH incident.
    - If all sources are 'unknown' -> LOW incident (poor observability).
    """
    incidents = []

    total = summary.get("total_events_analyzed") or 0
    top_event_ids = summary.get("top_event_ids") or []
    top_sources = summary.get("top_sources") or []

    if total <= 0:
        return incidents

    # Rule 1: dominant single event_id
    if top_event_ids:
        top1 = top_event_ids[0]
        top1_ratio = top1["count"] / total

        if top1_ratio > 0.4:
            incidents.append({
                "id": 1,
                "severity": "MEDIUM",
                "reason": (
                    f"EventId {top1['event_id']} accounts for "
                    f"{top1['count']} of {total} events (~{top1_ratio:.0%})."
                ),
                "related_event_ids": [top1["event_id"]],
            })

    # Rule 2: top 2 event_ids dominate
    if len(top_event_ids) >= 2:
        top2 = top_event_ids[1]
        top1 = top_event_ids[0]
        combined = top1["count"] + top2["count"]
        combined_ratio = combined / total

        if combined_ratio > 0.7:
            incidents.append({
                "id": 2,
                "severity": "HIGH",
                "reason": (
                    f"EventIds {top1['event_id']} and {top2['event_id']} "
                    f"together account for {combined} of {total} events "
                    f"(~{combined_ratio:.0%})."
                ),
                "related_event_ids": [top1["event_id"], top2["event_id"]],
            })

    # Rule 3: all sources 'unknown' (observability issue)
    if top_sources:
        # If the only top source is 'unknown'
        if len(top_sources) == 1 and top_sources[0].get("source") == "unknown":
            incidents.append({
                "id": 3,
                "severity": "LOW",
                "reason": (
                    "All recent events are from 'unknown' source. "
                    "This may indicate missing or incomplete log source tags."
                ),
                "related_event_ids": [e["event_id"] for e in top_event_ids],
            })

    return incidents

def generate_ai_explanation(summary: dict) -> str:
    """
    Optional: use an LLM to generate a human-readable security explanation
    of the summary returned by analyze_recent_logs.

    If OpenAI or API key is missing, it returns a fallback message.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    # Safety: if no key or library, return a basic explanation
    if not api_key or OpenAI is None:
        return (
            "AI explanation not available (no API key configured). "
            "Summary:\n"
            f"- Total events analyzed: {summary.get('total_events_analyzed')}\n"
            f"- Top event IDs: {summary.get('top_event_ids')}\n"
            f"- Top sources: {summary.get('top_sources')}\n"
            f"- Notes: {summary.get('notes')}"
        )

    client = OpenAI(api_key=api_key)

    # Build a concise prompt
    prompt = (
        "You are a security analyst. You receive a summary of Windows event logs. "
        "Explain in clear, concise language what is going on and whether anything "
        "looks suspicious. Don't invent facts; base everything only on the summary.\n\n"
        f"Summary JSON:\n{json.dumps(summary, indent=2)}"
    )

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        # Extract first text output
        msg = response.output[0].content[0].text
        return msg
    except Exception as e:
        return (
            "Failed to generate AI explanation. "
            f"Error: {e}. "
            f"Fallback summary: {summary}"
        )

