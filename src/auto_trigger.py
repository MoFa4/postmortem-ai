# src/auto_trigger.py
import os, json, requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.timeline_unifier import TimelineUnifier
from src.bias_checker import check_bias, fix_bias
from src.report_generator import ReportGenerator

class AutoSREBridge:
    def __init__(self, slack_webhook_url: str = os.getenv("SLACK_WEBHOOK", "")):
        self.slack_url = slack_webhook_url
        self.generator = ReportGenerator()

    def _extract_time_window(self, alert_payload: Dict) -> tuple:
        """Pulls start/end time from resolved alert. Mocks real data for dev."""
        # Real payload would come from PagerDuty/Alertmanager
        start = alert_payload.get("started_at", "2026-04-18T22:00:00Z")
        end = alert_payload.get("resolved_at", "2026-04-18T22:25:00Z")
        services = alert_payload.get("affected_services", ["checkout", "payment"])
        assignee = alert_payload.get("assignee", "@sre-oncall")
        return start, end, services, assignee

    def _fetch_context(self, start: str, end: str, services: List[str]) -> List[Dict]:
        """In prod: calls OTel/CloudWatch/Slack APIs for this time window.
        Here: simulates realistic auto-scanned data."""
        return [
            {"timestamp": start, "source": "PagerDuty", "service": services[0], "message": f"Alert triggered for {services[0]}"},
            {"timestamp": "2026-04-18T22:03:12Z", "source": "CloudWatch", "service": services[1], "message": "Connection pool saturation detected"},
            {"timestamp": "2026-04-18T22:10:45Z", "source": "Slack", "service": "incident-channel", "message": f"@{services[0]}-team investigating spike"},
            {"timestamp": "2026-04-18T22:18:30Z", "source": "GitHub", "service": services[1], "message": "Hotfix deployed: pool size + retry logic"},
            {"timestamp": end, "source": "Grafana", "service": services[0], "message": "Metrics normalized. Incident resolved."}
        ]

    def _send_to_sre(self, assignee: str, incident_id: str, report_md: str, report_url: str):
        """Delivers report to the handling SRE. Mocks Slack DM for dev."""
        if not self.slack_url:
            print(f"📤 [MOCK] Sending report to {assignee}\n🔗 {report_url}")
            return
        # Real Slack delivery
        payload = {
            "text": f"📋 Post-Mortem Auto-Generated for `{incident_id}`\n{report_url}\n\n*Blameless revision applied. Review & publish.*"
        }
        requests.post(self.slack_url, json=payload, timeout=10)

    def process_resolved_alert(self, alert_payload: Dict) -> Dict:
        incident_id = alert_payload.get("incident_id", f"INC-{int(datetime.utcnow().timestamp())}")
        start, end, services, assignee = self._extract_time_window(alert_payload)
        
        # 1️⃣ Auto-scan context
        raw_events = self._fetch_context(start, end, services)
        
        # 2️⃣ Generate timeline & bias check
        unifier = TimelineUnifier(skew_tolerance_sec=5)
        unifier.ingest_events(raw_events)
        timeline_md = unifier.export_markdown()
        
        narrative = f"Alert resolved for {', '.join(services)}. Automated context fetch complete."
        bias_result = check_bias(narrative)
        bias_result["blameless_revision"] = fix_bias(narrative) if bias_result["has_bias"] else narrative

        # 3️⃣ Build full report
        report_md = self.generator.generate_full_report(incident_id, timeline_md, bias_result, narrative)
        
        # 4️⃣ Upload to Drive & Notify Slack
        from src.storage import DriveUploader
        from src.notifier import SlackNotifier
        
        drive = DriveUploader()
        notifier = SlackNotifier()
        
        report_url = drive.upload(f"{incident_id}.md", report_md)
        notifier.send_report_alert(incident_id, assignee, report_url)
        
        return {"status": "auto_generated", "incident_id": incident_id, "report_url": report_url}