from abc import ABC, abstractmethod


class AbstractConverter(ABC):
    @abstractmethod
    def can_convert(self, filename: str) -> bool:
        pass

    @abstractmethod
    def convert(self, filename: str, output_filename: str) -> str:
        pass
