from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass
class BathRoom(ABC):
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
