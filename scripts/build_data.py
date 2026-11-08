from __future__ import annotations

import csv
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(BASE_DIR, "schools.csv")

# Columns the site needs. A missing name means the CSV format changed.
REQUIRED = [
    "INST_NR",
    "INST_NAVN",
    "INST_ADR",
    "POSTNR",
    "POSTDISTRIKT",
    "TLF_NR",
    "E_MAIL",
    "WEB_ADR",
    "INST_TYPE_NR",
    "INST_TYPE_NAVN",
    "ADM_KOMMUNE_NAVN",
    "GEO_BREDDE_GRAD",
    "GEO_LAENGDE_GRAD",
]


def ensure_data_dir() -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as e:
        raise SystemExit(f"Cannot create {DATA_DIR}: {e}") from e


def parse_float(value: str) -> float | None:
    # CSV uses comma as decimal separator
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_csv_rows(csv_path: str) -> list[list[str]]:
    try:
        with open(csv_path, "r", encoding="utf-16-le", newline="") as f:
            return list(csv.reader(f, delimiter=";"))
    except OSError as e:
        raise SystemExit(f"Cannot read {csv_path}: {e}") from e


def build_artifacts(rows: list[list[str]]) -> dict:
    header = [name.strip() for name in rows[0]]
    missing = set(REQUIRED) - set(header)
    if missing:
        raise SystemExit(f"schools.csv header is missing columns: {sorted(missing)}")
    at = {name: header.index(name) for name in REQUIRED}

    def text(row: list[str], name: str) -> str | None:
        return row[at[name]].strip() or None

    schools: list[dict] = []
    inst_types_set = set()
    kommune_set = set()

    for row in rows[1:]:
        if len(row) < len(header):
            continue

        lat = parse_float(row[at["GEO_BREDDE_GRAD"]])
        lon = parse_float(row[at["GEO_LAENGDE_GRAD"]])
        if lat is None or lon is None:
            continue

        school = {
            "id": coerce_int(row[at["INST_NR"]]),
            "inst_navn": text(row, "INST_NAVN"),
            "geo_bredde_grad": lat,
            "geo_laengde_grad": lon,
            "inst_type_navn": text(row, "INST_TYPE_NAVN"),
            "adm_kommune_navn": text(row, "ADM_KOMMUNE_NAVN"),
            "inst_adr": text(row, "INST_ADR"),
            "postnr": text(row, "POSTNR"),
            "postdistrikt": text(row, "POSTDISTRIKT"),
            "tlf_nr": text(row, "TLF_NR"),
            "e_mail": text(row, "E_MAIL"),
            "web_adr": text(row, "WEB_ADR"),
        }
        schools.append(school)

        inst_type_nr = text(row, "INST_TYPE_NR")
        if inst_type_nr and school["inst_type_navn"]:
            inst_types_set.add((inst_type_nr, school["inst_type_navn"]))
        if school["adm_kommune_navn"]:
            kommune_set.add(school["adm_kommune_navn"])

    inst_types = [
        {"inst_type_nr": nr, "inst_type_navn": navn} for nr, navn in sorted(inst_types_set)
    ]

    return {
        "schools": schools,
        "inst_types": inst_types,
        "kommune_list": sorted(kommune_set),
    }


def coerce_int(value: str):
    value = (value or "").strip()
    try:
        return int(value)
    except ValueError:
        return value


def write_json(path: str, data) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError as e:
        raise SystemExit(f"Cannot write {path}: {e}") from e


def main() -> None:
    ensure_data_dir()
    artifacts = build_artifacts(read_csv_rows(CSV_PATH))

    # Empty output means the CSV format changed; never publish an empty map.
    if not artifacts["schools"]:
        raise SystemExit("No schools parsed from schools.csv - check the file encoding (utf-16-le)")

    write_json(os.path.join(DATA_DIR, "schools.json"), artifacts["schools"])
    write_json(os.path.join(DATA_DIR, "inst_types.json"), artifacts["inst_types"])
    write_json(os.path.join(DATA_DIR, "kommune_list.json"), artifacts["kommune_list"])

    print(f"Wrote {len(artifacts['schools'])} schools to data/schools.json")
    print(f"Wrote {len(artifacts['inst_types'])} inst types to data/inst_types.json")
    print(f"Wrote {len(artifacts['kommune_list'])} kommuner to data/kommune_list.json")


if __name__ == "__main__":
    main()
