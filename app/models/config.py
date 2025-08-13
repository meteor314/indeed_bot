from __future__ import annotations

from pathlib import Path
from typing import Optional, List

import yaml
from pydantic import BaseModel, Field, ValidationError


class SearchConfig(BaseModel):
    base_url: str = Field(..., description="Indeed search URL with query params")
    base_urls: Optional[List[str]] = Field(None, description="Optional list of Indeed search URLs; if provided, supersedes base_url")
    start: int = Field(0, description="Pagination start index")
    end: int = Field(100, description="Pagination end index (inclusive)")


class CamoufoxConfig(BaseModel):
    user_data_dir: str = Field(..., description="Directory for Camoufox user data")
    language: str = Field("us", description="Locale/country code, e.g. us, uk, fr")


class AppConfig(BaseModel):
    search: SearchConfig
    camoufox: CamoufoxConfig

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> "AppConfig":
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        try:
            return cls(**data)
        except ValidationError as e:
            # Re-raise with clearer context
            raise ValueError(f"Invalid configuration in {path} -> {e}") from e
