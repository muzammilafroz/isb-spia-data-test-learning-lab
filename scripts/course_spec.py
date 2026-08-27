"""Single source of truth for public, self-study quiz contracts."""

from __future__ import annotations


def question(
    question_id: str,
    variable: str,
    prompt: str,
    answer_type: str,
    answer,
    explanation: str,
    *,
    choices: list[dict[str, str]] | None = None,
    tolerance: dict[str, float] | None = None,
) -> dict:
    item = {
        "question_id": question_id,
        "variable": variable,
        "prompt": prompt,
        "type": answer_type,
        "answer": answer,
        "explanation": explanation,
    }
    if choices:
        item["choices"] = choices
    if tolerance:
        item["tolerance"] = tolerance
    return item


def choices(*values: tuple[str, str]) -> list[dict[str, str]]:
    return [{"value": value, "label": label} for value, label in values]


MODULES = [
    {
        "module_id": "module-01",
        "title": "Python and pandas foundations",
        "lesson": "01_python_pandas_foundations.ipynb",
        "test": "01_python_pandas_test.ipynb",
        "questions": [
            question("m1_q01", "m1_district_rows", "How many rows are in district_production.csv?", "integer", 25, "Each row represents one fictional district, so shape[0] is 25."),
            question("m1_q02", "m1_unique_codes", "How many unique values are in the district code column d?", "integer", 25, "All 25 district codes are unique. This is why d is a safe join key."),
            question("m1_q03", "m1_duplicated_name", "Which display name is deliberately used by two districts?", "normalized-string", "Riverbend", "Riverbend appears twice even though each district code is unique. Names are labels, not reliable keys."),
            question("m1_q04", "m1_groups", "Select every sampling group present in survey_points.csv.", "multi-select", ["A", "B", "C", "D"], "The file contains four groups: A, B, C, and D.", choices=choices(("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"))),
            question("m1_q05", "m1_group_a_count", "How many sampling points belong to group A?", "integer", 50, "value_counts() shows 50 group A points."),
            question("m1_q06", "m1_production_kind", "Which broad data type best describes the production column?", "multiple-choice", "integer", "The values are whole-number counts and pandas reads the column as an integer type.", choices=choices(("integer", "Integer"), ("floating", "Floating point"), ("text", "Text"), ("boolean", "Boolean"))),
            question("m1_q07", "m1_missing_production", "How many production values are missing?", "integer", 0, "isna().sum() returns zero for this complete teaching column."),
            question("m1_q08", "m1_merge_contract", "Which pandas merge validation contract should be used when both tables have one row per district code?", "multiple-choice", "one_to_one", "one_to_one asks pandas to fail if either table repeats a district code.", choices=choices(("one_to_one", "one_to_one"), ("one_to_many", "one_to_many"), ("many_to_one", "many_to_one"), ("many_to_many", "many_to_many"))),
        ],
    },
    {
        "module_id": "module-02",
        "title": "Geospatial validation and mapping",
        "lesson": "02_geospatial_validation_mapping.ipynb",
        "test": "02_geospatial_test.ipynb",
        "questions": [
            question("m2_q01", "m2_polygon_count", "How many district polygons are in the GeoJSON?", "integer", 25, "The GeoJSON contains one polygon feature for each of 25 district codes."),
            question("m2_q02", "m2_crs", "What coordinate reference system is assigned to the district GeoDataFrame?", "normalized-string", "EPSG:4326", "The GeoJSON uses longitude and latitude in EPSG:4326."),
            question("m2_q03", "m2_duplicated_rows", "How many point rows belong to a repeated longitude-latitude pair, counting both originals and repeats?", "integer", 12, "Six coordinate pairs occur twice, so 12 rows are members of duplicated pairs."),
            question("m2_q04", "m2_duplicated_pairs", "How many distinct longitude-latitude pairs are repeated?", "integer", 6, "Grouping by longitude and latitude reveals six coordinate pairs with a count above one."),
            question("m2_q05", "m2_group_d_count", "How many points belong to group D?", "integer", 5, "The synthetic design contains five group D points."),
            question("m2_q06", "m2_join_key", "Which field should join production to district geometry?", "normalized-string", "d", "The field d is unique in both tables. The display name is not unique."),
            question("m2_q07", "m2_classifier", "Which classification method is used for the skewed production map?", "multiple-choice", "fisher_jenks", "Fisher-Jenks chooses breaks that reduce within-class variation in this skewed teaching distribution.", choices=choices(("fisher_jenks", "Fisher-Jenks"), ("quantiles", "Quantiles"), ("equal_interval", "Equal intervals"), ("manual", "Unvalidated manual breaks"))),
            question("m2_q08", "m2_legend_strategy", "Where should a large legend be placed when it would cover district polygons?", "multiple-choice", "outside_reserved_space", "Reserved space outside the data axes keeps the map visible and the legend readable.", choices=choices(("outside_reserved_space", "In reserved space outside the map"), ("over_data", "On top of the polygons"), ("remove", "Remove the legend"), ("tiny", "Shrink it until unreadable"))),
        ],
    },
    {
        "module_id": "module-03",
        "title": "Household rates and reproducible cleaning",
        "lesson": "03_household_rates_cleaning.ipynb",
        "test": "03_household_rates_test.ipynb",
        "questions": [
            question("m3_q01", "m3_test_slots", "How many test-result slots are present in the wide file?", "integer", 23, "The columns test_01 through test_23 provide 23 possible member-test slots."),
            question("m3_q02", "m3_households", "How many household rows are in the test-result file?", "integer", 360, "There is one wide test row for each of 360 Lumen 2018 households."),
            question("m3_q03", "m3_zero_denominators", "How many households have no nonblank test result?", "integer", 52, "Fifty-two rows have zero observed results across all 23 slots."),
            question("m3_q04", "m3_valid_rates", "How many households have a defined positive rate?", "integer", 308, "A rate is defined only when the denominator is positive, leaving 308 households."),
            question("m3_q05", "m3_first_valid_id", "What is the first household ID with a defined rate? Keep all eight positions.", "normalized-string", "04000001", "Reading the ID as text preserves its leading zero. The first row has no tests, so 04000001 is first with a rate."),
            question("m3_q06", "m3_other_outcomes", "How many nonblank results are labelled inconclusive?", "integer", 3, "Three observed results are inconclusive. They belong in the main denominator because they are nonblank test outcomes."),
            question("m3_q07", "m3_merge_contract", "Which merge validation contract fits one survey row and one rate row per household ID?", "multiple-choice", "one_to_one", "Both sides should contain each normalized household ID at most once." , choices=choices(("one_to_one", "one_to_one"), ("one_to_many", "one_to_many"), ("many_to_one", "many_to_one"), ("many_to_many", "many_to_many"))),
            question("m3_q08", "m3_clean_rows", "How many rows are in the pooled clean analysis file?", "integer", 1268, "The clean repeated cross-section contains 1,268 household-wave observations."),
            question("m3_q09", "m3_poorwater_count", "How many pooled households are classified as using a poor water source?", "integer", 419, "The documented water-source rule marks 419 rows as poorwater equal to one."),
            question("m3_q10", "m3_zero_rate_rule", "How should a zero-denominator household rate be represented?", "multiple-choice", "missing", "Zero divided by zero is undefined. Missing preserves that fact, while zero would falsely claim an observed zero positive rate.", choices=choices(("missing", "Missing"), ("zero", "Zero"), ("one", "One"), ("drop_raw_row", "Delete the raw household row"))),
        ],
    },
    {
        "module_id": "module-04",
        "title": "Regression, fixed effects, and credibility",
        "lesson": "04_regression_fixed_effects.ipynb",
        "test": "04_regression_test.ipynb",
        "questions": [
            question("m4_q01", "m4_analysis_rows", "How many observations are in the pooled clean file before model-specific missing-value deletion?", "integer", 1268, "The pooled input has 1,268 rows before formula variables define a common model sample."),
            question("m4_q02", "m4_wave_count", "How many survey waves are represented?", "integer", 4, "There are four fictional country-year survey waves."),
            question("m4_q03", "m4_country_year_pairs", "How many observed country-year pairs are represented?", "integer", 4, "Each survey wave is one observed country-year pair in this synthetic repeated cross-section."),
            question("m4_q04", "m4_covariance", "Which heteroskedasticity-consistent covariance estimator is used when design fields are unavailable?", "multiple-choice", "HC1", "HC1 adjusts ordinary least-squares standard errors for heteroskedasticity. It does not recreate missing survey weights, strata, or clusters.", choices=choices(("HC1", "HC1"), ("nonrobust", "Nonrobust only"), ("cluster_psu", "Cluster by an unavailable PSU"), ("bootstrap_claim", "Claim design consistency without fields"))),
            question("m4_q05", "m4_claim_language", "Which word best describes the estimated wealth-malaria relationship in this observational exercise?", "multiple-choice", "association", "Without a causal design, random assignment, or defensible instrument, the coefficient is an association.", choices=choices(("association", "Association"), ("causal_effect", "Causal effect"), ("treatment_effect", "Randomized treatment effect"), ("proof", "Proof"))),
            question("m4_q06", "m4_adjusted_wealth_coefficient", "Fit the documented adjusted model. What is the wealth_index coefficient?", "float", -0.1557734269, "The adjusted HC1 model estimates about -0.1558. A one-unit higher synthetic wealth index is associated with a 0.156 lower positive-rate fraction, holding listed covariates fixed.", tolerance={"absolute": 0.001, "relative": 0.001}),
            question("m4_q07", "m4_coefficient_sign", "Is the adjusted wealth coefficient positive or negative?", "normalized-string", "negative", "The fitted coefficient is below zero in the synthetic data."),
            question("m4_q08", "m4_common_sample", "How many observations enter the adjusted model after formula-level missing-value deletion?", "integer", 1244, "Missing head-age values reduce the common regression sample to 1,244 observations."),
        ],
    },
    {
        "module_id": "module-05",
        "title": "Validation, reproducibility, and interview defense",
        "lesson": "05_validation_reproducibility_defense.ipynb",
        "test": "05_validation_test.ipynb",
        "questions": [
            question("m5_q01", "m5_synthetic_flag", "What is the value of synthetic_only in data_manifest.json?", "normalized-string", "true", "The manifest explicitly records that the teaching data are synthetic."),
            question("m5_q02", "m5_manifest_files", "How many generated teaching files are recorded in the manifest?", "integer", 11, "The manifest records the ten teaching datasets plus expected_outputs.json. The manifest does not hash itself."),
            question("m5_q03", "m5_fresh_kernel_reason", "Why execute a notebook from a fresh kernel?", "multiple-choice", "detect_hidden_state", "A fresh run detects cells that silently depend on variables or imports left over from an earlier interactive session.", choices=choices(("detect_hidden_state", "Detect hidden state and ordering dependencies"), ("change_answers", "Change inconvenient results"), ("skip_errors", "Skip cells that fail"), ("decorate", "Improve colors automatically"))),
            question("m5_q04", "m5_figure_check", "What is the strongest check after saving a figure?", "multiple-choice", "open_exact_file", "Open the exact saved file at its intended display size and inspect clipping, overlap, encoding, and readability.", choices=choices(("open_exact_file", "Open and inspect the exact saved file"), ("exists_only", "Check only that a path exists"), ("trust_code", "Assume plotting code guarantees readability"), ("check_name", "Read only the filename"))),
            question("m5_q05", "m5_hash_purpose", "What does a stored file hash help detect?", "multiple-choice", "byte_changes", "A cryptographic hash changes when the file bytes change, so it detects unexpected input drift.", choices=choices(("byte_changes", "Unexpected byte changes"), ("causality", "Causal identification"), ("missing_weights", "Unavailable survey weights"), ("plot_taste", "Whether a color is attractive"))),
            question("m5_q06", "m5_ai_disclosure", "Which AI disclosure is defensible?", "multiple-choice", "specific_verified", "A useful disclosure states what AI assisted with and what the author independently checked and remains responsible for.", choices=choices(("specific_verified", "Describe assistance and independent verification"), ("deny", "Deny assistance that occurred"), ("delegate", "Claim AI is responsible for errors"), ("vague", "Give a vague statement with no verification"))),
            question("m5_q07", "m5_data_structure", "What is the pooled four-wave dataset: a panel or a repeated cross-section?", "multiple-choice", "repeated_cross_section", "Different households are observed in each survey wave, so the pooled data are a repeated cross-section.", choices=choices(("repeated_cross_section", "Repeated cross-section"), ("household_panel", "Household panel"), ("time_series", "Single time series"), ("experiment", "Randomized experiment"))),
            question("m5_q08", "m5_interview_opening", "What should come first when defending an analytical decision?", "multiple-choice", "purpose_and_constraint", "Start with the analytical purpose and the actual data constraint, then explain the rule, validation, limitation, and alternatives.", choices=choices(("purpose_and_constraint", "Purpose and data constraint"), ("package_name", "A package name without context"), ("large_claim", "The largest possible claim"), ("apology", "An apology before the evidence"))),
        ],
    },
    {
        "module_id": "capstone",
        "title": "Integrated capstone",
        "lesson": None,
        "test": "06_capstone_test.ipynb",
        "questions": [
            question("cap_q01", "cap_point_count", "How many sampling-point rows are present?", "integer", 80, "The sampling-point file contains 80 rows."),
            question("cap_q02", "cap_maximum_production", "What is the largest district production value?", "integer", 24458, "The maximum synthetic production value is 24,458."),
            question("cap_q03", "cap_maximum_district_code", "Which district code d has that largest production value?", "integer", 25, "District code 25 contains the maximum production value."),
            question("cap_q04", "cap_valid_rate_households", "How many Lumen 2018 households have a defined positive rate?", "integer", 308, "Only households with at least one nonblank test outcome have a defined rate."),
            question("cap_q05", "cap_inconclusive_results", "How many observed test results are inconclusive?", "integer", 3, "Three nonblank slots contain the label inconclusive."),
            question("cap_q06", "cap_first_valid_rate", "What is the positive rate for household 04000001?", "float", 0.5, "The household has one positive result among two observed results, so its rate is 0.5.", tolerance={"absolute": 0.000001, "relative": 0.0}),
            question("cap_q07", "cap_pooled_rows", "How many household-wave rows are in the pooled clean file?", "integer", 1268, "The four synthetic waves contribute 1,268 rows after the undefined Lumen 2018 rates are excluded from this prepared analysis file."),
            question("cap_q08", "cap_poorwater_share", "What fraction of pooled households use a poor water source? Report a value from zero to one.", "float", 0.330441640379, "The mean of the zero-one poorwater indicator is about 0.33044.", tolerance={"absolute": 0.0001, "relative": 0.001}),
            question("cap_q09", "cap_unadjusted_wealth_coefficient", "In positive_rate ~ wealth_index, what is the wealth_index coefficient?", "float", -0.1502429673, "The unadjusted HC1 model estimates about -0.15024 on the synthetic data.", tolerance={"absolute": 0.001, "relative": 0.001}),
            question("cap_q10", "cap_fixed_effect", "Which fixed effect directly represents the four observed survey waves without redundant country and year dummy sets?", "multiple-choice", "survey_wave", "A survey-wave category directly identifies each observed country-year wave.", choices=choices(("survey_wave", "Survey-wave fixed effects"), ("household", "Household fixed effects for unrelated households"), ("country_plus_year", "Both full country and year sets despite rank redundancy"), ("none_claim", "No effects and no disclosure"))),
            question("cap_q11", "cap_result_language", "Which phrase is appropriate for the regression result?", "multiple-choice", "negatively_associated", "The observational design supports a negative association, not a causal impact claim.", choices=choices(("negatively_associated", "Negatively associated"), ("caused_reduction", "Caused a reduction"), ("proved", "Proved the mechanism"), ("randomized", "Estimated a randomized effect"))),
            question("cap_q12", "cap_missing_design_fields", "Select every survey-design field that is unavailable in this teaching setup and cannot be invented.", "multi-select", ["weights", "psu", "strata"], "Survey weights, primary sampling units, and strata are all unavailable. HC1 does not substitute for these design fields.", choices=choices(("weights", "Survey weights"), ("psu", "Primary sampling units"), ("strata", "Strata"), ("wealth", "The synthetic wealth index"))),
        ],
    },
]


QUIZ_SPEC = {
    "schema_version": 1,
    "pass_percent": 80,
    "explanation_policy": "Reveal after a pass or after the second completed attempt.",
    "modules": MODULES,
}
