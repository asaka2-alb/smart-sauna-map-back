# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import cache
from typing import Optional

from smart_sauna_map.data_models.sauna import Sauna
from smart_sauna_map.searchers.abstract_searcher import AbstractSearcher
from smart_sauna_map.searchers.sauna_ikitai_searcher import SaunaIkitaiSearcher

__all__ = ["search_sauna"]


@cache
def search_sauna(
    keyword: Optional[str] = "しきじ",
    searcher: AbstractSearcher = SaunaIkitaiSearcher(),
) -> list[Sauna]:
    """Get sauna information from sauna-ikitai.com with given parameters.

    Args:
        keyword: Search word to get sauna list. Defaults to "富士".
        searcher: Instance of searcher object.

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
    return searcher.search_sauna(keyword=keyword)
