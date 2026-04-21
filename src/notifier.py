# src/notifier.py
import os, requests

class SlackNotifier:
    def __init__(self, webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")):
        self.webhook = webhook_url

    def send_report_alert(self, incident_id: str, assignee: str, report_url: str):
        if not self.webhook:
            print(f"📤 [MOCK SLACK] Posting to #sre-reports for {assignee}: {report_url}")
            return

        payload = {
            "text": f"📋 *Post-Mortem Generated*: `{incident_id}`\n"
                    f"👤 *Assignee*: {assignee}\n"
                    f"🔗 *Report*: {report_url}\n"
                    f"⚡ Please review, validate root cause, & close action items.",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": f"🚨 Post-Mortem Ready: {incident_id}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Assignee:* {assignee}\n*Status:* Auto-generated • Bias-checked • Timeline unified"}},
                {"type": "actions", "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "📄 Open Report"}, "url": report_url, "style": "primary"},
                    {"type": "button", "text": {"type": "plain_text", "text": "✅ Acknowledge"}, "url": "https://jira.company.com/"}
                ]}
            ]
        }
        res = requests.post(self.webhook, json=payload, timeout=10)
        res.raise_for_status()
        print(f"✅ Slack alert sent for {incident_id} to {assignee}")