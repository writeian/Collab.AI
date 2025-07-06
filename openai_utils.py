"""Helper functions for talking to OpenAI.

All OpenAI-specific logic lives here so the rest of the app stays clean.
"""
import os
from openai import OpenAI
from flask import current_app
from models import Message

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


def get_ai_response(
    chat,
    *,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=300,
):
    """Return the assistant's reply text for a given Chat row."""
    if not client:
        return "⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    messages_payload = [
        {"role": m.role, "content": m.content}
        for m in Message.query.filter_by(chat_id=chat.id)
        .order_by(Message.timestamp)
        .all()
    ]

    # Keep only the last 20 messages to cap cost
    messages_payload = messages_payload[-20:]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages_payload,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        current_app.logger.error("OpenAI API failure: %s", exc)
        return "⚠️ Sorry — I couldn't reach the AI service just now."
