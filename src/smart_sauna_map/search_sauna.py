# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
import re
from dataclasses import dataclass
from functools import cache
from typing import Optional
from urllib.parse import urlencode, urlparse

import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, initialize_app

from smart_sauna_map.geocoding import geocode

__all__ = ["search_sauna"]

# TODO: パッケージトップを指すパスを init.py などに定義すると良いかも
SECRET = "./secrets/smart-sauna-map-firebase-adminsdk-kwl6u-5067562322.json"

initialize_app(credentials.Certificate(SECRET))


@dataclass
class Sauna:
    sauna_id: int
    name: str
    address: str
    ikitai: int
    lat: float | None
    lng: float | None
    image_url: str | None
    mans_room: MansRoom | None
    womans_room: WomansRoom | None
    unisex_room: UnisexRoom | None
    description: list[str] | None


@dataclass
class BathRoom(abc.ABC):
    sauna_temperature: float | None
    mizuburo_temperature: float | None


@dataclass
class MansRoom(BathRoom):
    pass


@dataclass
class WomansRoom(BathRoom):
    pass


@dataclass
class UnisexRoom(BathRoom):
    pass


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
        page_index: Page index to load sauna. One page contains 20 saunas. Defaults to
            1.

    Returns:
        List of sauna objects which contain the name, the address, the ikitai.

    Examples:
        >>> search_sauna(keyword="しきじ", prefecture="shizuoka", page_index=1)
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
                mans_room=MansRoom(sauna_temperature=110.0, mizuburo_temperature=19.0),
                womans_room=WomansRoom(
                    sauna_temperature=95.0,
                    mizuburo_temperature=17.0,
                ),
                unisex_room=None, description=['入浴料：500円〜', '定休日：無休'],
            )
        ]
    """
    response: str = _request(keyword, prefecture, page=page_index)
    soup: BeautifulSoup = _parse(response)
    return _extract_saunas(soup)


class BaseFetcherFirebase(abc.ABC):
    @abc.abstractmethod
    def fetch_saunas(lat, lng, lat_width, lng_width):
        pass


class SaunaFetcher(BaseFetcherFirebase):
    def __init__(self, collection_name: str = "saunas"):
        self.db = get_firestore_database()
        self.collection_name = collection_name

    def fetch_saunas(
        self,
        lat: float,
        lng: float,
        lat_width: float,
        lng_width: float,
    ) -> List[Sauna]:
        """Fetch saunas based on lat, lng.

        Args:
            lat: 緯度.
            lng: 経度.
            lat_width: 検索する緯度の幅.
            lng_width: 検索する経度の幅.

        Returns:
            List[Sauna]: List of sauna.
        """
        # サウナ collection への reference を取得する
        saunas_ref = get_collection_reference(self.db, self.collection_name)

        # Firebase からデータをクエリする
        lat_query_ref = saunas_ref.where("lat", ">", lat - lat_width).where(
            "lat", "<", lat + lat_width
        )
        docs_extracted_by_lat = lat_query_ref.stream()

        # Firebase では直接 lat, lng の2つで絞ることができないため、こちら側で絞る.
        out_saunas = []
        for doc_extracted_by_lat in docs_extracted_by_lat:
            dict_extracted_by_lat = doc_extracted_by_lat.to_dict()
            if is_within_designated_area(
                lat=dict_extracted_by_lat["lat"],
                lng=dict_extracted_by_lat["lng"],
                lat_center=lat,
                lng_center=lng,
                lat_width=lat_width,
                lng_width=lng_width,
            ):
                out_saunas.append(Sauna(**dict_extracted_by_lat))

        return out_saunas


# TODO: WIP
# TODO: Firestore への接続まわりをオブジェクト化 あるいは unit of work にする
@cache
def search_sauna_from_firebase(
    fetcher: Class,
    keyword: Optional[str] = "しきじ",
    lat_width: float = 0.2,
    lng_width: float = 0.2,
) -> list[Sauna]:
    """Get sauna information from Firebase with given parameters.

    Args:
        keyword: Search word to get sauna list. Defaults to "富士".
        lat_width: Valid width of latitude. The range is from -90 to 90.
            The valid search area will be from lat - lat_width to lat + lat_width.
        lng_width: Valid width of longitude. The range is from -180 to 180.
            The valid search area will be from lng - lng_width to lng + lng_width.

    Returns:
        List of sauna objects which contain the name, the address, the ikitai.

    Examples:
        >>> search_sauna(keyword="しきじ", prefecture="shizuoka", page_index=1)
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
                mans_room=MansRoom(sauna_temperature=110.0, mizuburo_temperature=19.0),
                womans_room=WomansRoom(
                    sauna_temperature=95.0,
                    mizuburo_temperature=17.0,
                ),
                unisex_room=None, description=['入浴料：500円〜', '定休日：無休'],
            )
        ]
    """
    # keyword をもとに geocode して lat, lon を得る
    latlng = geocode(keyword if keyword is not None else "")
    lat: float = latlng.get("lat", 35.0)  # TODO: デフォルト値は要検討
    lng: float = latlng.get("lng", 135.0)

    saunas = fetcher.fetch_saunas(
        lat,
        lng,
        lat_width,
        lng_width,
    )
    return saunas


def get_firestore_database():
    return firestore.client()


def get_collection_reference(db, collection_name: str = "saunas"):
    """Return reference of a firestore collection."""
    return db.collection(collection_name)


def is_within_designated_area(
    lat: float,
    lng: float,
    lat_center: float,
    lng_center: float,
    lat_width: float,
    lng_width: float,
) -> bool:
    if not (abs(lat - lat_center) < lat_width):
        return False
    if not (abs(lng - lng_center) < lng_width):
        return False
    return True


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
    return requests.get(url, params=urlencode(payload), timeout=timeout)


def _raise_error_if_status_code_is_not_200(res: requests.models.Response):
    res.raise_for_status()


def _parse(res: str) -> BeautifulSoup:
    return BeautifulSoup(res, "html.parser")


def _extract_saunas(soup: BeautifulSoup) -> list[Sauna]:
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


if __name__ == "__main__":
    info = search_sauna(keyword="", prefecture="shizuoka", page_index=1)
