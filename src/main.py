# src/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import os, uuid
from src.bias_checker import check_bias, fix_bias
from src.timeline_unifier import TimelineUnifier
from src.report_generator import ReportGenerator
from src.storage import DriveUploader
from src.notifier import SlackNotifier
import uvicorn

app = FastAPI(title="PostMortemAI v2.1", version="Clean-2Step")
app.mount("/static", StaticFiles(directory="static"), name="static")

# STRICT in-memory state. Resets on restart. No auto-triggers.
active_incidents = {}

class InjectRequest(BaseModel):
    service: str = "checkout-service"
    error: str = "db_pool_exhaustion"

@app.post("/inject")
def inject_incident(req: InjectRequest = InjectRequest()):
    incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.utcnow()
    events = [
        {"timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "Prometheus", "service": req.service, "message": f"Alert: {req.error} detected"},
        {"timestamp": (now + timedelta(seconds=3)).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "CloudWatch", "service": req.service, "message": "Error rate > 40%, latency spike"},
        {"timestamp": (now + timedelta(seconds=12)).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "PagerDuty", "service": req.service, "message": "On-call acknowledged"},
        {"timestamp": (now + timedelta(seconds=25)).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "GitHub", "service": req.service, "message": "Hotfix deployed"}
    ]
    active_incidents[incident_id] = {"id": incident_id, "status": "injected", "events": events}
    return {"status": "ready", "incident_id": incident_id}

@app.post("/scan")
def scan_and_generate():
    if not active_incidents:
        return {"status": "normal", "message": "✅ No abnormalities detected. System is healthy."}
    
    # Grab latest injected incident
    incident_id, inc = list(active_incidents.items())[-1]
    
    unifier = TimelineUnifier()
    unifier.ingest_events(inc["events"])
    timeline_md = unifier.export_markdown()
    
    narrative = f"Service {inc['events'][0]['service']} failed due to simulated error. Resolved via hotfix."
    bias_result = check_bias(narrative)
    bias_result["blameless_revision"] = fix_bias(narrative) if bias_result["has_bias"] else narrative
    
    generator = ReportGenerator()
    report_md = generator.generate_full_report(incident_id, timeline_md, bias_result, narrative)
    
    drive = DriveUploader()
    notifier = SlackNotifier()
    report_url = drive.upload(f"{incident_id}.md", report_md)
    notifier.send_report_alert(incident_id, "@sre-oncall", report_url)
    
    active_incidents.clear()  # Reset state after scan
    return {"status": "success", "report_url": report_url, "incident_id": incident_id}

@app.get("/reports/{filename}")
def get_report(filename: str):
    path = os.path.join("reports", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="text/markdown")
    raise HTTPException(status_code=404, detail="Report not found")

@app.get("/health")
def health(): 
    return {"status": "healthy", "pending_incidents": len(active_incidents)}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
