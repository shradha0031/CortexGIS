"""Local LLM clients for CortexGIS planning."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class OllamaClient:
    """Minimal Ollama API client compatible with planner.generate() usage."""

    model: str = "llama3.1:8b"
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 60
    temperature: float = 0.2

    def generate(self, prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = Request(
            url=f"{self.base_url.rstrip('/')}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(f"Unable to reach Ollama at {self.base_url}: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        text = data.get("response", "") if isinstance(data, dict) else ""
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Ollama returned an empty response")
        return text

    def describe(self) -> str:
        return f"ollama:{self.model}"


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_local_llm_client_from_env() -> Optional[OllamaClient]:
    """Build a local LLM client from environment variables.

    Environment variables:
    - CORTEXGIS_USE_LOCAL_LLM: 1/0 (default: 1)
    - CORTEXGIS_LLM_PROVIDER: currently supports 'ollama' (default: ollama)
    - CORTEXGIS_LLM_MODEL: model tag (default: llama3.1:8b)
    - CORTEXGIS_LLM_BASE_URL: Ollama base URL (default: http://localhost:11434)
    - CORTEXGIS_LLM_TIMEOUT: request timeout in seconds (default: 60)
    - CORTEXGIS_LLM_TEMPERATURE: generation temperature (default: 0.2)
    """
    enabled = _is_truthy(os.getenv("CORTEXGIS_USE_LOCAL_LLM", "1"))
    if not enabled:
        return None

    provider = os.getenv("CORTEXGIS_LLM_PROVIDER", "ollama").strip().lower()
    if provider != "ollama":
        return None

    model = os.getenv("CORTEXGIS_LLM_MODEL", "llama3.1:8b").strip()
    base_url = os.getenv("CORTEXGIS_LLM_BASE_URL", "http://localhost:11434").strip()

    try:
        timeout_seconds = int(os.getenv("CORTEXGIS_LLM_TIMEOUT", "60"))
    except ValueError:
        timeout_seconds = 60

    try:
        temperature = float(os.getenv("CORTEXGIS_LLM_TEMPERATURE", "0.2"))
    except ValueError:
        temperature = 0.2

    return OllamaClient(
        model=model,
        base_url=base_url,
        timeout_seconds=max(5, timeout_seconds),
        temperature=temperature,
    )
