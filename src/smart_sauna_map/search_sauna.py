# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import cache
from dataclasses import dataclass
from typing import Optional


import urllib.parse
import re
import requests
from bs4 import BeautifulSoup

from smart_sauna_map.geocoding import geocode

__all__ = ["search_sauna"]


@dataclass
class Sauna:
    name: str
    address: str
    ikitai: int
    lat: float | None
    lng: float | None


@cache
def search_sauna(
    keyword: Optional[str] = "しきじ",
    prefecture: Optional[str] = "shizuoka",
    page_index: int = 1,
) -> list[Sauna]:
    """Get sauna information from sauna-ikitai.com with given parameters.

    Args:
        keyword: Search word to get sauna list. Defaults to "富士".
        prefecture: Prefecture to narrow down the search range. Defaults to "tokyo".
        page_index: Page index to load sauna. One page contains 20 saunas. Defaults to 1.

    Returns:
        List of sauna objects which contain the name, the address, the ikitai.

    Examples:
        >>> search_sauna(keyword="しきじ", prefecture="shizuoka", page_index=1)
        [
            Sauna(name='サウナしきじ', address='静岡県静岡市駿河区敷地2丁目25-1', ikitai=7142),
            Sauna(name='蓮台寺温泉 清流荘', address='静岡県下田市河内２-２', ikitai=1168),
            Sauna(name='駿河健康ランド', address='静岡県静岡市清水区興津東町１２３４', ikitai=771),
            ...,
            Sauna(name='笑福の湯', address='静岡県焼津市柳新屋２４１-１', ikitai=162),
            Sauna(name='赤沢日帰り温泉館', address='静岡県伊東市赤沢浮山170-2', ikitai=156),
            Sauna(name='sauna MYSA', address='静岡県静岡市葵区足久保口組１６２０−１', ikitai=153),
        ]
    """
    response: str = _request(keyword, prefecture, page=page_index)
    soup: BeautifulSoup = _parse(response)
    return _extract_saunas(soup)


def _request(
    keyword: Optional[str] = "富士",
    prefecture: Optional[str] = "tokyo",
    page: Optional[int] = 1,
) -> str:
    url = "https://sauna-ikitai.com/search"
    payload: dict[str, str | int] = {}
    if keyword:
        payload.update({"keyword": keyword})
    if prefecture:
        payload.update({"prefecture[]": prefecture})
    if page:
        payload.update({"page": page})

    res: requests.models.Response = _sub_request(url, payload)
    _raise_error_if_status_code_is_not_200(res)
    return res.text


def _sub_request(
    url: str, payload: dict[str, str | int], timeout: float = 3.0
) -> requests.models.Response:
    return requests.get(url, params=urllib.parse.urlencode(payload), timeout=timeout)


def _raise_error_if_status_code_is_not_200(res: requests.models.Response):
    res.raise_for_status()


def _parse(res: str) -> BeautifulSoup:
    return BeautifulSoup(res, "html.parser")


def _extract_saunas(soup: BeautifulSoup) -> list[Sauna]:
    names = _extract_sauna_names(soup)
    addresses = _extract_sauna_addresses(soup)
    ikitais = _extract_sauna_ikitai_from_contents(soup)
    latlngs = [geocode(name) for name in list(names)]

    saunas: list[Sauna] = [
        Sauna(
            name=name,
            address=address,
            ikitai=ikitai,
            lat=latlng["lat"],
            lng=latlng["lng"],
        )
        for name, address, ikitai, latlng in zip(names, addresses, ikitais, latlngs)
    ]
    return saunas


def _extract_sauna_names(soup: BeautifulSoup) -> list[str]:
    def parse(s):
        return s.find("h3").text.strip()

    return [parse(s) for s in soup.find_all(class_="p-saunaItemName")]


def _extract_sauna_addresses(soup: BeautifulSoup) -> list[str]:
    def parse(s):
        return s.text.strip().replace("\xa0", "")

    return [parse(s) for s in soup.find_all("address")]


def _extract_sauna_ikitai_from_contents(
    soup, class_: str = "p-saunaItem_actions", search_string: str = "イキタイ"
) -> list[int]:
    ikitais = []
    for actions in soup.find_all(class_=class_):
        for content in actions.contents:
            if search_string in content.text:
                matched_texts = re.findall(r"[\d]+", content.text)
                if len(matched_texts) > 1:
                    raise ValueError(
                        f"ikitai number is expected to have a digit, but found multiple ikitai number {matched_texts}."
                    )
                ikitai = int(matched_texts[0])
                ikitais.append(ikitai)
    return ikitais


if __name__ == "__main__":
    info = search_sauna(keyword="", prefecture="shizuoka", page_index=1)
