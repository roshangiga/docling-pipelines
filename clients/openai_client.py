from __future__ import annotations

import os
from typing import List, Optional

from pydantic import BaseModel, Field

try:
    from openai import OpenAI  # >=1.0 style client
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class EnrichedChunk(BaseModel):
    title: Optional[str] = Field(None, description="Short title inferred for the chunk")
    summary: str = Field(..., description="1-3 sentence summary of the chunk")
    key_points: List[str] = Field(default_factory=list, description="Bullet points capturing salient details")
    enriched_text: str = Field(..., description="Context-augmented chunk suitable for embedding/search")


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not available. Please install 'openai'.")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def enrich_chunk(self, text: str, context: str = "") -> EnrichedChunk:
        # Prefer structured output via JSON schema if supported
        schema = {
            "name": "EnrichedChunk",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "enriched_text": {"type": "string"},
                },
                "required": ["summary", "enriched_text"],
                "additionalProperties": False,
            },
            "strict": True,
        }

        prompt = (
            "You enhance document chunks for search/embedding.\n"
            "Return a JSON object with fields: title (optional), summary (1-3 sentences), "
            "key_points (array of short bullets), enriched_text (context-augmented rewrite).\n\n"
            f"Context (optional):\n{context}\n\n"
            f"Chunk:\n{text}\n"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={
                    "type": "json_schema",
                    "json_schema": schema,
                },
                messages=[
                    {"role": "system", "content": "You return only valid JSON conforming to the schema."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = resp.choices[0].message.content  # type: ignore[attr-defined]
        except Exception:  # fallback: try a plain JSON response
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "Return ONLY JSON with keys title, summary, key_points, enriched_text."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = resp.choices[0].message.content  # type: ignore[attr-defined]

        # Parse into Pydantic model
        import json

        try:
            data = json.loads(content)
        except Exception:
            # If the model returned non-JSON, wrap as minimal structure
            data = {"summary": content.strip(), "enriched_text": content.strip(), "key_points": []}
        return EnrichedChunk.model_validate(data)
