"""Lambda handler for Procurement Policy Agent chat API."""

import json
import os

from agent import chat


def handler(event, context):
    """Handle chat requests from API Gateway or Lambda Function URL."""
    # Support both API Gateway and Lambda Function URL formats
    body = event.get("body") or event
    if isinstance(body, str):
        body = json.loads(body)

    messages = body.get("messages", [])
    session_id = body.get("session_id", "default")

    if not messages:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "messages required"}),
        }

    try:
        result = chat(messages, session_id)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps(result),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
