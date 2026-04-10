# ABOUTME: Loads and validates prompts.yaml and models.yaml configuration files.
# ABOUTME: Provides typed data structures for prompts, contestants, and judges.

from dataclasses import dataclass
from pathlib import Path

import yaml


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
