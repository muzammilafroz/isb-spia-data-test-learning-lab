from __future__ import annotations

from pathlib import Path

import pytest

from learning_lab.io import get_data_url, read_teaching_csv, read_teaching_geojson


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "teaching"


def test_versioned_raw_url(monkeypatch):
    monkeypatch.delenv("LEARNING_LAB_DATA_BASE", raising=False)
    monkeypatch.delenv("LEARNING_LAB_DATA_REF", raising=False)
    assert get_data_url("survey_points.csv").endswith(
        "/v1.0.0/data/teaching/survey_points.csv"
    )


def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("LEARNING_LAB_DATA_BASE", str(DATA))
    frame = read_teaching_csv("district_production.csv")
    geography = read_teaching_geojson()
    assert len(frame) == 25
    assert len(geography) == 25
    assert geography.crs.to_string() == "EPSG:4326"


def test_filename_cannot_escape_data_directory():
    with pytest.raises(ValueError):
        get_data_url("../private.csv")
