from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "teaching"


def test_expected_outputs_match_public_data():
    expected = json.loads((DATA / "expected_outputs.json").read_text(encoding="utf-8"))
    points = pd.read_csv(DATA / "survey_points.csv")
    clean = pd.read_csv(DATA / "synthetic_analysis_clean.csv")
    tests = pd.read_csv(DATA / "lumen_2018_test_results.csv", dtype={"hhid": "string"})
    slots = [column for column in tests if column.startswith("test_")]
    denominator = tests[slots].notna().sum(axis=1)
    assert len(points) == expected["sampling_point_count"]
    assert points.duplicated(["longitude", "latitude"], keep=False).sum() == expected["duplicated_coordinate_rows"]
    assert denominator.eq(0).sum() == expected["zero_denominator_households"]
    assert len(clean) == expected["clean_analysis_rows"]
    assert clean["poorwater"].mean() == pytest.approx(expected["poorwater_share"], abs=1e-12)
