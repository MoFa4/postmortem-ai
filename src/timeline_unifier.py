# src/timeline_unifier.py
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

class TimelineUnifier:
    def __init__(self, skew_tolerance_sec: int = 5):
        self.skew_tolerance = timedelta(seconds=skew_tolerance_sec)
        self.events = []

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Handles ISO 8601, spaced logs, and Unix epochs."""
        ts_str = ts_str.strip()
        for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        # Fallback: Unix timestamp (seconds)
        try:
            return datetime.fromtimestamp(float(ts_str))
        except (ValueError, OSError):
            raise ValueError(f"Unsupported timestamp format: {ts_str}")

    def ingest_events(self, raw_events: List[Dict[str, Any]]):
        """Normalize & validate incoming events from any source."""
        for evt in raw_events:
            try:
                ts = self._parse_timestamp(evt["timestamp"])
                self.events.append({
                    "timestamp": ts,
                    "source": evt.get("source", "unknown"),
                    "service": evt.get("service", "unknown"),
                    "message": evt["message"],
                    "type": evt.get("type", "log")
                })
            except (KeyError, ValueError) as e:
                print(f"⚠️ Skipping malformed event: {e}")

    def _cluster_events(self) -> List[Dict]:
        """Merge events within skew tolerance to avoid timeline clutter."""
        if not self.events:
            return []

        sorted_events = sorted(self.events, key=lambda x: x["timestamp"])
        clusters = []
        current_cluster = [sorted_events[0]]

        for evt in sorted_events[1:]:
            if evt["timestamp"] - current_cluster[0]["timestamp"] <= self.skew_tolerance:
                current_cluster.append(evt)
            else:
                clusters.append(current_cluster)
                current_cluster = [evt]
        clusters.append(current_cluster)

        # Convert clusters → clean timeline entries
        timeline = []
        for cluster in clusters:
            ts = cluster[0]["timestamp"]
            messages = [f"[{e['source'].upper()}] {e['message']}" for e in cluster]
            timeline.append({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "events": messages,
                "services_involved": list(set(e["service"] for e in cluster))
            })
        return timeline

    def build_timeline(self) -> List[Dict]:
        return self._cluster_events()

    def export_markdown(self) -> str:
        timeline = self.build_timeline()
        md = "## 🔹 Incident Timeline (UTC)\n| Time | Events |\n|------|--------|\n"
        for entry in timeline:
            events_str = "<br>".join(entry["events"])
            md += f"| {entry['timestamp']} | {events_str} |\n"
        return md

# 🧪 DEMO MODE
if __name__ == "__main__":
    unifier = TimelineUnifier(skew_tolerance_sec=5)

    # Simulated raw incident data (different formats, sources, clock skews)
    raw_incident_data = [
        {"timestamp": "2026-04-18T22:00:00Z", "source": "PagerDuty", "service": "checkout", "message": "Alert: error_rate > 5%", "type": "alert"},
        {"timestamp": "2026-04-18 22:00:03", "source": "CloudWatch", "service": "payment", "message": "Connection pool exhausted", "type": "log"},
        {"timestamp": "1713470405", "source": "OpenTelemetry", "service": "payment", "message": "Trace: timeout on DB query", "type": "trace"},
        {"timestamp": "2026-04-18T22:00:07.123Z", "source": "Slack", "service": "on-call", "message": "Engineer joined #incidents", "type": "human"},
        {"timestamp": "2026-04-18 22:15:00", "source": "GitHub", "service": "payment", "message": "Deployed hotfix: increased pool size", "type": "action"},
        {"timestamp": "2026-04-18T22:22:00Z", "source": "Grafana", "service": "checkout", "message": "Error rate normalized", "type": "metric"},
    ]

    unifier.ingest_events(raw_incident_data)
    print("🕰️ Unified Timeline Generated:\n")
    print(unifier.export_markdown())