"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path = PROJECT_ROOT / "data"
    output_dir: Path = PROJECT_ROOT / "output"
    api_key: str | None = None
    cloud_lab_url: str | None = None

    @property
    def database_path(self) -> Path:
        return self.data_dir / "superconductor_database.json"

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            data_dir=Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data")),
            output_dir=Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output")),
            api_key=os.getenv("SUPERCONDUCTOR_API_KEY"),
            cloud_lab_url=os.getenv("CLOUD_LAB_API_URL"),
        )
