from abc import ABC, abstractmethod
from enum import Enum


class OutputType(str, Enum):
    """
    Enum for the output types
    """
    JSON = "json"


class Output(ABC):
    """
    Abstract base class for output types
    """
    @abstractmethod
    def write(self, data: dict) -> None:
        pass
