# -*- coding: utf-8 -*-

import json

import pytest
import requests
from requests.exceptions import HTTPError

from smart_sauna_map.search_sauna import search_sauna
from smart_sauna_map.searcher.abstract_searcher import AbstractSearcher
from smart_sauna_map.searcher.google_map_searcher import GoogleMapSearcher


def mock_sauna_response(filename) -> list[dict]:
    with open(f"./tests/data/{filename}.json", "r") as f:
        return [json.load(f)]


def mock_response(status_code: int = 404):
    # TODO: Rename it.
    r = requests.models.Response()
    r.status_code = status_code
    return r


@pytest.fixture
def searcher() -> AbstractSearcher:
    return GoogleMapSearcher()


SHINJUKU = {
    "json": mock_sauna_response("gmap_shinjuku"),
    "place_id": "ChIJpaKQwbSNGGARu2ACecsZ24Y",
    "service_hours": "本日の営業時間: 24時間営業",
    "lat_lng": {"lat": 35.69025476558695, "lng": 139.7006123537284},
}

SHIMOSUWA = {
    "place_id": "ChIJQSMyFFFVHGARwCusWN8A3KM",
    "service_hours": "本日の営業時間: 5時30分～22時00分",
}


class TestSearchSauna:
    @pytest.mark.parametrize("keyword", ["新宿"])
    def test(self, mocker, keyword, searcher):
        mocker.patch(
            "smart_sauna_map.searcher.google_map_searcher.GoogleMapSearcher._search_sauna",
            return_value=SHINJUKU["json"],
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=SHINJUKU["lat_lng"],
        )
        sauna = search_sauna(keyword, searcher)[0]
        assert sauna.name == "SOLA SPA 歌舞伎町 新宿の湯"

    @pytest.mark.parametrize("place_id", [SHINJUKU["place_id"], SHIMOSUWA["place_id"]])
    def test_get_image(self, searcher, place_id):
        # NOTE: 現状はただの疎通テストなのでassertを入れる
        _ = searcher._get_image(place_id)

    @pytest.mark.parametrize(
        "place_id, expected_service_hours",
        [
            (SHINJUKU["place_id"], SHINJUKU["service_hours"]),
            (SHIMOSUWA["place_id"], SHIMOSUWA["service_hours"]),
        ],
    )
    def test_get_service_hours(self, searcher, place_id, expected_service_hours):
        service_hours = searcher._get_service_hours(place_id, weekday_id=0)
        assert expected_service_hours == service_hours

    def test_get_200(self, mocker, searcher):
        mocker.patch(
            "smart_sauna_map.searcher.google_map_searcher.GoogleMapSearcher._search_sauna",
            return_value=SHINJUKU["json"],
        )
        search_sauna(keyword="SOLA SPA 歌舞伎町 新宿の湯", searcher=searcher)

    def test_get_404(self, mocker, searcher):
        mocker.patch(
            "smart_sauna_map.searcher.google_map_searcher.GoogleMapSearcher._search_sauna",
            return_value=mock_response(404),
        )
        with pytest.raises(HTTPError):
            search_sauna(keyword="", searcher=searcher)
