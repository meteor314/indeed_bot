from __future__ import annotations

import textwrap
import pytest

from app.models.config import AppConfig


def test_app_config_load_success():
    cfg = AppConfig.load()  # uses default config.yaml at project root
    assert isinstance(cfg.search.base_url, str) and cfg.search.base_url
    assert isinstance(cfg.search.start, int)
    assert isinstance(cfg.search.end, int)
    assert isinstance(cfg.camoufox.user_data_dir, str) and cfg.camoufox.user_data_dir
    assert isinstance(cfg.camoufox.language, str) and cfg.camoufox.language


def test_app_config_load_validation_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(textwrap.dedent(
        """
        search:
          base_url: 123                # invalid type
          start: "zero"               # invalid type
          end: true                    # invalid type
        camoufox:
          user_data_dir: 42            # invalid type
          language: ["us"]            # invalid type
        """
    ), encoding="utf-8")

    with pytest.raises(ValueError):
        AppConfig.load(bad)
