from __future__ import annotations

import os
from datetime import datetime
from functools import cache
from typing import Optional

import googlemaps
from requests.exceptions import HTTPError

from smart_sauna_map.data_models.room import MansRoom, WomansRoom
from smart_sauna_map.data_models.sauna import Sauna
from smart_sauna_map.searchers.abstract_searcher import AbstractSearcher

GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")


class GoogleMapSearcher(AbstractSearcher):
    def __init__(self):
        self.gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)

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
        if self._is_abnormal_query(keyword):
            raise HTTPError

        saunas = self._search_sauna(keyword)
        return [self._cast_to_sauna(sauna) for sauna in saunas]

    def _search_sauna(self, keyword: str) -> list[dict]:
        response = self.gmaps.places(f"{keyword} サウナ", language="ja")
        return response["results"]

    def _is_abnormal_query(self, query: str) -> bool:
        max_query_length = 20  # NOTE: WIP

        if len(query) == 0:
            return True

        if len(query) > max_query_length:
            return True

        return False

    def _cast_to_sauna(self, sauna: dict) -> Sauna:
        return Sauna(
            sauna_id=sauna["place_id"],
            name=sauna["name"],
            address=sauna["formatted_address"],
            ikitai=sauna[
                "rating"
            ],  # TODO: Consider use rating or user_ratings_total or something
            lat=sauna["geometry"]["location"]["lat"],
            lng=sauna["geometry"]["location"]["lng"],
            image_url=self._get_image(sauna["place_id"]),
            mans_room=MansRoom(
                sauna_temperature=0.0, mizuburo_temperature=0.0
            ),  # TODO: Consider to abondone rooms and other information
            womans_room=WomansRoom(
                sauna_temperature=0.0,
                mizuburo_temperature=0.0,
            ),
            unisex_room=None,
            description=[self._get_service_hours(sauna["place_id"])],
        )

    def _get_image(self, place_id: str) -> str:
        response = self.gmaps.place(place_id, language="ja")
        photo_reference = (
            response["result"]["photos"][0]["photo_reference"]
            if "photos" in response["result"]
            else "AF1QipNp-EQkrzLg0lwmkqtY-AACLSw0mSp0Ku0Euzyr"
        )

        return (
            "https://maps.googleapis.com/maps/api/place/photo"
            + f"?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAP_API_KEY}"
        )

    def _get_service_hours(self, place_id: str, *, weekday_id: int = -1) -> str:
        default_weekday_text = [
            f"{weekday}: 記載なし"
            for weekday in ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        ]
        response = self.gmaps.place(place_id, language="ja")
        weekday_text = (
            response["result"]["current_opening_hours"]["weekday_text"]
            if "current_opening_hours" in response["result"]
            and "weekday_text" in response["result"]["current_opening_hours"]
            else default_weekday_text
        )

        today_service_hours_with_prefix = weekday_text[
            weekday_id if weekday_id != -1 else datetime.now().weekday()
        ]
        today_service_hours = today_service_hours_with_prefix.split()[1]
        if today_service_hours == "24":
            today_service_hours = "24時間営業"

        return "本日の営業時間: " + today_service_hours
