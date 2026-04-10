# ABOUTME: Loads and validates prompts.yaml and models.yaml configuration files.
# ABOUTME: Provides typed data structures for prompts, contestants, and judges.

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GEMINI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "ollama": None,  # local, no key needed
}


@dataclass
class Prompt:
    id: str
    category: str
    prompt: str


@dataclass
class ModelsConfig:
    contestants: list[str]
    judges: list[str]


def load_prompts(path: Path) -> list[Prompt]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [Prompt(**p) for p in data["prompts"]]


def load_models(path: Path) -> ModelsConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return ModelsConfig(
        contestants=[m["model"] for m in data["contestants"]],
        judges=[m["model"] for m in data["judges"]],
    )


def has_api_key(model: str) -> bool:
    provider = model.split("/")[0] if "/" in model else model
    if provider not in PROVIDER_KEY_MAP:
        return False  # unknown provider, assume key is missing
    env_var = PROVIDER_KEY_MAP[provider]
    if env_var is None:
        return True  # no key needed (e.g., ollama)
    return bool(os.environ.get(env_var))


def filter_available_models(models: list[str]) -> tuple[list[str], list[str]]:
    available = [m for m in models if has_api_key(m)]
    skipped = [m for m in models if not has_api_key(m)]
    return available, skipped
