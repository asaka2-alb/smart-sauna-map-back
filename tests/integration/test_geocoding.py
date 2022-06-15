import pytest
from smart_sauna_map.api import app


@pytest.mark.parametrize(
    "query, expected_status, expected_res", [
        (
            "新宿", 200, {'lat': 35.6938253, 'lng': 139.7033559},
        ),
    ]
)
def test_normal(query, expected_status, expected_res):
    rv = app.test_client().post("/", json={"query": query})
    data = rv.get_json()
    for key in expected_res:
        assert rv.status_code == expected_status
        assert data[key] == expected_res[key]


@pytest.mark.parametrize(
    "query, expected_status, expected_res", [
        (
            "", 404, None,
        ),
    ]
)
def test_abnormal(query, expected_status, expected_res):
    rv = app.test_client().post("/", json={"query": query})
    data = rv.get_json()
    assert rv.status_code == expected_status
    assert data == expected_res
