from abc import ABC, abstractmethod
from typing import Optional

from smart_sauna_map.sauna import Sauna


class AbstractScraper(ABC):
    @abstractmethod
    def search_sauna(
        keyword: Optional[str] = "しきじ",
    ) -> list[Sauna]:
        pass
