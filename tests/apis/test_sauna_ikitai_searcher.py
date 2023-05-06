# -*- coding: utf-8 -*-

import pytest
import requests
from requests.exceptions import HTTPError

from smart_sauna_map.data_models.room import MansRoom, UnisexRoom, WomansRoom
from smart_sauna_map.data_models.sauna import Sauna
from smart_sauna_map.search_sauna import search_sauna


def read_html(filename):
    with open(f"./tests/data/{filename}.html", "r") as f:
        text = f.read()
    return text


def mock_response(status_code: int = 404):
    r = requests.models.Response()
    r.status_code = status_code
    return r


HTML_SHINJUKU = read_html("shinjuku")
HTML_SHIKIJI = read_html("shikiji")

LAT_LNG_SHINJUKU = {"lat": 35.69025476558695, "lng": 139.7006123537284}
LAT_LNG_SHIKIJI = {"lat": 34.950765, "lng": 138.413977}

SAUNA_SHIKIJI = Sauna(
    sauna_id=123,
    name="サウナしきじ",
    address="静岡県静岡市駿河区敷地2丁目25-1",
    ikitai=7255,
    image_url="http://example.com",
    mans_room=MansRoom(100.0, 20.0),
    womans_room=WomansRoom(101.0, 21.0),
    unisex_room=UnisexRoom(102.0, 22.0),
    description=["hogehoge", "awesome"],
    **LAT_LNG_SHIKIJI,
)


class TestSearchSauna:
    @pytest.mark.parametrize("keyword", ["新宿"])
    def test(self, mocker, keyword):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._request",
            return_value=HTML_SHINJUKU,
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=LAT_LNG_SHINJUKU,
        )
        search_sauna(keyword)[0]

    def test_type(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._request",
            return_value=HTML_SHIKIJI,
        )
        out = search_sauna(keyword="サウナしきじ")[0]
        assert isinstance(out, Sauna)

    def test_name(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._request",
            return_value=HTML_SHIKIJI,
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=LAT_LNG_SHIKIJI,
        )
        expected = SAUNA_SHIKIJI
        actual = search_sauna(keyword="サウナしきじ")[0]
        assert actual.name == expected.name

    def test_address(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._request",
            return_value=HTML_SHIKIJI,
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=LAT_LNG_SHIKIJI,
        )
        expected = SAUNA_SHIKIJI
        actual = search_sauna(keyword="サウナしきじ")[0]
        assert actual.address == expected.address

    def test_ikitai(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._request",
            return_value=read_html("shikiji"),
        )
        mocker.patch(
            "smart_sauna_map.geocoding.geocode",
            return_value=LAT_LNG_SHIKIJI,
        )
        expected = SAUNA_SHIKIJI
        actual = search_sauna(keyword="サウナしきじ")[0]
        assert actual.ikitai == expected.ikitai

    def test_get_200(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._sub_request",
            return_value=mock_response(200),
        )
        search_sauna(keyword="サウナしきじ")

    def test_get_404(self, mocker):
        mocker.patch(
            "smart_sauna_map.searchers.sauna_ikitai_searcher.SaunaIkitaiSearcher._sub_request",
            return_value=mock_response(404),
        )
        with pytest.raises(HTTPError):
            search_sauna(keyword="")
