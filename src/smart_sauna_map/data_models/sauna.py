from __future__ import annotations

from dataclasses import dataclass

from smart_sauna_map.data_models.room import MansRoom, UnisexRoom, WomansRoom


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
