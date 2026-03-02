# Policy Knowledge Agent — User Guide

A walkthrough of how to use the Policy Knowledge Agent for procurement policy questions, process guidance, and general queries.

---

## Getting Started

### Accessing the Agent

1. **Open the app** — Use the shared URL (e.g. `https://d16rp4uhgi8oz0.cloudfront.net` or your organization’s link).
2. **No login required** — The agent is available 24/7 without an account.
3. **Start chatting** — Type your question in the input box and press **Send**, or click one of the suggested questions.

### The Interface

- **Header** — Shows "Policy Knowledge Agent" and its capabilities (policy knowledge base, answers with citations, web search when needed).
- **Chat area** — Your messages appear on the right (amber), the agent’s replies on the left (gray).
- **Input bar** — Type your question and click **Send** (or press Enter).

---

## What You Can Ask

### 1. Procurement Policy & Process

**Examples:**

- *"I need to buy a SaaS tool for my team — $18k/year. What do I do?"*
- *"We want to use a new vendor. What paperwork is required?"*
- *"What approvals do I need for a $50k purchase?"*
- *"What’s the SOW template and when do I use it?"*

**What to expect:**

- Step-by-step guidance based on your organization’s procurement policy.
- Policy citations (e.g. POL-001, POL-002).
- Spend thresholds and approval requirements.
- Escalation flags (Legal, Security, Finance) when relevant.

### 2. Templates & Artifacts

**Examples:**

- *"Give me the SOW template and draft an email to procurement with the required intake details."*
- *"What’s the intake form for new software purchases?"*

**What to expect:**

- Template names and when to use them.
- Mandatory fields and links.
- Draft emails or summaries with placeholders in [brackets].

### 3. Date & Time

**Examples:**

- *"What is the date today?"*
- *"What time is it?"*

**What to expect:**

- Current date or time from the system.
- No web search needed.

### 4. General Questions

**Examples:**

- *"Who is the US president?"*
- *"What’s the weather in New York?"*
- *"What’s the latest news on [topic]?"*

**What to expect:**

- If the agent doesn’t have the answer in its policy knowledge base, it may use web search to find current information.
- Answers can include citations to web sources.
- For very recent or fast-changing topics, it may suggest checking a news source.

---

## How to Use It Effectively

### Be Specific When You Can

- **Better:** *"I need to buy a SaaS tool for $18k/year. What approvals do I need?"*
- **Less helpful:** *"How do I buy something?"*

For spend-related questions, include the amount and category when possible.

### Use Follow-Up Questions

You can ask follow-ups in the same conversation:

1. *"What paperwork is required for a new vendor?"*
2. *"What’s the SLA for approval?"*
3. *"Can you draft the intake email?"*

The agent keeps context within the session.

### Click Suggested Questions

The **Try these** section shows example questions. Click one to populate the input and send it. Use these as starting points for similar questions.

### Expect Citations

Policy answers typically include references like **POL-001**, **POL-002**, or source URLs. Use these to verify or look up details in your official policy documents.

---

## What Happens Behind the Scenes

1. **Policy first** — Your question is answered using the embedded procurement policy knowledge base.
2. **Tools when needed** — For date/time, the agent uses the system clock. For other questions it doesn’t know, it may run a web search and answer from those results.
3. **One response** — You get a single reply per turn. If the agent needs to search, that happens before the reply is shown.

---

## Tips & Best Practices

| Do | Don’t |
|----|-------|
| Include dollar amounts for spend questions | Assume the agent has real-time access to your systems |
| Ask for templates by name or purpose | Share confidential or sensitive data in questions |
| Use follow-ups to go deeper | Expect contract or legal advice beyond policy guidance |
| Check citations for verification | Rely on it for vendor recommendations beyond the preferred list |

---

## Troubleshooting

**"Error: HTTP 403" or "Invalid response"**

- Refresh the page.
- If it persists, the deployment may be updating. Wait a few minutes and try again.

**"Request timed out"**

- The question may be complex. Try again or break it into smaller questions.

**Answer seems outdated**

- For current-events or general-knowledge questions, the agent may use web search. If it still seems old, try rephrasing or asking for "the latest" information.

**No answer or "I don't have that in the knowledge base"**

- The agent may not have that information. Try rephrasing or asking a more specific question.
- If web search is enabled, it may retry with search and provide an updated answer.

---

## Summary

The Policy Knowledge Agent is a 24/7 assistant for procurement policy and process. Use it for:

- **Policy questions** — Spend thresholds, approvals, escalations.
- **Process guidance** — Vendor onboarding, templates, intake forms.
- **General questions** — When enabled, it can use web search for current information.

Ask clearly, use follow-ups, and check citations when you need to verify against official policy.
