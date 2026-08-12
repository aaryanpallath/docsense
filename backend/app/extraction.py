import base64
import io
import json
import os
import re
from typing import Optional

import anthropic
from pypdf import PdfReader

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

EXTRACTION_SYSTEM_PROMPT = """You are a document data extraction assistant. You will be given the \
text or image of a receipt or invoice. Extract the following fields and respond with ONLY a single \
JSON object - no other text, no markdown code fences:

{
  "vendor": string or null,
  "date": string (YYYY-MM-DD if determinable, otherwise as printed) or null,
  "total_amount": number or null,
  "category": string or null (one of: "Meals", "Travel", "Office Supplies", "Software", \
"Utilities", "Other"),
  "line_items": array of objects, each with "description" (string), "quantity" (number or null), \
"unit_price" (number or null), "amount" (number or null)
}

If a field cannot be determined, use null (or an empty array for line_items). Respond with ONLY \
the JSON object."""


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def parse_extraction_response(raw: str) -> dict:
    """Pull a JSON object out of the model's response, tolerating markdown fences or stray text."""
    text = raw.strip()

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    elif not text.startswith("{"):
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    data = json.loads(text)

    return {
        "vendor": data.get("vendor"),
        "date": data.get("date"),
        "total_amount": _to_float(data.get("total_amount")),
        "category": data.get("category"),
        "line_items": data.get("line_items") or [],
    }


def extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_from_text(document_text: str) -> dict:
    client = _client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": document_text}],
    )
    raw = "".join(block.text for block in message.content if block.type == "text")
    return parse_extraction_response(raw)


def extract_from_image(image_bytes: bytes, media_type: str) -> dict:
    client = _client()
    encoded = base64.standard_b64encode(image_bytes).decode("utf-8")
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": encoded},
                    },
                    {"type": "text", "text": "Extract the fields from this document image."},
                ],
            }
        ],
    )
    raw = "".join(block.text for block in message.content if block.type == "text")
    return parse_extraction_response(raw)
