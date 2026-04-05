"""
Ports: abstract interfaces defined by the domain, implemented by infrastructure.
"""

from abc import ABC, abstractmethod


class TelemetryPort(ABC):
    """Background health monitoring — continuous channel reading."""

    @abstractmethod
    def read(self, instrument_id: str, channel: str) -> float: ...

    @abstractmethod
    def is_connected(self, instrument_id: str) -> bool: ...
