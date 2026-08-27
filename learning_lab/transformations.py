from __future__ import annotations

import numpy as np
import pandas as pd

SURFACE_WATER_LABEL = (
    "river, dam, lake, pond, stream, canal or irrigation channel"
)
POOR_WATER_LABELS = {
    "unprotected well",
    "unprotected spring",
    "surface water",
    SURFACE_WATER_LABEL,
}


def normalize_hhid(values: pd.Series, name: str = "hhid") -> pd.Series:
    text = values.astype("string").str.strip()
    invalid = text.isna() | ~text.str.fullmatch(r"\d+", na=False)
    assert not invalid.any(), f"{name}: missing or nondigit identifier"
    assert text.str.len().le(8).all(), f"{name}: identifier wider than eight digits"
    assert text.is_unique, f"{name}: raw identifier is not unique"
    normalized = text.str.zfill(8)
    assert normalized.is_unique, f"{name}: normalization created a collision"
    return normalized


def construct_household_rates(test_results: pd.DataFrame) -> pd.DataFrame:
    test_columns = [column for column in test_results if column.startswith("test_")]
    assert len(test_columns) == 23, "expected 23 member-test slots"
    labels = test_results[test_columns].astype("string").apply(
        lambda column: column.str.strip().str.lower()
    )
    sampled = labels.notna().sum(axis=1)
    positive = labels.eq("positive").sum(axis=1)
    rates = pd.DataFrame(
        {
            "hhid_raw": test_results["hhid"].astype("string"),
            "hhid": normalize_hhid(test_results["hhid"], "test results"),
            "sampled_member_count": sampled,
            "positive_count": positive,
        }
    )
    rates["positive_rate"] = positive.div(sampled).where(sampled.gt(0))
    assert rates["positive_count"].le(rates["sampled_member_count"]).all()
    assert rates["positive_rate"].dropna().between(0, 1).all()
    return rates


def clean_analysis_fields(frame: pd.DataFrame) -> pd.DataFrame:
    clean = frame.copy()
    clean["wealth_index"] = pd.to_numeric(clean["wealth_raw"]) / 100_000
    raw_minutes = pd.to_numeric(clean["water_minutes_raw"], errors="coerce")
    clean["water_minutes"] = raw_minutes.mask(raw_minutes.eq(998))
    clean.loc[raw_minutes.eq(996), "water_minutes"] = 0
    raw_age = pd.to_numeric(clean["head_age_raw"], errors="coerce")
    clean["head_age"] = raw_age.mask(raw_age.eq(98) | ~raw_age.between(10, 97))
    clean["female_head"] = clean["head_sex"].str.strip().str.lower().eq("female").astype("Int64")
    labels = clean["water_source"].astype("string").str.strip().str.lower()
    clean["poorwater"] = labels.isin(POOR_WATER_LABELS).astype("Int64").mask(labels.isna())
    clean["bednets"] = pd.to_numeric(clean["bednets_raw"], errors="coerce").replace(-99, np.nan)
    clean["floor_material"] = clean["floor_material"].replace({"dirty": "dirt"})
    return clean
