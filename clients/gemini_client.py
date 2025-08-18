from __future__ import annotations

import os
from typing import List, Optional

from pydantic import BaseModel, Field

try:
    # google-generativeai >= 0.7.0
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None  # type: ignore


class EnrichedChunk(BaseModel):
    title: Optional[str] = Field(None, description="Short title inferred for the chunk")
    summary: str = Field(..., description="1-3 sentence summary of the chunk")
    key_points: List[str] = Field(default_factory=list, description="Bullet points capturing salient details")
    enriched_text: str = Field(..., description="Context-augmented chunk suitable for embedding/search")


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash") -> None:
        if genai is None:
            raise RuntimeError("google-generativeai package not available. Please install 'google-generativeai'.")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(self.model_name)

    def enrich_chunk(self, text: str, context: str = "") -> EnrichedChunk:
        # We'll prompt for a strict JSON conforming to the Pydantic schema
        schema_desc = (
            "JSON keys: title (string, optional), summary (string, 1-3 sentences), "
            "key_points (array of strings), enriched_text (string)."
        )
        prompt = (
            "You enhance document chunks for search/embedding.\n"
            f"Return ONLY JSON with the following schema. {schema_desc}\n\n"
            f"Context (optional):\n{context}\n\n"
            f"Chunk:\n{text}\n"
        )
        # Try to get a JSON response
        response = self.model.generate_content(prompt)
        content = response.text or "{}"
        import json
        try:
            data = json.loads(content)
        except Exception:
            # Try with a rephrase asking explicitly for JSON if first attempt failed
            prompt2 = (
                "Return ONLY valid JSON with keys: title (optional), summary, key_points, enriched_text.\n\n"
                + prompt
            )
            response = self.model.generate_content(prompt2)
            content = response.text or "{}"
            try:
                data = json.loads(content)
            except Exception:
                data = {"summary": content.strip(), "enriched_text": content.strip(), "key_points": []}
        return EnrichedChunk.model_validate(data)
