from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class AIResponse:
    provider: str
    model: str
    text: str


class ProviderError(RuntimeError):
    pass


def _post_json(url: str, payload: dict, headers: dict[str, str], timeout: int = 45) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderError(str(exc)) from exc


def openai_compatible(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    api_key = os.environ.get("AEGISLOG_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("No API key found. Set AEGISLOG_API_KEY or OPENAI_API_KEY.")
    root = (base_url or os.environ.get("AEGISLOG_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    data = _post_json(
        f"{root}/chat/completions",
        {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
        {"Authorization": f"Bearer {api_key}"},
    )
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Provider returned an unexpected response shape") from exc
    return AIResponse("openai-compatible", model, text)


def ollama(prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    root = (base_url or os.environ.get("AEGISLOG_OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    data = _post_json(f"{root}/api/generate", {"model": model, "prompt": prompt, "stream": False}, {})
    text = data.get("response")
    if not isinstance(text, str):
        raise ProviderError("Ollama returned an unexpected response shape")
    return AIResponse("ollama", model, text)


def run_provider(provider: str, prompt: str, model: str, base_url: str | None = None) -> AIResponse:
    name = provider.strip().lower()
    if name in {"openai", "openai-compatible"}:
        return openai_compatible(prompt, model or "gpt-4.1-mini", base_url)
    if name == "ollama":
        return ollama(prompt, model or "llama3.2", base_url)
    raise ProviderError(f"Unsupported AI provider: {provider}")
