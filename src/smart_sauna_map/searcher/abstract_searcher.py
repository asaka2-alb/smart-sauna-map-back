from abc import ABC, abstractmethod
from typing import Optional

from smart_sauna_map.data_models.sauna import Sauna


class AbstractSearcher(ABC):
    @abstractmethod
    def search_sauna(
        keyword: Optional[str] = "しきじ",
    ) -> list[Sauna]:
        pass
