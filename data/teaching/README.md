# Synthetic teaching data

Every row in this directory is fictional and independently simulated by `scripts/generate_teaching_data.py` with seed `20260827`. The generator does not read any external or private dataset.

Run the drift check with:

```powershell
uv run python scripts/generate_teaching_data.py --check
```

## Files

| File | Teaching role |
|---|---|
| `training_districts.geojson` | 25 polygon features, unique code `d`, and one duplicated display name |
| `district_production.csv` | Skewed district values for classification and mapping |
| `survey_points.csv` | Groups A to D and six intentionally repeated coordinate pairs |
| `lumen_2018_survey.csv` | Household attributes with leading-zero text IDs and documented special codes |
| `lumen_2018_test_results.csv` | One household per row and 23 possible member-test slots |
| `lumen_2018_reference_rates.csv` | Deterministic reference rates for generator validation |
| `lumen_2014.csv`, `noria_2015.csv`, `noria_2021.csv` | Three additional fictional survey waves |
| `synthetic_analysis_clean.csv` | Prepared four-wave repeated cross-section for regression lessons |
| `expected_outputs.json` | Deterministic counts and rates used by automated checks |
| `data_manifest.json` | Seed, row counts, and SHA-256 hashes |

Identifiers are strings. Blank values are intentional. The countries Lumen and Noria do not represent real places or populations.

## Versioned loading

Public notebooks use raw GitHub files under release `v1.0.1`. Local and CI runs can override the source:

```powershell
$env:LEARNING_LAB_DATA_BASE = "data/teaching"
$env:LEARNING_LAB_DATA_REF = "v1.0.1"
```

The data are dedicated under CC0 1.0. See `LICENSE` in this directory.
