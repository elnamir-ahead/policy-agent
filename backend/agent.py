"""Procurement Policy Agent - Bedrock-powered RAG with tool logic."""

import json
import os
from datetime import datetime
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from data.knowledge import (
    ESCALATIONS,
    PROCUREMENT_POLICY,
    SPEND_THRESHOLDS,
    SUPPLIER_ONBOARDING,
    TEMPLATE_GUIDE,
)
from search import SEARCH_ENABLED, format_search_results, search_web

# Claude Sonnet 4.6 (active; Claude 3.5 Sonnet is legacy). Override with BEDROCK_MODEL env var.
BEDROCK_MODEL = os.environ.get("BEDROCK_MODEL", "us.anthropic.claude-sonnet-4-6")
BEDROCK_REGION = "us-east-1"

SYSTEM_PROMPT = """You are the Procurement Concierge, a 24/7 policy and process assistant. You help employees with procurement questions.

## Your Knowledge Base (cite section IDs when relevant):
{knowledge}

## Spend Threshold Matrix:
{thresholds}

## Escalation Triggers:
- Legal: Contract terms, MSA/SOW, Over $100k, Indemnification
- Security: PII/PHI data, Software integrations, Cloud services  
- Finance: Over $250k, Multi-year commitment, Payment terms > 30 days

## Rules:
1. Be helpdesk-concise. For complex flows, offer to explain step-by-step.
2. Always cite policy sections (e.g., POL-001, POL-002) when answering from the knowledge base.
3. For "how do I buy X for $Y" questions: ask 1-2 clarifying questions (data access? urgency?) before recommending the path.
4. When asked for templates: provide the template name, when to use it, mandatory fields, and link.
5. When asked to draft an email or intake summary: generate it with placeholders in [brackets].
6. If the knowledge base doesn't contain the answer and no web search results are provided, say "I don't have that information in the knowledge base."
7. Never give contract advice, pricing commitments, or vendor recommendations beyond the preferred list.
8. Flag when Legal/Security/Finance reviews are required based on the escalation triggers.
9. When web search results are provided below, use them to answer the user's question—including general or non-procurement questions (current events, general knowledge, etc.). Cite sources by URL. Do not deflect to procurement-only when search results are available; answer from the results.
10. When a "Current Date (system)" or "Current Time (system)" section is provided below, use that as today's date or current time and answer date/time questions directly (e.g. "Today is [date].").
11. When answering a question that is not mainly about procurement (e.g. current events, general knowledge), do not add a closing line like "Is there anything procurement-related I can help you with?"—just answer the question.
"""


def get_threshold_guidance(amount: float, category: str = "general") -> dict:
    """Get spend threshold guidance for a given amount."""
    for t in SPEND_THRESHOLDS:
        if t["max"] is None and amount >= t["min"]:
            return t
        if t["min"] <= amount < (t["max"] or float("inf")):
            return t
    return SPEND_THRESHOLDS[-1]


def get_escalation_flags(amount: float, has_data_access: bool, has_contract: bool) -> list[str]:
    """Determine which reviews are required."""
    flags = []
    if amount >= 100000 or has_contract:
        flags.append("Legal review")
    if has_data_access:
        flags.append("Security review")
    if amount >= 250000:
        flags.append("Finance review")
    return flags


def build_knowledge_context(web_search_context: str = "") -> str:
    """Build full knowledge context for the prompt."""
    thresholds_str = json.dumps(SPEND_THRESHOLDS, indent=2)
    base = SYSTEM_PROMPT.format(
        knowledge=PROCUREMENT_POLICY + "\n\n" + SUPPLIER_ONBOARDING + "\n\n" + TEMPLATE_GUIDE,
        thresholds=thresholds_str,
    )
    if web_search_context:
        base += "\n\n" + web_search_context
    return base


def invoke_bedrock(messages: list[dict], system: str):
    """Invoke Bedrock Claude with messages. Returns (response_text, citations)."""
    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

    # Format messages for Bedrock (content blocks require "type": "text")
    formatted = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "user":
            formatted.append({"role": "user", "content": [{"type": "text", "text": content}]})
        elif role == "assistant":
            formatted.append({"role": "assistant", "content": [{"type": "text", "text": content}]})

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "system": system,
        "messages": formatted,
    }

    try:
        response = client.invoke_model(
            modelId=BEDROCK_MODEL,
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())
        output = result["content"][0]["text"]
        citations = []  # Bedrock KB would provide these; we use policy refs in prompt
        return output, citations
    except ClientError as e:
        return f"Error calling Bedrock: {e.response['Error']['Message']}", []


# Only date/time: we inject from system (no search). All other questions → one LLM call, then search if it doesn't know.
REALTIME_QUERY_PATTERNS = [
    "date today", "today's date", "todays date", "current date", "what date", "what's the date",
    "what is the date", "what is today", "today date",
    "time now", "current time", "what time", "what's the time",
    "what is the time", "what time is it",
]

# Phrases that indicate the agent doesn't have the answer or didn't understand (triggers web search retry)
NEEDS_WEB_SEARCH_PHRASES = [
    "i don't have that information in the knowledge base",
    "i don't have that in the knowledge base",
    "not in the knowledge base",
    "knowledge base doesn't contain",
    "i'm unable to find that",
    "i cannot find that",
    "i don't have that information",
    "i don't have access to",
    "i'm not able to check",
    "i cannot check",
    "i'm not able to",
    "i can't check",
    "i don't have real-time",
    "not able to check real-time",
    # When agent doesn't understand — trigger search to try to find an answer
    "i'm not sure i understand",
    "i don't quite understand",
    "could you rephrase",
    "could you clarify",
    "can you rephrase",
    "unclear what you mean",
    "not sure what you're asking",
    "not sure what you mean",
    "don't have direct access",
    "outside my knowledge",
    # Answer is from training / might be outdated → run search to get current info
    "knowledge cutoff",
    "as of my knowledge",
    "check a live news source",
    "most current information",
    "recommend checking",
    "training data",
    "training cutoff",
]


def _is_realtime_query(query: str) -> bool:
    """Check if query is about real-time info the KB won't have."""
    lower = query.lower()
    return any(p in lower for p in REALTIME_QUERY_PATTERNS)


def _get_search_query(user_msg: str) -> str:
    """Search query for retry: use user message as-is (we don't predict question types)."""
    return user_msg


def _get_realtime_fallback(user_msg: str) -> str:
    """Fallback when search fails - inject date/time from system."""
    lower = user_msg.lower()
    now = datetime.now()
    if any(p in lower for p in ["date", "today"]):
        return f"## Current Date (system): {now.strftime('%A, %B %d, %Y')}"
    if any(p in lower for p in ["time", "clock"]):
        return f"## Current Time (system): {now.strftime('%I:%M %p %Z')}"
    return ""


def _indicates_need_web_search(response: str) -> bool:
    """Check if the response indicates the KB doesn't have the answer."""
    lower = response.lower().strip()
    return any(phrase in lower for phrase in NEEDS_WEB_SEARCH_PHRASES)


def chat(messages: list[dict], session_id: Optional[str] = None) -> dict:
    """
    Process a chat turn. Returns {response, citations, artifacts}.
    Flow: policy (RAG) always in context. Only date/time is pre-injected from system.
    For any other question we call the LLM once; if it indicates it doesn't know,
    we run web search and call the LLM again with search results (no keyword list).
    """
    last_user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

    # Extra context: only date/time from system (no keyword list). Everything else → LLM first, then search if it doesn't know.
    extra_context = ""
    if last_user_msg and _is_realtime_query(last_user_msg):
        extra_context = _get_realtime_fallback(last_user_msg) or ""

    # One LLM call: policy (RAG) + optional date/time. No pre-search based on keywords.
    system = build_knowledge_context(web_search_context=extra_context)
    response_text, citations = invoke_bedrock(messages, system)

    # If LLM indicated it doesn't know and we didn't search yet, add search and retry once
    if SEARCH_ENABLED and not extra_context and last_user_msg and _indicates_need_web_search(response_text):
        search_results = search_web(last_user_msg, max_results=5)
        if search_results:
            extra_context = format_search_results(search_results)
            system = build_knowledge_context(web_search_context=extra_context)
            response_text, citations = invoke_bedrock(messages, system)

    artifacts = []
    return {
        "response": response_text,
        "citations": citations,
        "artifacts": artifacts,
    }
