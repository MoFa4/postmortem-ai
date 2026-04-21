# src/report_generator.py
from datetime import datetime
from typing import Dict, Any, List

class ReportGenerator:
    def generate_full_report(self, incident_id: str, timeline_md: str, bias_result: Dict, narrative: str) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        # Extract impact & action placeholders (MVP-grade, easily extensible)
        exec_summary = self._draft_exec_summary(narrative, timeline_md)
        bias_flags = ", ".join(bias_result["flags"]) if bias_result["flags"] else "None detected"
        
        report = f"""# 📋 Post-Mortem Report: `{incident_id}`
**Generated**: {now} | **Engine**: PostMortemAI v0.2.0

## 🔹 Executive Summary
{exec_summary}

## 🔹 Incident Timeline
{timeline_md}

## 🔹 Root Cause Analysis
*Based on automated log clustering and configuration correlation:*
- [ ] Primary hypothesis to be validated by engineering
- [ ] Secondary contributing factors pending runbook review

## 🔹 Impact Assessment
| Metric | Value |
|--------|-------|
| Duration | [Auto-calculate from timeline] |
| Users Affected | [Pull from analytics] |
| SLA Impact | [Check status page] |

## 🔹 Bias & Culture Check
| Flagged Phrase | Suggested Rewrite |
|----------------|-------------------|
| {bias_flags or "N/A"} | See `blameless_revision` below |

**Blameless Revision**: `{bias_result.get("blameless_revision", narrative)}`

## 🔹 Action Items (Template)
| Task | Owner | Priority | Due | Status |
|------|-------|----------|-----|--------|
| Validate root cause hypothesis | @eng-lead | P0 | +48h | ⚪ |
| Update runbook with new scenario | @sre | P1 | +72h | ⚪ |
| Add alert threshold for {incident_id} pattern | @monitoring | P2 | +1w | ⚪ |

## 🔹 Lessons Learned
✅ What went well: [Auto-extract positive signals from logs]  
🔧 What to improve: [Bias flags + missing validation gaps]  
🔄 Systemic change: [Promote to architecture review]

---
*Generated automatically by PostMortemAI. Review, validate, and publish.*
"""
        return report

    def _draft_exec_summary(self, narrative: str, timeline: str) -> str:
        # Simple NLP-like summary extraction for MVP
        first_line = narrative.split(".")[0].strip() if narrative else "Incident data ingested."
        last_event = timeline.split("|")[-2].strip() if "|" in timeline else "Timeline generated."
        return f"{first_line}. {last_event.replace('[', '').replace(']', '').strip()}. Full analysis attached."