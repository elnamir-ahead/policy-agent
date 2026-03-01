# Procurement Policy Agent — Implementation Plan

## Executive Summary

A **Procurement Concierge** chatbot deployed on AWS that provides 24/7 first-line support for procurement policy and process questions. The system uses an **agentic RAG architecture** with Amazon Bedrock, Knowledge Bases, and serverless deployment for cost efficiency and scalability.

---

## 1. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (React SPA)                              │
│                    Hosted on S3 + CloudFront (CDN)                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (REST + WebSocket)                            │
│              /chat (REST) | /stream (WebSocket for streaming)                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    LAMBDA ORCHESTRATOR (Agent Controller)                         │
│  • Intent classification (triage / onboarding / templates)                       │
│  • Multi-turn conversation state (DynamoDB)                                      │
│  • Tool routing to specialized handlers                                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            ▼                           ▼                           ▼
┌───────────────────┐     ┌───────────────────────┐     ┌───────────────────────┐
│  BEDROCK AGENT    │     │  BEDROCK KNOWLEDGE     │     │  CUSTOM TOOLS          │
│  (Claude 3.5)     │     │  BASE (RAG)            │     │  • Spend threshold     │
│  • Reasoning      │     │  • Policy docs         │     │  • Approval matrix     │
│  • Tool use       │     │  • SOPs, templates     │     │  • Artifact generation │
│  • Citations      │     │  • OpenSearch vector   │     │  • Escalation logic    │
└───────────────────┘     └───────────────────────┘     └───────────────────────┘
            │                           │                           │
            └───────────────────────────┼───────────────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         S3 BUCKET (Knowledge Base Source)                         │
│  policies/ | sops/ | templates/ | approval-matrix/ | preferred-suppliers/         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

| Requirement | Solution |
|-------------|----------|
| **Evidence-first answers** | Bedrock Knowledge Base RAG + citation metadata in responses |
| **Policy-aware decisioning** | Custom tools (Lambda) that query spend thresholds + approval matrix |
| **Targeted follow-ups** | Agent with structured prompts + conversation state in DynamoDB |
| **Artifact generation** | Bedrock Agent with action groups for SOW/email/exception drafts |
| **Escalation & routing** | Tool that checks approval matrix → flags Legal/Security/Finance |
| **24/7, scalable** | Serverless (Lambda, API Gateway, S3) — no servers to manage |
| **Cost-efficient** | Pay-per-use; Bedrock on-demand pricing; OpenSearch Serverless |

---

## 2. AWS Services (Modern & Efficient)

| Service | Purpose |
|---------|---------|
| **Amazon Bedrock** | LLM (Claude 3.5 Sonnet) for reasoning, tool use, generation |
| **Bedrock Knowledge Base** | RAG over policy docs, SOPs, templates — with OpenSearch Serverless |
| **Bedrock Agents** | Orchestration, action groups (tools), prompt templates |
| **Lambda** | Agent controller, tool implementations, API handlers |
| **API Gateway (REST)** | `/chat`, `/stream` endpoints |
| **DynamoDB** | Conversation history, session state |
| **S3** | Knowledge base source, static frontend |
| **CloudFront** | CDN for frontend, low latency |
| **IAM** | Least-privilege access |
| **CloudWatch** | Logs, metrics, traces |

### Vector Store Choice: OpenSearch Serverless

- **Why**: Fully managed, auto-scaling, no cluster management
- **Alternative**: Aurora PostgreSQL if you already use RDS (slightly lower cost at scale)

---

## 3. Agentic Design (Without Risky Integrations)

### Agent Flow

1. **User asks question** → API Gateway → Lambda
2. **Lambda** loads session from DynamoDB, sends to Bedrock Agent
3. **Bedrock Agent**:
   - Queries Knowledge Base (RAG) for relevant policy chunks
   - Calls **action groups** (tools) when needed:
     - `get_spend_threshold_guidance` — category + amount → PO vs P-card vs sourcing
     - `get_supplier_onboarding_steps` — required docs, approvals, SLAs
     - `get_template_and_guidance` — SOW/MSA/NDA + when to use
     - `generate_artifact` — intake summary, RFQ email, exception request
     - `check_escalation` — Legal/Security/Finance flags
4. **Agent** returns response with **citations** (source chunks) + optional artifacts
5. **Lambda** saves turn to DynamoDB, streams/returns to user

### Red Lines (Guardrails)

- **No contract advice** — only process/template guidance
- **No pricing commitments** — only threshold/process rules
- **No vendor recommendations** — only preferred-supplier list lookup (mocked)
- **Strict grounding** — when KB is silent, agent says "I don't have that in the knowledge base" (configurable)

---

## 4. MVP Scope — 3 Demo Flows

| Flow | User Intent | Agent Behavior |
|------|-------------|----------------|
| **1. Buy Something Triage** | "I need to buy X for $Y" | Asks 1–2 questions (category, data access, urgency) → recommends PO vs P-card vs sourcing → cites policy → checklist + template links |
| **2. Supplier Onboarding** | "We want to use a new vendor" | Steps + required docs + approvers + SLA expectations → citations |
| **3. Templates & Artifacts** | "Give me SOW template and draft email" | Template link + intake summary + email draft + citations |

---

## 5. Minimum Content Set (Demo Knowledge Base)

| Content Type | Format | Purpose |
|--------------|--------|---------|
| Procurement policy | PDF/Word | Spend thresholds, approval rules, P-card limits |
| Process SOPs | PDF/Word | "How Procurement Works" consolidated guide |
| Approval matrix / RACI | CSV/JSON | Spend thresholds, approvers by category |
| Preferred suppliers | JSON | Mock list for demo |
| Template library | PDF/Word + metadata | SOW, MSA, NDA + "when to use" notes |

**Structure in S3:**

```
s3://procurement-kb-demo/
├── policies/
│   └── procurement-policy.pdf
├── sops/
│   └── how-procurement-works.pdf
├── approval-matrix/
│   └── spend-thresholds.json
├── preferred-suppliers/
│   └── preferred-suppliers.json
└── templates/
    ├── sow-template.docx
    ├── msa-template.docx
    └── template-guide.pdf
```

---

## 6. 5-Minute Demo Script (High-Confidence)

| # | User Says | Expected Assistant Behavior |
|---|-----------|-----------------------------|
| **1** | "I need to buy a SaaS tool for my team — $18k/year. What do I do?" | Asks: "Does it handle sensitive data? What's the urgency?" → Recommends path (likely PO under threshold) → Cites policy section → Checklist + template links |
| **2** | "We want to use a new vendor. What paperwork is required?" | Supplier onboarding steps + required docs (W-9, insurance, etc.) + who approves + SLA expectations + citations |
| **3** | "Give me the SOW template and draft an email to procurement with the required intake details." | SOW template link + intake summary + email draft + citations |

---

## 7. Tech Stack Summary

| Layer | Technology |
|-------|------------|
| **Frontend** | React + Vite, Tailwind CSS, streaming chat UI |
| **Backend** | Python 3.12 (Lambda) — boto3 for Bedrock |
| **Infrastructure** | AWS CDK (TypeScript) or Terraform |
| **LLM** | Claude 3.5 Sonnet (Bedrock) |
| **RAG** | Bedrock Knowledge Base + OpenSearch Serverless |
| **Deployment** | CI/CD via GitHub Actions → CDK deploy |

---

## 8. Implementation Phases

### Phase 1: Foundation (Days 1–2)
- Project structure, CDK/Terraform skeleton
- S3 bucket + sample knowledge base content (mock policies, SOPs, approval matrix)
- Bedrock Knowledge Base creation + sync
- Basic Lambda + API Gateway `/chat` endpoint

### Phase 2: Agent & RAG (Days 3–4)
- Bedrock Agent with Knowledge Base integration
- Action groups: spend threshold, supplier onboarding, template lookup
- Citation formatting in responses
- DynamoDB for conversation state

### Phase 3: Artifacts & Demo Flows (Days 5–6)
- Artifact generation (intake summary, email draft)
- Escalation check tool
- Refine prompts for 3 demo scenarios
- End-to-end testing of demo script

### Phase 4: Frontend & Deployment (Days 7–8)
- React chat UI with streaming
- CloudFront + S3 hosting
- CDK/Terraform full stack
- Documentation + runbook

---

## 9. Answers to Design Questions (Per Your Spec)

| Question | Answer |
|----------|--------|
| **Primary user** | Employee requesters (first-line); procurement team can use for reference |
| **Top 10 routine questions** | (1) Competitive bids for $X? (2) Onboard new supplier? (3) P-card for software? (4) SOW/MSA template + mandatory fields? (5) Approval for $X? (6) Urgent purchase process? (7) Preferred suppliers for category? (8) Exception request process? (9) RFQ process? (10) Contract renewal steps? |
| **3 workflows to demo** | Buy triage, Supplier onboarding, Templates & artifacts |
| **Spend threshold + RACI** | Yes — we'll create mock JSON for demo; you replace with real data |
| **Policies: global or regional?** | MVP: single global standard; architecture supports multi-tenant later |
| **Strict KB grounding?** | Yes — when KB silent, say "I don't have that" (configurable) |
| **Tone** | Helpdesk-concise with optional "explain like I'm new" for complex flows |
| **Red lines** | No contract advice, no pricing commitments, no vendor recommendations beyond preferred list |

---

## 10. Estimated Costs (Demo / Low Traffic)

| Service | Est. Monthly (Demo) |
|---------|---------------------|
| Bedrock (Claude 3.5) | ~$5–20 (100–500 requests) |
| OpenSearch Serverless | ~$50–100 (small index) |
| Lambda | < $1 |
| API Gateway | < $1 |
| S3 + CloudFront | < $5 |
| **Total** | **~$60–130/month** |

---

## 11. Deliverables

1. **Source code** — monorepo: `frontend/`, `backend/`, `infrastructure/`, `knowledge-base/`
2. **Infrastructure as Code** — CDK or Terraform
3. **Sample knowledge base** — mock policies, SOPs, approval matrix, templates
4. **Deployment guide** — AWS setup, env vars, runbook
5. **Demo script** — step-by-step for stakeholders

---

## Next Step

**Please review this plan and confirm:**
1. Approve architecture and tech choices?
2. Any changes to MVP scope or demo flows?
3. Prefer **CDK** (TypeScript) or **Terraform** for IaC?
4. Any specific AWS region?

Once approved, implementation will proceed in the phases outlined above.
