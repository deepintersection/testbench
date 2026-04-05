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


class InstrumentPort(ABC):
    """Active test instrument control — DMM, scope, PSU, eload, specan."""

    @abstractmethod
    def connect(self, instrument_id: str) -> None: ...

    @abstractmethod
    def disconnect(self, instrument_id: str) -> None: ...

    @abstractmethod
    def send_command(self, instrument_id: str, command: str) -> str: ...

    @abstractmethod
    def measure(
        self, instrument_id: str, measurement_type: str, channel: str = ""
    ) -> float: ...

    @abstractmethod
    def capture_screenshot(self, instrument_id: str, filepath: str) -> str:
        """Save instrument screen capture to file. Returns actual path."""
        ...

    @abstractmethod
    def capture_trace(
        self, instrument_id: str, filepath: str, format: str = "csv"
    ) -> str:
        """Save trace/measurement data to file. Returns actual path.
        format: csv, s2p, s4p, wfm, etc.
        """
        ...
