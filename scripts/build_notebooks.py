"""Build the public lesson and blank assessment notebooks."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat

from course_spec import MODULES, QUIZ_SPEC

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "muzammilafroz/applied-economics-data-learning-lab"
PAGES_ROOT = "https://muzammilafroz.github.io/applied-economics-data-learning-lab"


def markdown(source: str):
    return nbformat.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbformat.v4.new_code_cell(source.strip())


def notebook_header(title: str, filename: str, *, module_id: str | None) -> str:
    lite_path = f"lessons/{filename}" if module_id else f"tests/{filename}"
    repo_path = f"notebooks/{lite_path}"
    links = [
        f"[Run in browser]({PAGES_ROOT}/lab/index.html?path={lite_path})",
        f"[Open in Colab](https://colab.research.google.com/github/{REPOSITORY}/blob/main/{repo_path})",
        f"[Course home]({PAGES_ROOT}/)",
    ]
    if module_id:
        links.append(f"[Take the test]({PAGES_ROOT}/tests/?module={module_id})")
    return f"# {title}\n\n" + " | ".join(links) + "\n\n> This independent learning resource uses fictional, synthetic data. It is not an official assessment or credential."


BOOTSTRAP = r'''
from __future__ import annotations

import os
import sys
import types
from urllib.request import urlopen

if sys.platform == "emscripten":
    import piplite
    await piplite.install("pyodide-http")
    import pyodide_http
    pyodide_http.patch_all()

RAW_CODE_ROOT = "https://raw.githubusercontent.com/muzammilafroz/applied-economics-data-learning-lab/v1.0.1/learning_lab"
if sys.platform == "emscripten":
    from js import window
    if window.location.hostname in {"127.0.0.1", "localhost"}:
        RAW_CODE_ROOT = f"{window.location.origin}/learning_lab"
        os.environ["LEARNING_LAB_DATA_BASE"] = f"{window.location.origin}/data/teaching"

def load_public_module(module_name):
    """Import locally, or fetch the small public helper when running in Colab/Lite."""
    try:
        return __import__(f"learning_lab.{module_name}", fromlist=[module_name])
    except ModuleNotFoundError:
        location = f"{RAW_CODE_ROOT}/{module_name}.py"
        source = urlopen(location).read().decode("utf-8")
        module = types.ModuleType(f"learning_lab.{module_name}")
        exec(compile(source, location, "exec"), module.__dict__)
        return module

lab_io = load_public_module("io")
get_data_url = lab_io.get_data_url
read_teaching_csv = lab_io.read_teaching_csv
read_teaching_geojson = lab_io.read_teaching_geojson

print("Runtime:", sys.platform)
print("Data reference:", os.getenv("LEARNING_LAB_DATA_REF", "v1.0.1"))
'''


LESSON_1 = [
    ("markdown", """
## Why this lesson matters

Applied data work begins before any model or map. You need to know what an object contains, how rows and columns are selected, what missing values mean, and whether a proposed key is actually unique.

Prerequisites: none. You will learn imports, variables, types, indexing, masks, functions, assertions, and safe joins.
"""),
    ("code", BOOTSTRAP),
    ("code", """
import pandas as pd

production = read_teaching_csv("district_production.csv")
points = read_teaching_csv("survey_points.csv")

print("production shape:", production.shape)
print("points shape:", points.shape)
display(production.head())
"""),
    ("markdown", """
## Objects, names, and types

`production` is a variable. It points to a pandas `DataFrame`, which is a rectangular table. `shape` returns a tuple: `(number_of_rows, number_of_columns)`. `dtypes` reports how pandas represents each column.

An integer stores a whole number. A floating-point value can store a decimal approximation. A string stores text. A Boolean is `True` or `False`.
"""),
    ("code", """
print(type(production))
print(production.dtypes)

district_codes = production["d"]
print("One selected column is a", type(district_codes).__name__)
print("First three codes:", district_codes.iloc[:3].tolist())
"""),
    ("markdown", """
## Indexing and masks

Square brackets select a column. `.loc[row_rule, columns]` selects by labels and a Boolean rule. `.iloc` selects by numerical position. A mask is a sequence of `True` and `False` values that tells pandas which rows to keep.
"""),
    ("code", """
high_production = production["production"] > production["production"].median()
selected = production.loc[high_production, ["d", "production"]]

print("Rows above the median:", len(selected))
display(selected.head())
"""),
    ("markdown", """
## Nullable values and explicit checks

Missing is not the same as zero. `isna()` identifies missing values. An assertion turns an assumption into an executable contract. If the condition is false, Python stops with an `AssertionError` near the source of the problem.
"""),
    ("code", """
missing_by_column = production.isna().sum()
print(missing_by_column)

assert production["d"].notna().all(), "district code is missing"
assert production["d"].is_unique, "district code must be unique"
assert production["production"].ge(0).all(), "production cannot be negative"
print("All district-table contracts passed.")
"""),
    ("markdown", """
## Labels are not always keys

The GeoJSON deliberately contains two districts named `Riverbend`. A display name helps a reader, but it may be duplicated or edited. The code `d` is the stable, unique key.
"""),
    ("code", """
districts = read_teaching_geojson()
duplicate_names = districts.loc[
    districts["district_name"].duplicated(keep=False),
    ["d", "district_name"],
]
display(duplicate_names)

assert districts["d"].is_unique
assert not districts["district_name"].is_unique
"""),
    ("markdown", """
## A safe join

`merge` combines tables. `on="d"` names the shared key. `how="left"` keeps every district geometry. `validate="one_to_one"` requires each key to appear at most once on both sides. `indicator=True` records whether each row matched.
"""),
    ("code", """
district_data = districts.merge(
    production,
    on="d",
    how="left",
    validate="one_to_one",
    indicator=True,
)

print(district_data["_merge"].value_counts())
assert district_data["production"].notna().all()
district_data = district_data.drop(columns="_merge")
"""),
    ("markdown", """
## Functions package a rule

A function gives a meaningful name to reusable steps. Parameters are the inputs named in the definition. `return` sends a result back to the caller. Type hints document expected types but do not automatically enforce them.
"""),
    ("code", """
def count_rows_for_group(frame: pd.DataFrame, group: str) -> int:
    # Return the number of rows whose group exactly matches group.
    matches = frame["group"].eq(group)
    return int(matches.sum())

group_counts = {group: count_rows_for_group(points, group) for group in sorted(points["group"].unique())}
print(group_counts)
assert sum(group_counts.values()) == len(points)
"""),
    ("markdown", """
## Common failure: letting pandas guess an identifier

An identifier can look numeric while behaving like text. Arithmetic on a household ID is meaningless, and leading zeros can matter. Read such columns with `dtype={"hhid": "string"}`. This choice preserves the original representation before validation.

What would break if we skipped this? A value such as `04000001` could become `4000001`, and joins to a text key could fail.
"""),
    ("code", """
survey_preview = read_teaching_csv(
    "lumen_2018_survey.csv",
    dtype={"hhid": "string"},
    nrows=3,
)
print(survey_preview["hhid"].tolist())
print("Stripped lengths:", survey_preview["hhid"].str.strip().str.len().tolist())
"""),
    ("markdown", """
## Guided practice

Try these before the test:

1. Use `value_counts()` on the point group column.
2. Use `nunique()` to count district codes.
3. Change `validate="one_to_one"` to a deliberately wrong key in a copy of the code and read the error.

Self-check: Why is a failing assertion useful? It stops the workflow before an invalid assumption silently changes later results.

Next: open the module test. Its final cell creates a JSON answer bundle that can be pasted into the website form.
"""),
]


LESSON_2 = [
    ("markdown", """
## Why this lesson matters

A map is a data product, not decoration. Its key, coordinate system, classification, layer order, and legend can all change what a reader concludes.

Prerequisite: Lesson 1. You will validate geometry joins, preserve repeated coordinates, build Fisher-Jenks classes, and inspect a readable map.
"""),
    ("code", BOOTSTRAP),
    ("code", """
import geopandas as gpd
if sys.platform == "emscripten":
    await piplite.install("mapclassify")
import mapclassify
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

districts = read_teaching_geojson()
production = read_teaching_csv("district_production.csv")
points = read_teaching_csv("survey_points.csv")

print("Geometry types:", districts.geometry.geom_type.value_counts().to_dict())
print("CRS:", districts.crs)
"""),
    ("markdown", """
## Geometry and coordinate reference systems

A GeoDataFrame is a pandas table with a geometry column and a coordinate reference system, or CRS. EPSG:4326 stores longitude and latitude in angular degrees. It is suitable here for displaying the fictional teaching map. For accurate distance or area, reproject to an appropriate local projected CRS first.
"""),
    ("code", """
assert districts.crs.to_string() == "EPSG:4326"
assert districts.geometry.notna().all()
assert districts.geometry.is_valid.all()
assert districts["d"].is_unique
print("Geometry, CRS, and key checks passed.")
"""),
    ("markdown", """
## Join by the unique code

The name `Riverbend` occurs twice. Joining on that name would create an ambiguous many-to-many relationship. Joining on `d` preserves one geometry and one production value per district.
"""),
    ("code", """
mapped = districts.merge(production, on="d", validate="one_to_one")
assert len(mapped) == len(districts) == len(production)
assert mapped["production"].notna().all()

display(mapped.loc[mapped["district_name"].eq("Riverbend"), ["d", "district_name", "production"]])
"""),
    ("markdown", """
## Why Fisher-Jenks here

Production is deliberately skewed. Equal-width bins can crowd many districts into the lowest class. Quantiles put similar numbers of districts in each class but can separate nearly equal values. Fisher-Jenks searches for breaks that make values within each class relatively similar and classes relatively distinct.

This is a data-dependent descriptive choice, not a universal best method. Always report the classifier and inspect the break values.
"""),
    ("code", """
classifier = mapclassify.FisherJenks(mapped["production"], k=5)
mapped["production_class"] = classifier.yb

print("Class upper bounds:", classifier.bins.tolist())
print("Districts per class:", pd.Series(classifier.yb).value_counts().sort_index().to_dict())
assert len(classifier.bins) == 5
"""),
    ("markdown", """
## Repeated coordinates are information

Some point rows deliberately share exactly the same coordinates. That can represent multiple records at one site. Dropping duplicates would change group counts. Jittering the stored values would corrupt the data. We keep every row and diagnose overlap explicitly.
"""),
    ("code", """
coordinate_counts = (
    points.groupby(["longitude", "latitude"], as_index=False)
    .size()
    .sort_values("size", ascending=False)
)
repeated_pairs = coordinate_counts.loc[coordinate_counts["size"].gt(1)]
repeated_rows = points.duplicated(["longitude", "latitude"], keep=False)

display(repeated_pairs)
print("Rows belonging to repeated pairs:", int(repeated_rows.sum()))
assert points["point_id"].is_unique
"""),
    ("markdown", """
## Build the map in layers

The polygons form the base. Points are drawn afterward so they remain visible. A white edge separates districts. The legends occupy reserved space to the right, outside the data axes. Point coordinates remain unchanged.
"""),
    ("code", """
fig, ax = plt.subplots(figsize=(11, 6.2))
class_cmap = plt.get_cmap("YlOrBr", 5)
mapped.plot(
    column="production_class",
    categorical=True,
    cmap=class_cmap,
    linewidth=0.8,
    edgecolor="white",
    ax=ax,
)

markers = {"A": "o", "B": "s", "C": "^", "D": "X"}
colors = {"A": "#145DA0", "B": "#D1495B", "C": "#2A9D8F", "D": "#6A4C93"}
for group, group_points in points.groupby("group", sort=True):
    ax.scatter(
        group_points["longitude"],
        group_points["latitude"],
        label=f"Group {group} (n={len(group_points)})",
        marker=markers[group],
        color=colors[group],
        edgecolor="white",
        linewidth=0.5,
        s=40,
        alpha=0.85,
    )

handles, labels = ax.get_legend_handles_labels()
group_legend = ax.legend(handles, labels, title="Sampling groups", loc="upper left", bbox_to_anchor=(1.02, 0.48))
class_labels = [f"Up to {classifier.bins[0]:,.0f}"] + [
    f"{classifier.bins[index - 1] + 1:,.0f} to {classifier.bins[index]:,.0f}"
    for index in range(1, 5)
]
class_handles = [Patch(facecolor=class_cmap(index), edgecolor="white", label=label) for index, label in enumerate(class_labels)]
class_legend = ax.legend(class_handles, class_labels, title="Production classes", loc="upper left", bbox_to_anchor=(1.02, 1.0))
ax.add_artist(group_legend)
ax.set(title="Synthetic district production and sampling points", xlabel="Longitude", ylabel="Latitude")
ax.set_aspect("equal")
fig.subplots_adjust(right=0.68)
plt.show()
"""),
    ("markdown", """
## Visual validation checklist

After saving a figure, open the exact saved file. Check that every district is visible, symbols are distinguishable, legends do not cover data, labels are not clipped, colors have enough contrast, and the title says the data are synthetic.

Common failure: a plot can execute without error and still be unusable. File existence proves only that bytes were written.

Guided practice: compare `mapclassify.Quantiles` and `mapclassify.EqualInterval` on the same production column. Record how their break values and class counts differ. Then return to Fisher-Jenks for the module test.
"""),
]


LESSON_3 = [
    ("markdown", """
## Why this lesson matters

Household survey files often arrive in different shapes. One file may contain one household per row while another spreads member test results across many columns. A reproducible pipeline must define the denominator, protect identifiers, validate the merge, document special codes, and preserve provenance.

Prerequisite: Lesson 1. The data are fictional and independently simulated.
"""),
    ("code", BOOTSTRAP),
    ("code", """
import numpy as np
import pandas as pd

transformations = load_public_module("transformations")
normalize_hhid = transformations.normalize_hhid
construct_household_rates = transformations.construct_household_rates
clean_analysis_fields = transformations.clean_analysis_fields

survey = read_teaching_csv("lumen_2018_survey.csv", dtype={"hhid": "string"})
tests = read_teaching_csv("lumen_2018_test_results.csv", dtype={"hhid": "string"})
print("survey shape:", survey.shape)
print("test shape:", tests.shape)
"""),
    ("markdown", """
## Find the wide test slots by rule

The prefix `test_` defines the 23 member-result columns. Selecting them by a documented naming rule is safer than typing every column name by hand. The assertion prevents a silently incomplete denominator if a slot is renamed or omitted.
"""),
    ("code", """
test_columns = [column for column in tests.columns if column.startswith("test_")]
print(test_columns[:3], "...", test_columns[-3:])
assert len(test_columns) == 23, "expected exactly 23 test slots"
"""),
    ("markdown", """
## Define numerator and denominator before calculating

The main denominator is every nonblank observed result, including `inconclusive`. The numerator counts only `positive`. This answers: among people with any recorded test outcome, what fraction were positive?

Counting only positive and negative results would answer a different question and should be labelled as a sensitivity, not silently substituted.
"""),
    ("code", """
labels = tests[test_columns].astype("string").apply(
    lambda column: column.str.strip().str.lower()
)
sampled_member_count = labels.notna().sum(axis=1)
positive_count = labels.eq("positive").sum(axis=1)
positive_rate = positive_count.div(sampled_member_count).where(sampled_member_count.gt(0))

print("Observed outcome labels:", sorted(labels.stack().unique().tolist()))
print("Undefined rates:", int(positive_rate.isna().sum()))
assert positive_count.le(sampled_member_count).all()
assert positive_rate.dropna().between(0, 1).all()
"""),
    ("markdown", """
## Why zero denominators become missing

If no member has a recorded result, both numerator and denominator are zero. Writing a rate of zero would claim that the household was observed and had no positives. The honest value is missing because the rate is undefined.
"""),
    ("code", """
zero_denominator_preview = pd.DataFrame(
    {
        "hhid": tests["hhid"],
        "denominator": sampled_member_count,
        "numerator": positive_count,
        "rate": positive_rate,
    }
).loc[sampled_member_count.eq(0)].head()
display(zero_denominator_preview)
"""),
    ("markdown", """
## Preserve and normalize household IDs

An ID is text even when all its characters are digits. The helper strips surrounding spaces, rejects missing or nondigit values, rejects values longer than eight positions, checks uniqueness, and pads on the left with zeros. It also retains a raw copy before normalization.
"""),
    ("code", """
rates = construct_household_rates(tests)
survey = survey.assign(
    hhid_raw=survey["hhid"],
    hhid=normalize_hhid(survey["hhid"], "survey"),
)

display(rates.head(3))
print("First raw survey ID:", repr(survey.loc[0, "hhid_raw"]))
print("First normalized survey ID:", survey.loc[0, "hhid"])
"""),
    ("markdown", """
## Merge with an explicit contract

Both tables should have one row per normalized household ID. `validate="one_to_one"` turns that design claim into a check. The merge indicator lets us count unmatched rows before deciding what to do with them.
"""),
    ("code", """
merged = survey.merge(
    rates.drop(columns="hhid_raw"),
    on="hhid",
    how="left",
    validate="one_to_one",
    indicator=True,
    suffixes=("_survey", ""),
)

print(merged["_merge"].value_counts())
assert merged["_merge"].eq("both").all()
assert len(merged) == len(survey)
merged = merged.drop(columns="_merge")
"""),
    ("markdown", """
## Clean non-destructively

The cleaning function starts with `frame.copy()`. Raw columns remain available, while new analysis columns are added.

- `wealth_raw` is divided by 100,000 to create a readable index scale.
- Water code 996 means on premises and becomes zero minutes.
- Water code 998 means unknown and becomes missing.
- Age code 98 and implausible ages become missing.
- Bednet code -99 becomes missing.
- The long river, dam, lake, pond, stream, canal, or irrigation-channel label is classified as surface water.
- `dirty` is corrected to `dirt` without changing the source file.
"""),
    ("code", """
clean_2018 = clean_analysis_fields(merged)
columns_to_compare = [
    "wealth_raw", "wealth_index", "water_minutes_raw", "water_minutes",
    "head_age_raw", "head_age", "bednets_raw", "bednets",
]
display(clean_2018.loc[:8, columns_to_compare])

assert clean_2018["wealth_index"].notna().all()
assert clean_2018["poorwater"].dropna().isin([0, 1]).all()
"""),
    ("markdown", """
## Append waves into a repeated cross-section

`pd.concat` stacks rows that share a schema. These are different households sampled in different waves, so the result is a repeated cross-section, not a household panel. A `survey_wave` label identifies each country-year source.
"""),
    ("code", """
analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})
wave_counts = analysis["survey_wave"].value_counts().sort_index()
print(wave_counts)

assert analysis["source_record_key"].is_unique
assert analysis["positive_rate"].between(0, 1).all()
assert analysis["survey_wave"].nunique() == 4
"""),
    ("markdown", """
## Provenance and common failures

`source_record_key` records the source wave and a source-row sequence. Provenance makes it possible to trace a pooled row back to the fictional source file.

Common failures include reading IDs as numbers, filling undefined rates with zero, editing raw special codes in place, merging without cardinality validation, and calling repeated cross-sections a panel.

Guided practice: calculate a sensitivity rate that excludes `inconclusive` from the denominator. Compare it with the main rate only for affected households. Explain why the main denominator still answers the documented primary question.
"""),
]


LESSON_4 = [
    ("markdown", """
## Why this lesson matters

Regression summarizes conditional associations, but formula design and sample construction determine what was actually estimated. This lesson makes those choices visible.

Prerequisites: Lessons 1 and 3. You will use Patsy formula syntax and statsmodels, inspect rank redundancy, fit one common sample, use HC1 standard errors, and describe results without causal overreach.
"""),
    ("code", BOOTSTRAP),
    ("code", """
import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf

analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})
print("Rows before model-specific deletion:", len(analysis))
print(analysis["survey_wave"].value_counts().sort_index())
"""),
    ("markdown", """
## Formula syntax

In `outcome ~ predictor + control`, the left side is the outcome and the right side lists explanatory variables. `C(name)` tells Patsy to encode a categorical variable as indicator columns. One level is the reference category when an intercept is present.
"""),
    ("code", """
formula = "positive_rate ~ wealth_index + C(survey_wave) + head_age + female_head"
model_frame = analysis[[
    "positive_rate", "wealth_index", "survey_wave", "head_age", "female_head"
]].dropna()

print("Common sample rows:", len(model_frame))
print("Rows removed for a missing formula value:", len(analysis) - len(model_frame))
"""),
    ("markdown", """
## Why country and year effects are redundant here

The four waves occupy four specific country-year cells. Not every country appears in every year. With this pattern, a full set of survey-wave indicators already represents the observed cells. Adding full country and categorical-year sets creates exact linear dependence among columns.

Matrix rank is the number of linearly independent columns. If rank is below the number of columns, some coefficients cannot be separately identified.
"""),
    ("code", """
redundant = patsy.dmatrix(
    "C(survey_wave) + C(country) + C(year)",
    analysis,
    return_type="dataframe",
)
wave_only = patsy.dmatrix("C(survey_wave)", analysis, return_type="dataframe")

print("Redundant design: columns =", redundant.shape[1], "rank =", np.linalg.matrix_rank(redundant))
print("Wave design: columns =", wave_only.shape[1], "rank =", np.linalg.matrix_rank(wave_only))
assert np.linalg.matrix_rank(redundant) < redundant.shape[1]
assert np.linalg.matrix_rank(wave_only) == wave_only.shape[1]
"""),
    ("markdown", """
## Fit OLS with HC1 covariance

Ordinary least squares chooses coefficients that minimize squared residuals. `cov_type="HC1"` replaces the usual homoskedastic covariance estimate with a heteroskedasticity-consistent estimate and a finite-sample adjustment.

HC1 is useful here because the teaching files do not provide survey weights, primary sampling units, or strata. It is not a substitute for those unavailable design fields.
"""),
    ("code", """
adjusted = smf.ols(formula, data=model_frame).fit(cov_type="HC1")

coefficient = adjusted.params["wealth_index"]
standard_error = adjusted.bse["wealth_index"]
confidence_interval = adjusted.conf_int().loc["wealth_index"].tolist()

print("wealth coefficient:", round(coefficient, 6))
print("HC1 standard error:", round(standard_error, 6))
print("95% confidence interval:", [round(value, 6) for value in confidence_interval])
print("nobs:", int(adjusted.nobs))
"""),
    ("markdown", """
## Interpret scale and language

The outcome is a fraction from zero to one. `wealth_index` was scaled by 100,000, so a one-unit change is meaningful on the synthetic index scale. The coefficient is negative: conditional on the listed controls and wave indicators, a one-unit higher wealth index is associated with a lower positive-rate fraction.

Use `associated with`, not `caused`. Confounding, measurement, selection, and missing survey-design fields remain possible.
"""),
    ("code", """
coefficient_table = pd.DataFrame(
    {
        "term": adjusted.params.index,
        "estimate": adjusted.params.values,
        "HC1_standard_error": adjusted.bse.values,
        "p_value": adjusted.pvalues.values,
    }
)
display(coefficient_table)
"""),
    ("markdown", """
## Report all dummy levels

The coefficient table includes each estimable survey-wave indicator relative to the omitted reference wave. Hiding dummy rows makes the fitted specification harder to audit. A clear report names the reference category and explains that these indicators absorb average differences among waves.
"""),
    ("code", """
reference_wave = sorted(model_frame["survey_wave"].unique())[0]
dummy_rows = coefficient_table.loc[coefficient_table["term"].str.startswith("C(survey_wave)")]
print("Reference wave:", reference_wave)
display(dummy_rows)
"""),
    ("markdown", """
## Sensitivity checks

A sensitivity changes one defensible choice and asks whether the main conclusion is fragile. Here we compare an unadjusted model and a model with region indicators. All reported models use association language.
"""),
    ("code", """
unadjusted = smf.ols("positive_rate ~ wealth_index", data=analysis).fit(cov_type="HC1")
region_adjusted = smf.ols(
    "positive_rate ~ wealth_index + C(survey_wave) + C(region) + head_age + female_head",
    data=analysis,
).fit(cov_type="HC1")

comparison = pd.DataFrame(
    {
        "model": ["unadjusted", "wave and head controls", "plus region"],
        "wealth_coefficient": [
            unadjusted.params["wealth_index"],
            adjusted.params["wealth_index"],
            region_adjusted.params["wealth_index"],
        ],
        "nobs": [int(unadjusted.nobs), int(adjusted.nobs), int(region_adjusted.nobs)],
    }
)
display(comparison)
"""),
    ("markdown", """
## Common failure: mechanical controls

Electricity, floor material, and wall material help construct or closely reflect the simulated wealth index. Controlling for those mechanical components can remove the variation whose association you are trying to describe. Controls should follow an economic argument, not a request to include every available column.

Guided practice: write a two-sentence interview defense. Sentence one should name the estimand and controls. Sentence two should name the strongest limitation and use the word `association`.
"""),
]


LESSON_5 = [
    ("markdown", """
## Why this lesson matters

Good analysis is a chain of claims that another person can check. Reproducibility, artifact inspection, troubleshooting, and honest disclosure are part of the analysis, not chores added at the end.

Prerequisites: Lessons 1 through 4.
"""),
    ("code", BOOTSTRAP),
    ("code", """
import hashlib
import json
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

manifest_location = get_data_url("data_manifest.json")
expected_location = get_data_url("expected_outputs.json")

def read_json(location):
    if str(location).startswith(("http://", "https://")):
        return json.loads(urlopen(location).read().decode("utf-8"))
    return json.loads(Path(location).read_text(encoding="utf-8"))

manifest = read_json(manifest_location)
expected = read_json(expected_location)
print("Synthetic only:", manifest["synthetic_only"])
print("Generated files recorded:", len(manifest["files"]))
"""),
    ("markdown", """
## Fresh-kernel execution

Interactive notebooks remember variables from earlier cells. A cell may appear to work only because an old variable still exists. Restarting the kernel, clearing state, and running top to bottom tests whether the notebook contains every import and step it needs in the correct order.

A successful fresh run proves executability in that environment. It does not by itself prove that the analysis choices are valid.
"""),
    ("code", """
required_expected_keys = {
    "district_count", "sampling_point_count", "test_slot_count",
    "valid_rate_households", "clean_analysis_rows",
}
assert required_expected_keys.issubset(expected)
assert manifest["generator_seed"] == 20260827
assert manifest["synthetic_only"] is True
print("Manifest and expected-output schema checks passed.")
"""),
    ("markdown", """
## Hashes detect input drift

SHA-256 maps file bytes to a fixed-length fingerprint. If one byte changes, the fingerprint is overwhelmingly likely to change. A hash does not tell you whether a dataset is substantively correct, but it detects unexpected byte changes.
"""),
    ("code", """
production_location = get_data_url("district_production.csv")
if str(production_location).startswith(("http://", "https://")):
    production_bytes = urlopen(production_location).read()
else:
    production_bytes = Path(production_location).read_bytes()

observed_hash = hashlib.sha256(production_bytes).hexdigest()
recorded_hash = next(
    item["sha256"] for item in manifest["files"]
    if item["file"] == "district_production.csv"
)
assert observed_hash == recorded_hash
print("Production file hash matches the manifest.")
"""),
    ("markdown", """
## Inspect the exact saved artifact

The code below saves a small figure into a temporary directory, opens that exact PNG with Pillow, verifies its dimensions, and leaves no file behind after the context closes. Human visual review must still check clipping, overlap, contrast, and meaning.
"""),
    ("code", """
with tempfile.TemporaryDirectory(prefix="learning-lab-figure-") as folder:
    figure_path = Path(folder) / "validation_example.png"
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["Rows", "Valid rates"], [expected["clean_analysis_rows"], expected["valid_rate_households"]])
    ax.set(title="Synthetic validation counts", ylabel="Count")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=140)
    plt.show()
    plt.close(fig)

    with Image.open(figure_path) as saved:
        print("Saved format:", saved.format)
        print("Saved pixel size:", saved.size)
        assert saved.format == "PNG"
        assert saved.width >= 600 and saved.height >= 350
"""),
    ("markdown", """
## A validation loop

1. State the claim and expected unit.
2. Produce the number or artifact with code.
3. Check keys, ranges, row counts, hashes, and model samples.
4. Open rendered outputs and inspect them.
5. Record failures and corrections.
6. Re-run the affected check from clean state.

What would break if we skipped step 5? The final artifact might look correct, but a reviewer could not reconstruct how a defect was found and repaired.
"""),
    ("markdown", """
## Troubleshooting by symptom

| Symptom | Likely cause | First check |
|---|---|---|
| `ModuleNotFoundError` | Environment not synchronized | Confirm the intended kernel and dependencies |
| HTTP error | Wrong data ref or unpublished tag | Print `get_data_url()` and check the release |
| Merge error | Duplicate or malformed key | Inspect uniqueness and normalized IDs on both sides |
| Singular design | Redundant indicator columns | Compare matrix rank with column count |
| Different result after restart | Hidden notebook state | Run every cell top to bottom in a fresh kernel |
| Clipped legend | No reserved layout space | Open the exact image and adjust margins |
"""),
    ("markdown", """
## Honest AI disclosure

A defensible disclosure is specific: describe which tasks used AI assistance, identify the data and code checks you performed yourself, and accept responsibility for the final work. Do not deny assistance, transfer responsibility to a tool, or imply that generated text proves empirical accuracy.

Example: `AI assistance helped organize explanations and review code structure. I executed the notebooks, checked every reported value against generated artifacts, inspected the saved figures, and remain responsible for the analysis and its limitations.`
"""),
    ("markdown", """
## Interview defense pattern

Use five parts: purpose, data constraint, decision, validation, limitation. For example: `I joined on the unique district code because the display name was duplicated. I asserted uniqueness on both sides, used one-to-one merge validation, and checked that every geometry matched. A name join would be acceptable only after a separately audited crosswalk made names unique.`

Finish the module test, then take the capstone. The browser stores progress locally and can issue an unofficial local completion record after all six assessments are passed.
"""),
]


LESSONS = {
    "module-01": LESSON_1,
    "module-02": LESSON_2,
    "module-03": LESSON_3,
    "module-04": LESSON_4,
    "module-05": LESSON_5,
}


TEST_SETUPS = {
    "module-01": r'''
import pandas as pd

production = read_teaching_csv("district_production.csv")
points = read_teaching_csv("survey_points.csv")
districts = read_teaching_geojson()
print("Data loaded. Work from these three objects: production, points, districts.")
''',
    "module-02": r'''
import geopandas as gpd
if sys.platform == "emscripten":
    await piplite.install("mapclassify")
import mapclassify
import pandas as pd

districts = read_teaching_geojson()
production = read_teaching_csv("district_production.csv")
points = read_teaching_csv("survey_points.csv")
print("Geospatial teaching data loaded.")
''',
    "module-03": r'''
import numpy as np
import pandas as pd

transformations = load_public_module("transformations")
tests = read_teaching_csv("lumen_2018_test_results.csv", dtype={"hhid": "string"})
survey = read_teaching_csv("lumen_2018_survey.csv", dtype={"hhid": "string"})
analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})
print("Household teaching data loaded.")
''',
    "module-04": r'''
import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf

analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})
print("Regression teaching data loaded.")
''',
    "module-05": r'''
import json
from pathlib import Path

def read_json_file(filename):
    location = get_data_url(filename)
    if str(location).startswith(("http://", "https://")):
        return json.loads(urlopen(location).read().decode("utf-8"))
    return json.loads(Path(location).read_text(encoding="utf-8"))

manifest = read_json_file("data_manifest.json")
expected = read_json_file("expected_outputs.json")
print("Validation metadata loaded.")
''',
    "capstone": r'''
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

production = read_teaching_csv("district_production.csv")
points = read_teaching_csv("survey_points.csv")
tests = read_teaching_csv("lumen_2018_test_results.csv", dtype={"hhid": "string"})
analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})
print("Capstone data loaded.")
''',
}


def make_notebook(cells, original_path: Path):
    original = nbformat.read(original_path, as_version=4)
    notebook = nbformat.v4.new_notebook(cells=cells, metadata=original.metadata)
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata["language_info"] = {"name": "python", "version": "3.12"}
    return notebook


def write_lesson(module: dict) -> None:
    filename = module["lesson"]
    path = ROOT / "notebooks" / "lessons" / filename
    cells = [markdown(notebook_header(module["title"], filename, module_id=module["module_id"]))]
    for cell_type, source in LESSONS[module["module_id"]]:
        cells.append(markdown(source) if cell_type == "markdown" else code(source))
    notebook = make_notebook(cells, path)
    nbformat.write(notebook, path)


def choices_markdown(item: dict) -> str:
    if "choices" not in item:
        return ""
    return "\n\n" + "\n".join(
        f"- `{choice['value']}`: {choice['label']}" for choice in item["choices"]
    )


def answer_scaffold(item: dict) -> str:
    if item["type"] == "multi-select":
        hint = "# Assign a list of selected choice values, for example: ['value_a', 'value_b']"
    elif item["type"] == "multiple-choice":
        hint = "# Assign one choice value as a string."
    elif item["type"] == "normalized-string":
        hint = "# Assign a text answer. Capitalization and surrounding spaces are ignored by the web form."
    elif item["type"] == "float":
        hint = "# Assign a numeric value. The web form uses the tolerance stated in its feedback."
    else:
        hint = "# Assign one whole-number answer."
    return f"# TODO: write your code above the assignment.\n{hint}\n{item['variable']} = None\n{item['variable']}"


def answer_bundle_source(module: dict) -> str:
    lines = [
        "import json",
        "",
        "def json_ready(value):",
        "    if hasattr(value, 'item'):",
        "        return value.item()",
        "    if isinstance(value, set):",
        "        return sorted(value)",
        "    return value",
        "",
        "answer_bundle = {",
        "    'schema_version': 1,",
        f"    'module_id': '{module['module_id']}',",
        "    'answers': {",
    ]
    lines.extend(
        f"        '{item['question_id']}': json_ready({item['variable']}),"
        for item in module["questions"]
    )
    lines.extend(
        [
            "    },",
            "}",
            "print(json.dumps(answer_bundle, indent=2, sort_keys=True))",
        ]
    )
    return "\n".join(lines)


def write_test(module: dict) -> None:
    filename = module["test"]
    path = ROOT / "notebooks" / "tests" / filename
    title = module["title"] if module["module_id"] == "capstone" else f"Test: {module['title']}"
    cells = [
        markdown(notebook_header(title, filename, module_id=None)),
        markdown(
            """
## Instructions

Run the setup cells, then write your own code in each blank answer cell. Keep every named answer variable because the final cell uses those names to create copyable JSON.

The test is formative. The website requires 80 percent to pass, allows unlimited attempts, and reveals full explanations after a pass or after the second completed attempt. Browser answers and progress remain in local storage. Client-side answer keys are inspectable, so this is not secure certification.
"""
        ),
        code(BOOTSTRAP),
        code(TEST_SETUPS[module["module_id"]]),
    ]
    for number, item in enumerate(module["questions"], start=1):
        prompt = (
            f"## Question {number}\n\n"
            f"Question ID: `{item['question_id']}`\n\n"
            f"{item['prompt']}"
            f"{choices_markdown(item)}"
        )
        cells.extend([markdown(prompt), code(answer_scaffold(item))])
    cells.extend(
        [
            markdown(
                f"""
## Create your answer bundle

Run the next cell after filling every answer variable. Copy the printed JSON, open the [local test form]({PAGES_ROOT}/tests/?module={module['module_id']}), and use **Paste notebook bundle**. This cell does not grade or transmit your work.
"""
            ),
            code(answer_bundle_source(module)),
        ]
    )
    notebook = make_notebook(cells, path)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.execution_count = None
            cell.outputs = []
    nbformat.write(notebook, path)


def write_runtime_smoke() -> None:
    path = ROOT / "notebooks" / "_ci" / "runtime_smoke.ipynb"
    cells = [
        markdown(
            """
# Browser runtime smoke check

This compact technical notebook is used by automated browser checks. It confirms that JupyterLite can load the shared helper, public synthetic data, GeoPandas, mapclassify, and statsmodels. It is not a lesson or assessment.
"""
        ),
        code(BOOTSTRAP),
        code(
            """
import pandas as pd
import geopandas as gpd
if sys.platform == "emscripten":
    await piplite.install("mapclassify")
import mapclassify
import statsmodels.formula.api as smf

districts = read_teaching_geojson()
production = read_teaching_csv("district_production.csv")
analysis = read_teaching_csv("synthetic_analysis_clean.csv", dtype={"hhid": "string"})

mapped = districts.merge(production, on="d", validate="one_to_one")
classifier = mapclassify.FisherJenks(mapped["production"], k=5)
model = smf.ols("positive_rate ~ wealth_index", data=analysis).fit(cov_type="HC1")

assert len(mapped) == 25
assert len(classifier.bins) == 5
assert model.params["wealth_index"] < 0
print("JUPYTERLITE_SMOKE_OK", len(mapped), len(classifier.bins), round(model.params["wealth_index"], 6))
"""
        ),
    ]
    notebook = make_notebook(cells, path)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.execution_count = None
            cell.outputs = []
    nbformat.write(notebook, path)


def main() -> None:
    for module in MODULES:
        if module["lesson"]:
            write_lesson(module)
        write_test(module)
    write_runtime_smoke()

    quiz_path = ROOT / "web" / "assets" / "quiz-spec.v1.json"
    quiz_path.parent.mkdir(parents=True, exist_ok=True)
    quiz_path.write_text(
        json.dumps(QUIZ_SPEC, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("Built 5 lessons, 6 blank tests, 1 browser smoke notebook, and quiz spec v1.")


if __name__ == "__main__":
    main()
