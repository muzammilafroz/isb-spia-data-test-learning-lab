from __future__ import annotations

import pandas as pd
import pytest

from learning_lab.transformations import (
    SURFACE_WATER_LABEL,
    clean_analysis_fields,
    construct_household_rates,
    normalize_hhid,
)


def test_identifier_normalization_preserves_eight_positions():
    observed = normalize_hhid(pd.Series([" 4000001", "04000002"], dtype="string"))
    assert observed.tolist() == ["04000001", "04000002"]


def test_identifier_validation_rejects_nondigits():
    with pytest.raises(AssertionError, match="nondigit"):
        normalize_hhid(pd.Series(["04A00001"], dtype="string"))


def test_rate_denominator_counts_every_nonblank_result():
    row = {"hhid": "04000001"}
    row.update({f"test_{slot:02d}": None for slot in range(1, 24)})
    row.update({"test_01": "positive", "test_02": "negative", "test_03": "inconclusive"})
    rates = construct_household_rates(pd.DataFrame([row]))
    assert rates.loc[0, "sampled_member_count"] == 3
    assert rates.loc[0, "positive_count"] == 1
    assert rates.loc[0, "positive_rate"] == pytest.approx(1 / 3)


def test_zero_denominator_rate_is_missing():
    row = {"hhid": "04000001"}
    row.update({f"test_{slot:02d}": None for slot in range(1, 24)})
    rates = construct_household_rates(pd.DataFrame([row]))
    assert pd.isna(rates.loc[0, "positive_rate"])


def test_special_codes_are_cleaned_non_destructively():
    raw = pd.DataFrame(
        {
            "wealth_raw": [100_000],
            "water_minutes_raw": [996],
            "head_age_raw": [98],
            "head_sex": ["female"],
            "water_source": [SURFACE_WATER_LABEL],
            "bednets_raw": [-99],
            "floor_material": ["dirty"],
        }
    )
    clean = clean_analysis_fields(raw)
    assert raw.loc[0, "floor_material"] == "dirty"
    assert clean.loc[0, "wealth_index"] == 1
    assert clean.loc[0, "water_minutes"] == 0
    assert pd.isna(clean.loc[0, "head_age"])
    assert clean.loc[0, "poorwater"] == 1
    assert pd.isna(clean.loc[0, "bednets"])
    assert clean.loc[0, "floor_material"] == "dirt"
