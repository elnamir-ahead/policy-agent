"""Web search for the procurement agent. Supports Tavily (API key) or DuckDuckGo (free)."""

import os
from typing import List

SEARCH_ENABLED = os.environ.get("ENABLE_WEB_SEARCH", "0").lower() in ("1", "true", "yes")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")


def search_web(query: str, max_results: int = 5) -> List[dict]:
    """
    Search the web. Returns list of {title, url, snippet}.
    Uses Tavily if TAVILY_API_KEY is set, else DuckDuckGo (free).
    """
    if not query or not query.strip():
        return []

    query = query.strip()
    results = []

    # Try Tavily first (better quality for AI)
    if TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(query, max_results=max_results, search_depth="basic")
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", r.get("snippet", "")),
                })
            return results
        except Exception:
            pass  # Fall through to DuckDuckGo

    # Fallback: DuckDuckGo (free, no API key)
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("url", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                })
    except Exception:
        pass

    return results


def format_search_results(results: List[dict]) -> str:
    """Format search results for inclusion in the prompt."""
    if not results:
        return ""
    lines = ["## Web Search Results (use to supplement knowledge base when relevant):"]
    for i, r in enumerate(results, 1):
        lines.append(f"\n{i}. **{r.get('title', 'N/A')}**")
        lines.append(f"   URL: {r.get('url', '')}")
        lines.append(f"   {r.get('snippet', '')[:300]}...")
    return "\n".join(lines)
