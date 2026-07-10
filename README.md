# 🚀 AutoPatch Forge

> Autonomous Self-Healing CI/CD Platform powered by FastAPI, Fireworks AI, Google DeepMind Gemma, Docker and Streamlit.

AutoPatch Forge is an AI-powered multi-agent remediation platform that intercepts CI/CD pipeline failures, analyzes runtime exceptions, generates safe code patches, performs AI-based risk assessment, and prepares automated GitHub pull requests.

---

## ✨ Features

- 🔍 Runtime Trace Analyzer
- 🤖 AI Patch Planning Agent
- 🛡 Google DeepMind Gemma Risk Assessment
- 🩹 Deterministic Patch Engine
- 🌿 Automated Git Branch & Pull Request
- 📊 Interactive Streamlit Dashboard
- 🐳 Docker Development Environment

---

# Architecture

```
Pipeline Failure
        │
        ▼
Trace Analyzer
        │
        ▼
Patch Planner
        │
        ▼
Gemma Risk Assessment
        │
        ▼
Patch Engine
        │
        ▼
GitHub Pull Request
```

---

# Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| AI Runtime | Fireworks AI |
| AI Models | Google DeepMind Gemma |
| Dashboard | Streamlit |
| Container | Docker |
| Language | Python 3.12 |
| Dependency Manager | Astral UV |

---

# Repository Structure

```
app/
├── agents/
├── ai/
├── api/
├── core/
├── models/
├── services/

dashboard/

docker-compose.dev.yml
docker-compose.yml
Dockerfile
README.md
```

---

# Environment Configuration

Copy the example environment.

```bash
cp .env.example .env.local
```

Update the following values.

```env
APP_ENV=development

HOST=0.0.0.0
PORT=8000

FIREWORKS_API_KEY=YOUR_FIREWORKS_API_KEY

FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1

PATCH_PLANNER_MODEL=accounts/fireworks/models/gemma-4-31b-it

RISK_ASSESSOR_MODEL=accounts/fireworks/models/gemma-4-31b-it
```

---

# Local Development

Create the environment.

```bash
uv venv

source .venv/bin/activate

uv sync
```

Run FastAPI.

```bash
uv run uvicorn app.main:app --reload
```

Run Streamlit.

```bash
uv run streamlit run dashboard/app.py
```

FastAPI

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/docs
```

Dashboard

```
http://localhost:8501
```

---

# Docker Development

Build and start the development environment.

```bash
docker compose -f docker-compose.dev.yml up -d --build
```
Open http://localhost:8501/autopatch/

Stop.

```bash
docker compose -f docker-compose.dev.yml down
```

View logs.

```bash
docker compose -f docker-compose.dev.yml logs -f
```

Restart.

```bash
docker compose -f docker-compose.dev.yml restart
```

---

# Example API Request

```bash
curl -X POST http://localhost:8000/api/v1/intercept \
-H "Content-Type: application/json" \
-d '{
  "repo_url":"https://github.com/apurba-labs/autopatch-forge",
  "branch":"main",
  "commit_sha":"demo123",
  "error_log":"Traceback (most recent call last):\nFile \"app/utils/helpers.py\", line 14\nModuleNotFoundError: No module named '\''httpx'\''"
}'
```

---

# Dashboard

The Streamlit dashboard provides:

- Live pipeline execution
- Runtime exception analysis
- AI-generated patch preview
- Risk assessment
- Performance metrics
- JSON telemetry

---

# Roadmap

- Kubernetes Deployment
- Slack Notifications
- GitHub Actions Integration
- Security Review Agent
- Automated Test Generation
- Multi-language Patch Support

---

# License

MIT License

---

Built for the **AMD Developer Hackathon ACT II** using **Fireworks AI** and **Google DeepMind Gemma**.