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
6. If the knowledge base doesn't contain the answer, say "I don't have that information in the knowledge base."
7. Never give contract advice, pricing commitments, or vendor recommendations beyond the preferred list.
8. Flag when Legal/Security/Finance reviews are required based on the escalation triggers.
9. When web search results are provided below, you may use them to supplement your answer. Cite sources by URL when using web results.
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


# Queries we know the KB won't have - search immediately (no two-step)
REALTIME_QUERY_PATTERNS = [
    "date today", "today's date", "current date", "what date", "what's the date",
    "what is the date", "what is today", "today date",
    "time now", "current time", "what time", "what's the time",
    "what is the time", "what time is it",
    "weather", "temperature",
]

# Phrases that indicate the agent doesn't have the answer (triggers web search retry)
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
]


def _is_realtime_query(query: str) -> bool:
    """Check if query is about real-time info the KB won't have."""
    lower = query.lower()
    return any(p in lower for p in REALTIME_QUERY_PATTERNS)


def _get_search_query(user_msg: str) -> str:
    """Get an effective search query (normalize for better results)."""
    lower = user_msg.lower()
    if any(p in lower for p in ["date", "today"]):
        return "current date today"
    if any(p in lower for p in ["time", "clock"]):
        return "current time now"
    if "weather" in lower or "temperature" in lower:
        return "current weather"
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
    Web search is conditional:
    - Real-time queries (date, time, weather): search FIRST (KB doesn't have these)
    - Other queries: try KB first, then search if agent indicates it doesn't know
    """
    last_user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

    # Step 1: Real-time info (date/time/weather)
    web_search_context = ""
    if last_user_msg and _is_realtime_query(last_user_msg):
        # Date/time: always inject from system (no search, no ENABLE_WEB_SEARCH needed)
        fallback = _get_realtime_fallback(last_user_msg)
        if fallback:
            web_search_context = fallback
        # Weather: needs web search
        elif SEARCH_ENABLED:
            search_results = search_web(_get_search_query(last_user_msg), max_results=5)
            if search_results:
                web_search_context = format_search_results(search_results)

    # Step 2: First LLM call (with web results if we pre-searched)
    system = build_knowledge_context(web_search_context=web_search_context)
    response_text, citations = invoke_bedrock(messages, system)

    # Step 3: If agent still doesn't know AND we didn't search yet, search and retry
    if SEARCH_ENABLED and not web_search_context and _indicates_need_web_search(response_text):
        if last_user_msg:
            search_results = search_web(last_user_msg, max_results=5)
            if search_results:
                web_search_context = format_search_results(search_results)
                system_with_web = build_knowledge_context(web_search_context=web_search_context)
                response_text, citations = invoke_bedrock(messages, system_with_web)

    # Check if we should add artifact (e.g., email draft)
    artifacts = []
    last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    if "draft" in last_user.lower() and ("email" in last_user.lower() or "intake" in last_user.lower()):
        # Agent should have included it in response; we could parse it
        pass

    return {
        "response": response_text,
        "citations": citations,
        "artifacts": artifacts,
    }
