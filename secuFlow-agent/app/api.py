from fastapi import FastAPI
from pathlib import Path
import json

from . import agent 

# Create FastAPI app instance
app = FastAPI(title="SecuFlow Agent API")

# Absolute path to your prepared logs file
LOGS_PATH = Path(r"C:\Users\user\projects\secuFlow-agent\logs\windows_logs.json")


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Simple endpoint to verify that the API is running.
    """
    return {"status": "ok"}


# Return a small sample of logs
@app.get("/logs/sample")
def get_sample_logs(limit: int = 10):
    """
    Return the first N log records from the Windows logs JSON file.
    Default: 10 records.
    """
    if not LOGS_PATH.exists():
        return {"error": f"Log file not found at {str(LOGS_PATH)}"}

    with LOGS_PATH.open("r", encoding="utf-8") as f:
        logs = json.load(f)

    limit = min(limit, len(logs))
    return logs[:limit]

@app.get("/event/template/{event_id}")
def get_event_template(event_id: str):
    """
    Return the log template(s) associated with a given EventId, e.g. 'E36'.
    """
    try:
        return agent.get_templates_for_event(event_id)
    except FileNotFoundError as e:
        return {"error": str(e)}
    except ValueError as e:
        # Problem with CSV header
        return {"error": str(e)}
    
# Analyze logs using the agent
@app.post("/analyze")
def analyze_logs(limit: int = 200):
    """
    Use the 'agent' module to analyze the most recent logs.
    - summary: counts and top events
    - incidents: naive detection based on summary
    - ai_explanation: human-readable explanation (LLM or fallback)
    """
    try:
        summary = agent.analyze_recent_logs(limit=limit)
        incidents = agent.detect_incidents(summary)
        ai_explanation = agent.generate_ai_explanation(summary)

        return {
            "summary": summary,
            "incidents": incidents,
            "ai_explanation": ai_explanation,
        }
    except FileNotFoundError as e:
        return {"error": str(e)}


