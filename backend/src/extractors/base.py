from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExtractor(ABC):
    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def extract(self, file_path: str) -> Dict[str, Any]:
        pass
