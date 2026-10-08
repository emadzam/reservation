"""Backend configuration without a third-party dotenv dependency."""

import os
from pathlib import Path


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE lines only when the process has not set that key."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


load_local_env(Path(__file__).resolve().parents[1] / ".env")
GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-6-luna").strip()
