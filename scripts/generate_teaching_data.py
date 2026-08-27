from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import tempfile
from pathlib import Path

SEED = 20260827
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "teaching"
SURFACE_WATER = "river, dam, lake, pond, stream, canal or irrigation channel"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def logistic(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def generate_geography(output: Path, rng: random.Random) -> None:
    features = []
    production_rows = []
    district_names = []
    for index in range(25):
        code = index + 1
        row, column = divmod(index, 5)
        x0, y0 = 30.0 + column, -1.5 + row
        name = "Riverbend" if code in {7, 18} else f"Training District {code:02d}"
        district_names.append(name)
        polygon = [[
            [x0, y0], [x0 + 0.92, y0], [x0 + 0.92, y0 + 0.92],
            [x0, y0 + 0.92], [x0, y0],
        ]]
        features.append(
            {
                "type": "Feature",
                "properties": {"d": code, "district_name": name},
                "geometry": {"type": "Polygon", "coordinates": polygon},
            }
        )
        production = max(0, round(120 + (code ** 2.15) * 24 + rng.randint(-90, 90)))
        production_rows.append({"d": code, "production": production})

    geojson = {"type": "FeatureCollection", "features": features}
    (output / "training_districts.geojson").write_text(
        json.dumps(geojson, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_csv(output / "district_production.csv", production_rows, ["d", "production"])

    group_sequence = ["A"] * 50 + ["B"] * 15 + ["C"] * 10 + ["D"] * 5
    point_rows = []
    original_positions = []
    for index, group in enumerate(group_sequence):
        if index >= 74:
            longitude, latitude = original_positions[index - 74]
        else:
            district_index = rng.randrange(25)
            row, column = divmod(district_index, 5)
            longitude = round(30.0 + column + rng.uniform(0.12, 0.80), 6)
            latitude = round(-1.5 + row + rng.uniform(0.12, 0.80), 6)
            original_positions.append((longitude, latitude))
        point_rows.append(
            {"point_id": f"P{index + 1:03d}", "latitude": latitude, "longitude": longitude, "group": group}
        )
    write_csv(
        output / "survey_points.csv",
        point_rows,
        ["point_id", "latitude", "longitude", "group"],
    )


SURVEY_FIELDS = [
    "hhid", "year", "country", "region", "wealth_raw", "water_source",
    "water_minutes_raw", "head_age_raw", "head_sex", "electricity",
    "floor_material", "wall_material", "bednets_raw", "positive_rate",
    "sampled_member_count",
]


def make_household(
    rng: random.Random,
    country: str,
    year: int,
    index: int,
    id_offset: int,
    with_rate: bool,
) -> tuple[dict, float]:
    wave_shift = {("Lumen", 2014): -0.20, ("Lumen", 2018): 0.05, ("Noria", 2015): -0.35, ("Noria", 2021): 0.20}[(country, year)]
    wealth = rng.gauss(wave_shift, 0.90)
    hhid = f"{id_offset + index:08d}"
    water_roll = rng.random() + 0.17 * wealth
    if water_roll < 0.18:
        water_source = SURFACE_WATER
    elif water_roll < 0.33:
        water_source = "unprotected well"
    elif water_roll < 0.56:
        water_source = "protected well"
    elif water_roll < 0.78:
        water_source = "public tap"
    else:
        water_source = "piped on premises"

    if index % 41 == 0:
        water_minutes: int | str = 998
    elif water_source == "piped on premises":
        water_minutes = 996
    elif index % 67 == 0:
        water_minutes = ""
    else:
        water_minutes = max(1, round(rng.gauss(31 - 5 * wealth, 13)))

    age = max(18, min(86, round(rng.gauss(46, 14))))
    if index % 89 == 0:
        age = 98
    elif index % 131 == 0:
        age = 7

    denominator = 1 + (index % 4)
    probability = logistic(-0.75 - 0.68 * wealth + (0.15 if country == "Noria" else 0))
    positives = sum(rng.random() < probability for _ in range(denominator))
    rate = positives / denominator if with_rate else ""
    row = {
        "hhid": f"   {hhid}" if country == "Lumen" and year == 2018 else hhid,
        "year": year,
        "country": country,
        "region": f"Region {1 + index % 4}",
        "wealth_raw": round(wealth * 100_000),
        "water_source": water_source,
        "water_minutes_raw": water_minutes,
        "head_age_raw": age,
        "head_sex": "female" if rng.random() < 0.12 else "male",
        "electricity": int(wealth + rng.gauss(0, 0.55) > 0.05),
        "floor_material": "dirty" if index % 113 == 0 else ("dirt" if wealth < -0.30 else "cement"),
        "wall_material": "natural" if wealth < -0.45 else "finished",
        "bednets_raw": -99 if index % 157 == 0 else max(0, round(rng.gauss(2.2, 1.0))),
        "positive_rate": f"{rate:.6f}" if rate != "" else "",
        "sampled_member_count": denominator if with_rate else "",
    }
    return row, wealth


def generate_surveys(output: Path, rng: random.Random) -> None:
    wave_specs = [
        ("Lumen", 2014, 320, 1_000_000, "lumen_2014.csv"),
        ("Noria", 2015, 300, 2_000_000, "noria_2015.csv"),
        ("Noria", 2021, 340, 3_000_000, "noria_2021.csv"),
    ]
    historical_rows = []
    for country, year, count, offset, filename in wave_specs:
        rows = [make_household(rng, country, year, index, offset, True)[0] for index in range(count)]
        historical_rows.extend(rows)
        write_csv(output / filename, rows, SURVEY_FIELDS)

    survey_2018 = []
    wealth_by_id = {}
    for index in range(360):
        row, wealth = make_household(rng, "Lumen", 2018, index, 4_000_000, False)
        survey_2018.append(row)
        wealth_by_id[row["hhid"].strip()] = wealth
    write_csv(output / "lumen_2018_survey.csv", survey_2018, SURVEY_FIELDS)

    test_fields = ["hhid", *[f"test_{slot:02d}" for slot in range(1, 24)]]
    test_rows = []
    reference_rows = []
    rate_rows_for_clean = []
    for index, survey_row in enumerate(survey_2018):
        clean_id = survey_row["hhid"].strip()
        wealth = wealth_by_id[clean_id]
        if index % 7 == 0:
            denominator = 0
        else:
            denominator = 1 + (index % 4)
        probability = logistic(-0.70 - 0.72 * wealth)
        outcomes = ["positive" if rng.random() < probability else "negative" for _ in range(denominator)]
        if index in {71, 142, 213} and outcomes:
            outcomes[-1] = "inconclusive"
        test_row = {field: "" for field in test_fields}
        test_row["hhid"] = clean_id
        for slot, outcome in enumerate(outcomes, start=1):
            test_row[f"test_{slot:02d}"] = outcome
        test_rows.append(test_row)
        if denominator:
            positive_count = sum(value == "positive" for value in outcomes)
            rate = positive_count / denominator
            reference_rows.append({"hhid": clean_id, "positive_rate": f"{rate:.6f}"})
            clean_row = dict(survey_row)
            clean_row["positive_rate"] = f"{rate:.6f}"
            clean_row["sampled_member_count"] = denominator
            rate_rows_for_clean.append(clean_row)

    write_csv(output / "lumen_2018_test_results.csv", test_rows, test_fields)
    write_csv(output / "lumen_2018_reference_rates.csv", reference_rows, ["hhid", "positive_rate"])

    combined = historical_rows + rate_rows_for_clean
    clean_fields = [
        "source_record_key", "survey_wave", "hhid", "year", "country", "region",
        "positive_rate", "sampled_member_count", "wealth_index", "water_source",
        "water_minutes", "head_age", "female_head", "electricity", "poorwater",
        "floor_material", "wall_material", "bednets",
    ]
    poor_labels = {"unprotected well", "unprotected spring", "surface water", SURFACE_WATER}
    clean_rows = []
    for source_index, row in enumerate(combined, start=1):
        raw_minutes = row["water_minutes_raw"]
        water_minutes = "" if raw_minutes in {"", 998} else (0 if raw_minutes == 996 else raw_minutes)
        raw_age = row["head_age_raw"]
        head_age = "" if raw_age == 98 or not 10 <= int(raw_age) <= 97 else raw_age
        source_file = f"{row['country'].lower()}_{row['year']}"
        clean_rows.append(
            {
                "source_record_key": f"{source_file}:{source_index}",
                "survey_wave": f"{row['country']} {row['year']}",
                "hhid": row["hhid"].strip().zfill(8),
                "year": row["year"],
                "country": row["country"],
                "region": row["region"],
                "positive_rate": row["positive_rate"],
                "sampled_member_count": row["sampled_member_count"],
                "wealth_index": f"{int(row['wealth_raw']) / 100_000:.6f}",
                "water_source": row["water_source"],
                "water_minutes": water_minutes,
                "head_age": head_age,
                "female_head": int(row["head_sex"] == "female"),
                "electricity": row["electricity"],
                "poorwater": int(row["water_source"].strip().lower() in poor_labels),
                "floor_material": "dirt" if row["floor_material"] == "dirty" else row["floor_material"],
                "wall_material": row["wall_material"],
                "bednets": "" if row["bednets_raw"] == -99 else row["bednets_raw"],
            }
        )
    write_csv(output / "synthetic_analysis_clean.csv", clean_rows, clean_fields)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_count(path: Path) -> int | None:
    if path.suffix != ".csv":
        return None
    with path.open(encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_expected_outputs(output: Path) -> None:
    production = read_rows(output / "district_production.csv")
    points = read_rows(output / "survey_points.csv")
    tests = read_rows(output / "lumen_2018_test_results.csv")
    clean = read_rows(output / "synthetic_analysis_clean.csv")
    references = read_rows(output / "lumen_2018_reference_rates.csv")

    maximum = max(production, key=lambda row: int(row["production"]))
    coordinate_counts: dict[tuple[str, str], int] = {}
    for row in points:
        coordinate = (row["longitude"], row["latitude"])
        coordinate_counts[coordinate] = coordinate_counts.get(coordinate, 0) + 1
    test_columns = [f"test_{slot:02d}" for slot in range(1, 24)]
    denominators = [sum(bool(row[column].strip()) for column in test_columns) for row in tests]
    inconclusive = sum(
        row[column].strip().lower() == "inconclusive"
        for row in tests
        for column in test_columns
    )
    poorwater_count = sum(int(row["poorwater"]) for row in clean)

    expected = {
        "schema_version": 1,
        "district_count": len(production),
        "maximum_production": int(maximum["production"]),
        "maximum_production_district_code": int(maximum["d"]),
        "sampling_point_count": len(points),
        "duplicated_coordinate_rows": sum(
            count for count in coordinate_counts.values() if count > 1
        ),
        "duplicated_coordinate_pairs": sum(
            count > 1 for count in coordinate_counts.values()
        ),
        "test_slot_count": len(test_columns),
        "tested_household_count": len(tests),
        "zero_denominator_households": sum(value == 0 for value in denominators),
        "valid_rate_households": sum(value > 0 for value in denominators),
        "inconclusive_test_results": inconclusive,
        "first_valid_household_id": references[0]["hhid"],
        "first_valid_positive_rate": float(references[0]["positive_rate"]),
        "clean_analysis_rows": len(clean),
        "poorwater_households": poorwater_count,
        "poorwater_share": round(poorwater_count / len(clean), 12),
    }
    (output / "expected_outputs.json").write_text(
        json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for path in output.iterdir():
        if path.is_file() and path.name not in {"LICENSE", "README.md"}:
            path.unlink()
    rng = random.Random(SEED)
    generate_geography(output, rng)
    generate_surveys(output, rng)
    write_expected_outputs(output)
    files = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name not in {"LICENSE", "README.md", "data_manifest.json"}:
            files.append({"file": path.name, "sha256": sha256(path), "rows": row_count(path)})
    manifest = {
        "schema_version": 1,
        "generator_seed": SEED,
        "synthetic_only": True,
        "files": files,
    }
    (output / "data_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="learning-lab-data-") as temporary:
        candidate = Path(temporary)
        build(candidate)
        expected_names = {path.name for path in candidate.iterdir()}
        actual_names = {
            path.name
            for path in DEFAULT_OUTPUT.iterdir()
            if path.name not in {"LICENSE", "README.md"}
        }
        if expected_names != actual_names:
            raise SystemExit(f"Generated file set differs: expected {expected_names}, found {actual_names}")
        differences = [name for name in sorted(expected_names) if (candidate / name).read_bytes() != (DEFAULT_OUTPUT / name).read_bytes()]
        if differences:
            raise SystemExit(f"Generated teaching data drifted: {differences}")
    print("Synthetic teaching data match the deterministic generator.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        build(DEFAULT_OUTPUT)
        print(f"Generated teaching data in {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()
