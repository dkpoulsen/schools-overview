from build_data import build_artifacts

HEADER = [
    "HOVEDSKOLE_INST", "INST_NR", "INST_NAVN", "ENHEDSART", "INST_ADR", "POSTNR",
    "POSTDISTRIKT", "TLF_NR", "E_MAIL", "WEB_ADR", "INST_TYPE_NR", "INST_TYPE_NAVN",
    "INST_TYPE_GRUPPE", "UNDERV_NIV", "INST_LEDER", "CVR_NR", "KOMMUNE_NR",
    "ADM_KOMMUNE_NAVN", "BEL_KOMMUNE", "BEL_KOMMUNE_NAVN", "BEL_REGION", "REGION_NAVN",
    "EJER_KODE", "EJERKODE_NAVN", "P_NR", "VEJKODE", "GEO_BREDDE_GRAD", "GEO_LAENGDE_GRAD",
]


def row(**overrides):
    values = {
        "INST_NR": "101000",
        "INST_NAVN": "Test Skole",
        "INST_ADR": "Vej 1",
        "POSTNR": "1550",
        "POSTDISTRIKT": "København V",
        "WEB_ADR": "www.test.dk",
        "INST_TYPE_NR": "1012",
        "INST_TYPE_NAVN": "Folkeskoler",
        "ADM_KOMMUNE_NAVN": "Københavns Kommune",
        "GEO_BREDDE_GRAD": "55,6756275",
        "GEO_LAENGDE_GRAD": "12,56957768",
    }
    values.update(overrides)
    return [values.get(name, "") for name in HEADER]


def test_parses_school():
    artifacts = build_artifacts([HEADER, row()])

    assert artifacts["schools"] == [{
        "id": 101000,
        "inst_navn": "Test Skole",
        "geo_bredde_grad": 55.6756275,
        "geo_laengde_grad": 12.56957768,
        "inst_type_navn": "Folkeskoler",
        "adm_kommune_navn": "Københavns Kommune",
        "inst_adr": "Vej 1",
        "postnr": "1550",
        "postdistrikt": "København V",
        "tlf_nr": None,
        "e_mail": None,
        "web_adr": "www.test.dk",
    }]
    assert artifacts["inst_types"] == [{"inst_type_nr": "1012", "inst_type_navn": "Folkeskoler"}]
    assert artifacts["kommune_list"] == ["Københavns Kommune"]


def test_drops_rows_without_coordinates_or_fields():
    artifacts = build_artifacts([
        HEADER,
        row(GEO_BREDDE_GRAD=""),                    # no latitude
        row(INST_NR="101001", GEO_LAENGDE_GRAD="x"),  # no longitude
        row(INST_NR="101002")[:10],                 # too few columns
        row(INST_NR="101003", ADM_KOMMUNE_NAVN=""),  # no kommune
    ])

    assert [school["id"] for school in artifacts["schools"]] == [101003]
    assert artifacts["kommune_list"] == []


def test_rejects_changed_header():
    try:
        build_artifacts([["INST_NR"], row()])
    except SystemExit as e:
        assert "missing columns" in str(e)
    else:
        raise AssertionError("expected SystemExit for a changed CSV header")


if __name__ == "__main__":
    test_parses_school()
    test_drops_rows_without_coordinates_or_fields()
    test_rejects_changed_header()
    print("all tests passed")
