from __future__ import annotations

import re
from functools import cache
from typing import Optional
from urllib.parse import urlencode, urlparse

import requests
from bs4 import BeautifulSoup

from smart_sauna_map.data_models.room import MansRoom, UnisexRoom, WomansRoom
from smart_sauna_map.data_models.sauna import Sauna
from smart_sauna_map.geocoding import geocode
from smart_sauna_map.searcher.abstract_searcher import AbstractSearcher


class SaunaIkitaiSearcher(AbstractSearcher):
    @cache
    def search_sauna(
        self,
        keyword: Optional[str] = "しきじ",
    ) -> list[Sauna]:
        """Get sauna information from sauna-ikitai.com with given parameters.

        Args:
            keyword: Search word to get sauna list. Defaults to "富士".

        Returns:
            List of sauna objects which contain the name, the address, the ikitai.

        Examples:
            >>> search_sauna(keyword="しきじ")
            [
                Sauna(
                    sauna_id=2779,
                    name='サウナしきじ',
                    address='静岡県静岡市駿河区敷地2-25-1',
                    ikitai=8949,
                    lat=34.950765,
                    lng=138.413977,
                    image_url='https://img.sauna-ikitai.com/sauna/'
                        '2779_20220429_182044_Eittr9xyyp_medium.jpg',
                    mans_room=MansRoom(
                        sauna_temperature=110.0, mizuburo_temperature=19.0
                    ),
                    womans_room=WomansRoom(
                        sauna_temperature=95.0,
                        mizuburo_temperature=17.0,
                    ),
                    unisex_room=None, description=['入浴料：500円〜', '定休日：無休'],
                )
            ]
        """
        response: str = self._request(keyword)
        soup: BeautifulSoup = self._parse(response)
        return self._extract_saunas(soup)

    def _request(
        self,
        keyword: Optional[str] = "富士",
    ) -> str:
        url = "https://sauna-ikitai.com/search"
        payload: dict[str, str | int] = {}
        if keyword:
            payload.update({"keyword": keyword})

        res: requests.models.Response = self._sub_request(url, payload)
        self._raise_error_if_status_code_is_not_200(res)
        return res.text

    def _sub_request(
        self, url: str, payload: dict[str, str | int], timeout: float = 3.0
    ) -> requests.models.Response:
        return requests.get(url, params=urlencode(payload), timeout=timeout)

    def _raise_error_if_status_code_is_not_200(self, res: requests.models.Response):
        res.raise_for_status()

    def _parse(self, res: str) -> BeautifulSoup:
        return BeautifulSoup(res, "html.parser")

    def _extract_saunas(self, soup: BeautifulSoup) -> list[Sauna]:
        def sauna(s: BeautifulSoup) -> Sauna:
            name = _extract_sauna_name(s)
            latlng = geocode(name)
            return Sauna(
                sauna_id=_extract_sauna_id(s),
                name=name,
                address=_extract_sauna_address(s),
                ikitai=_extract_sauna_ikitai(s),
                lat=latlng.get("lat", None),
                lng=latlng.get("lng", None),
                image_url=_extract_sauna_image_url(s),
                mans_room=_extract_sauna_mans_room(s),
                womans_room=_extract_sauna_womans_room(s),
                unisex_room=_extract_sauna_unisex_room(s),
                description=_extract_sauna_description(s),
            )

        return [sauna(s) for s in soup.find_all(class_="p-saunaItem")]


def _extract_sauna_name(soup: BeautifulSoup) -> str:
    def parse(s):
        return s.find("h3").text.strip()

    return parse(soup.find(class_="p-saunaItemName"))


def _extract_sauna_address(soup: BeautifulSoup) -> str:
    def parse(s):
        return s.text.strip().replace("\xa0", "")

    return parse(soup.find("address"))


def _extract_sauna_id(soup: BeautifulSoup) -> int:
    def parse(s):
        url = s.find(name="a").get("href")
        sauna_id = int(urlparse(url).path.split("/")[-1])
        return sauna_id

    return parse(soup)


def _extract_sauna_image_url(soup: BeautifulSoup) -> str:
    def parse(s):
        url = str(s.find(name="img").get("src"))
        return url

    return parse(soup.find(class_="p-saunaItem_image"))


def _extract_sauna_mans_room(soup: BeautifulSoup) -> MansRoom | None:
    s = soup.find(class_="p-saunaItemSpec_content p-saunaItemSpec_content--man")
    if not s:
        return None
    return MansRoom(
        sauna_temperature=_find_sauna_temperature(s),
        mizuburo_temperature=_find_mizuburo_temperature(s),
    )


def _extract_sauna_womans_room(soup: BeautifulSoup) -> WomansRoom | None:
    s = soup.find(class_="p-saunaItemSpec_content p-saunaItemSpec_content--woman")
    if not s:
        return None
    return WomansRoom(
        sauna_temperature=_find_sauna_temperature(s),
        mizuburo_temperature=_find_mizuburo_temperature(s),
    )


def _extract_sauna_unisex_room(soup: BeautifulSoup) -> UnisexRoom | None:
    s = soup.find(class_="p-saunaItemSpec_content p-saunaItemSpec_content--unisex")
    if not s:
        return None
    return UnisexRoom(
        sauna_temperature=_find_sauna_temperature(s),
        mizuburo_temperature=_find_mizuburo_temperature(s),
    )


def _find_sauna_temperature(s):
    return _extract_digits(
        s.find(class_="p-saunaItemSpec_item p-saunaItemSpec_item--sauna")
        .find(class_="p-saunaItemSpec_value")
        .text
    )


def _find_mizuburo_temperature(s):
    return _extract_digits(
        s.find(class_="p-saunaItemSpec_item p-saunaItemSpec_item--mizuburo")
        .find(class_="p-saunaItemSpec_value")
        .text
    )


def _extract_digits(text: str) -> float | None:
    matched = re.match(r"\d+(\.\d+)?", text)
    if not matched:
        return None
    return float(matched.group())


def _extract_sauna_description(soup: BeautifulSoup) -> list[str]:
    def parse(s):
        descs = []
        for _s in s.find_all(name="li"):
            descs.append(_s.text)
        return descs

    return parse(soup.find(class_="p-saunaItem_informations"))


def _extract_sauna_ikitai(
    soup, class_: str = "p-saunaItem_actions", search_string: str = "イキタイ"
) -> int:
    ikitai = None
    contents = soup.find(class_=class_).contents

    for content in contents:
        if search_string in content.text:
            matched_texts = re.findall(r"[\d]+", content.text)
            if len(matched_texts) > 1:
                raise ValueError(
                    f"ikitai number must have a digit, but found multiple"
                    f" digits {matched_texts}."
                )
            ikitai = int(matched_texts[0])

    if ikitai is None:
        raise ValueError(
            f"ikitai number must be in content, but not found in {contents}."
        )

    return ikitai
