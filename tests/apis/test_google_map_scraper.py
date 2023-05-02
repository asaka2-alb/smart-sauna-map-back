# -*- coding: utf-8 -*-

import json

import pytest
import requests
from requests.exceptions import HTTPError

from smart_sauna_map.room import MansRoom, UnisexRoom, WomansRoom
from smart_sauna_map.sauna import Sauna
from smart_sauna_map.scraper.abstract_scraper import AbstractScraper
from smart_sauna_map.scraper.google_map_scraper import GoogleMapScraper
from smart_sauna_map.search_sauna import search_sauna


def mock_sauna_response(filename) -> list[dict]:
    with open(f"./tests/data/{filename}.json", "r") as f:
        return [json.load(f)]


def mock_response(status_code: int = 404):
    # TODO: Rename it.
    r = requests.models.Response()
    r.status_code = status_code
    return r


@pytest.fixture
def scraper() -> AbstractScraper:
    return GoogleMapScraper()


JSON_SHINJUKU = mock_sauna_response("gmap_shinjuku")

LAT_LNG_SHINJUKU = {"lat": 35.69025476558695, "lng": 139.7006123537284}


class TestSearchSauna:
    @pytest.mark.parametrize("keyword", ["新宿"])
    def test(self, mocker, keyword, scraper):
        mocker.patch(
            "smart_sauna_map.scraper.google_map_scraper.GoogleMapScraper._search_sauna",
            return_value=JSON_SHINJUKU,
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=LAT_LNG_SHINJUKU,
        )
        sauna = search_sauna(keyword, scraper)[0]
        assert sauna.name == ""

    def test_get_200(self, mocker, scraper):
        mocker.patch(
            "smart_sauna_map.scraper.google_map_scraper.GoogleMapScraper._search_sauna",
            return_value=JSON_SHINJUKU,
        )
        search_sauna(keyword="SOLA SPA 歌舞伎町 新宿の湯", scraper=scraper)

    def test_get_404(self, mocker, scraper):
        mocker.patch(
            "smart_sauna_map.scraper.google_map_scraper.GoogleMapScraper._search_sauna",
            return_value=mock_response(404),
        )
        with pytest.raises(HTTPError):
            search_sauna(keyword="", scraper=scraper)
