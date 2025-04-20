"""
Defines AbstractConverter class with methods to be implemented by all to_kraken_converters.
All concrete to_kraken_converters must inherit from this class.
"""
from abc import ABC, abstractmethod


class AbstractConverter(ABC):
    @abstractmethod
    def can_convert(self, filename: str) -> bool:
        pass

    @abstractmethod
    def convert(self, filename: str, output_filename: str) -> str:
        pass
