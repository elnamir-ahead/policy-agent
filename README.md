# Policy Knowledge Agent

24/7 Policy & Process Assistant — procurement policy knowledge base with evidence-backed answers, web search when needed, and artifact generation.

📐 **[Architecture & Pipeline Diagram](docs/ARCHITECTURE.md)** — design, tools, and flow  
📖 **[User Guide](docs/USER_GUIDE.md)** — how to use the agent

## Deploy to AWS

**Option 1: GitHub Actions** (recommended)

Push to `main` to deploy automatically. Configure secrets first — see [.github/DEPLOY_SETUP.md](.github/DEPLOY_SETUP.md).

**Option 2: Local deploy**

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

Share the output URL — no login required. See [DEPLOY.md](DEPLOY.md) for details.

## Quick Start: Test in Browser

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** (for frontend)
- **AWS credentials** configured (for Bedrock access)
- **Bedrock access** in `us-east-1` — enable Claude 3.5 Sonnet in the [Bedrock console](https://console.aws.amazon.com/bedrock/)

### 1. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 2. Start the frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

### 3. Open in browser

Go to **http://localhost:5173** and start chatting.

The frontend proxies `/api` to the backend at `localhost:8000`, so no CORS setup is needed.

---

## Demo Questions (5-Minute Script)

1. **"I need to buy a SaaS tool for my team — $18k/year. What do I do?"**  
   → Expects clarifying questions (data access, urgency) → recommended path → policy citations → checklist.

2. **"We want to use a new vendor. What paperwork is required?"**  
   → Supplier onboarding steps, required docs, approvers, SLAs.

3. **"Give me the SOW template and draft an email to procurement with the required intake details."**  
   → Template link, intake summary, email draft, citations.

---

## Project Structure

```
policy-agent/
├── backend/           # Python FastAPI + Bedrock agent
│   ├── app.py         # Local dev server
│   ├── agent.py       # Agent logic + Bedrock calls
│   ├── lambda_handler.py  # AWS Lambda entry point
│   └── data/          # Embedded knowledge base
├── frontend/          # React + Vite + Tailwind
├── infrastructure/    # Terraform (us-east-1)
│   ├── main.tf
│   ├── s3.tf
│   ├── dynamodb.tf
│   ├── lambda.tf
│   └── ...
└── knowledge-base/    # Source content (for reference)
```

---

## Deploy to AWS (Terraform)

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

Outputs:

- `lambda_function_url` — Chat API endpoint
- `s3_bucket_name` — Knowledge base bucket
- `dynamodb_table` — Conversations table

To use the deployed API from the frontend:

```bash
VITE_API_URL=https://<lambda-url> npm run dev
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (default: `/api` for local proxy) |
| `AWS_REGION` | AWS region (default: `us-east-1`) |
| `DYNAMODB_TABLE` | DynamoDB table (Lambda only) |
| `ENABLE_WEB_SEARCH` | Set to `1` to enable online search (uses DuckDuckGo by default) |
| `TAVILY_API_KEY` | Optional. Tavily API key for higher-quality search (free tier: 1000 credits/mo at [tavily.com](https://tavily.com)) |

---

## Architecture

- **Backend**: Python, Bedrock (Claude 3.5 Sonnet), embedded knowledge base
- **Frontend**: React, Vite, Tailwind
- **Infrastructure**: Terraform — S3, DynamoDB, Lambda, Lambda Function URL

The agent uses policy-aware logic (spend thresholds, approval matrix, escalation rules) and cites policy sections (POL-001, POL-002, etc.) in responses.

---

## Web Search (Optional)

Enable online search to supplement the knowledge base. **Search is conditional**:

- **Real-time queries** (date, time, weather): Search runs *first* — the KB doesn't have these.
- **Other queries**: Try KB first; if the agent indicates it doesn't know, search and retry.

```bash
export ENABLE_WEB_SEARCH=1
uvicorn app:app --reload --port 8000
```

- **DuckDuckGo** (default): Free, no API key. Uses `duckduckgo-search` package.
- **Tavily** (optional): Higher quality. Get a free API key at [tavily.com](https://app.tavily.com) (1000 credits/month), then:
  ```bash
  pip install tavily-python
  export TAVILY_API_KEY=tvly-your-key
  export ENABLE_WEB_SEARCH=1
  ```
