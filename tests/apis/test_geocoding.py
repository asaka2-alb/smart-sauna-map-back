# -*- coding: utf-8 -*-
import pytest

from smart_sauna_map.api import app


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "新宿",
            {"status_code": 200, "response": {"lat": 35.6938253, "lng": 139.7033559}},
        )
    ],
)
def test_when_receive_200_response(mocker, input, expected):
    mocker.patch(
        "smart_sauna_map.geocoding.geocode",
        return_value=({"lat": 35.6938253, "lng": 139.7033559}),
    )
    response = app.test_client().post("/geocode", json={"query": input})

    assert response.status_code == expected["status_code"]
    assert response.get_json() == expected["response"]


@pytest.mark.parametrize(
    "input, expected",
    [("", {"status_code": 404, "response": None})],
)
def test_when_receive_404_response(mocker, input, expected):
    mocker.patch(
        "smart_sauna_map.geocoding.geocode",
        return_value=({"lat": None, "lng": None}),
    )
    response = app.test_client().post("/geocode", json={"query": input})

    assert response.status_code == expected["status_code"]
    assert response.get_json() == expected["response"]
