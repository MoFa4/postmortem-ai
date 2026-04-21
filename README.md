# 🤖 PostMortemAI | Autonomous SRE Incident Engine
> *Zero-touch, blameless post-mortem generation. Inject → Scan → Done.*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)]()

## 🎯 Problem
Manual post-mortems are rushed, blame-adjacent, and rarely tracked → repeat outages + engineer burnout.

## 💡 Solution
Event-driven engine that auto-detects resolved incidents, unifies telemetry, enforces blameless language, and delivers structured reports to SREs in <3 seconds.

## 🚀 Quick Start
1. Double-click `start.bat`
2. Click **🔴 Inject Incident** → Simulates outage
3. Click **🟢 Scan & Generate** → Auto-generates report, routes to Slack, saves to `./reports/`
4. Double-click `stop.bat` to clean up

## 🛠️ Architecture
`Inject → State Guard → Timeline Unifier + Bias Checker → Markdown Report → Slack/Drive Routing`

## 📈 Next Steps
- [ ] Real Prometheus/OTel ingestion
- [ ] AWS S3 / Confluence upload
- [ ] LLM-grounded root-cause hypotheses
- [ ] Kubernetes deployment manifests

*Built for resilient engineering culture.*
