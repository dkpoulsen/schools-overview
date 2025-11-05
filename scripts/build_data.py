import csv
import json
import os
from typing import Dict, List, Any


CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schools-overview" if os.path.basename(os.path.dirname(os.path.dirname(__file__))) != "schools-overview" else "", "schools.csv")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def resolve_csv_path() -> str:
    # Prefer repo-root schools.csv
    candidate = os.path.join(BASE_DIR, "schools.csv")
    if os.path.exists(candidate):
        return candidate
    # Fallback to adjacent path computation
    return CSV_PATH


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def parse_float(value: str) -> float:
    value = (value or "").strip()
    if not value:
        return None  # type: ignore
    # Replace comma decimal separator with dot
    value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None  # type: ignore


def coerce_int(value: str) -> Any:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value


def read_csv_rows(csv_path: str) -> List[List[str]]:
    with open(csv_path, "r", encoding="utf-16-le", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)
    return rows


def build_artifacts(rows: List[List[str]]) -> Dict[str, Any]:
    # Header indices based on CSV columns used in UI
    header = rows[0]
    # Create a mapping from header name to index for safer access
    header_to_idx = {name: i for i, name in enumerate(header)}

    def idx(name: str) -> int:
        return header_to_idx.get(name, -1)

    schools: List[Dict[str, Any]] = []
    inst_types_set = set()
    kommune_set = set()

    for row in rows[1:]:
        # Guard length
        if len(row) < 28:
            continue

        lat = parse_float(row[idx("GEO_BREDDE_GRAD")] if idx("GEO_BREDDE_GRAD") != -1 else row[26])
        lon = parse_float(row[idx("GEO_LAENGDE_GRAD")] if idx("GEO_LAENGDE_GRAD") != -1 else row[27])
        if lat is None or lon is None:
            continue

        inst_nr_raw = row[idx("INST_NR")] if idx("INST_NR") != -1 else row[1]
        school_id = coerce_int(inst_nr_raw)

        school: Dict[str, Any] = {
            "id": school_id,
            "inst_navn": (row[idx("INST_NAVN")] if idx("INST_NAVN") != -1 else row[2]).strip() or None,
            "geo_bredde_grad": lat,
            "geo_laengde_grad": lon,
            "inst_type_navn": (row[idx("INST_TYPE_NAVN")] if idx("INST_TYPE_NAVN") != -1 else row[11]).strip() or None,
            "adm_kommune_navn": (row[idx("ADM_KOMMUNE_NAVN")] if idx("ADM_KOMMUNE_NAVN") != -1 else row[17]).strip() or None,
            "inst_adr": (row[idx("INST_ADR")] if idx("INST_ADR") != -1 else row[4]).strip() or None,
            "postnr": (row[idx("POSTNR")] if idx("POSTNR") != -1 else row[5]).strip() or None,
            "postdistrikt": (row[idx("POSTDISTRIKT")] if idx("POSTDISTRIKT") != -1 else row[6]).strip() or None,
            "tlf_nr": (row[idx("TLF_NR")] if idx("TLF_NR") != -1 else row[7]).strip() or None,
            "e_mail": (row[idx("E_MAIL")] if idx("E_MAIL") != -1 else row[8]).strip() or None,
            "web_adr": (row[idx("WEB_ADR")] if idx("WEB_ADR") != -1 else row[9]).strip() or None,
        }

        schools.append(school)

        inst_type_nr_val = (row[idx("INST_TYPE_NR")] if idx("INST_TYPE_NR") != -1 else row[10]).strip() or None
        inst_type_navn_val = school["inst_type_navn"]
        if inst_type_nr_val and inst_type_navn_val:
            inst_types_set.add((inst_type_nr_val, inst_type_navn_val))

        kommune_val = school["adm_kommune_navn"]
        if kommune_val:
            kommune_set.add(kommune_val)

    inst_types = [
        {"inst_type_nr": nr, "inst_type_navn": navn} for nr, navn in sorted(inst_types_set, key=lambda x: (coerce_int(x[0]) if isinstance(coerce_int(x[0]), int) else x[0], x[1]))
    ]
    kommune_list = sorted(kommune_set)

    return {
        "schools": schools,
        "inst_types": inst_types,
        "kommune_list": kommune_list,
    }


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def main() -> None:
    ensure_data_dir()
    csv_path = resolve_csv_path()
    rows = read_csv_rows(csv_path)
    artifacts = build_artifacts(rows)

    write_json(os.path.join(DATA_DIR, "schools.json"), artifacts["schools"])
    write_json(os.path.join(DATA_DIR, "inst_types.json"), artifacts["inst_types"])
    write_json(os.path.join(DATA_DIR, "kommune_list.json"), artifacts["kommune_list"])

    print(f"Wrote {len(artifacts['schools'])} schools to data/schools.json")
    print(f"Wrote {len(artifacts['inst_types'])} inst types to data/inst_types.json")
    print(f"Wrote {len(artifacts['kommune_list'])} kommuner to data/kommune_list.json")


if __name__ == "__main__":
    main()


