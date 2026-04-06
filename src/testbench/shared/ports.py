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


class SpaceWirePort(ABC):
    """SpaceWire I/O via 4Links hardware."""

    @abstractmethod
    def open_link(self, link_id: int, speed_mbps: float = 200.0) -> bool: ...

    @abstractmethod
    def close_link(self, link_id: int) -> None: ...

    @abstractmethod
    def send_packet(self, link_id: int, data: bytes, dest_addr: int = 0) -> bool: ...

    @abstractmethod
    def receive_packet(self, link_id: int, timeout_ms: int = 1000) -> bytes | None: ...

    @abstractmethod
    def get_link_status(self, link_id: int) -> dict: ...

    @abstractmethod
    def rmap_read(
        self, link_id: int, target_addr: int, memory_addr: int, length: int
    ) -> bytes: ...

    @abstractmethod
    def rmap_write(
        self, link_id: int, target_addr: int, memory_addr: int, data: bytes
    ) -> bool: ...


class VNAPort(ABC):
    """Vector Network Analyzer for S-parameter measurement."""

    @abstractmethod
    def configure_sweep(
        self, freq_start_hz: float, freq_stop_hz: float, points: int = 201
    ) -> None: ...

    @abstractmethod
    def measure_s2p(self, filepath: str) -> str:
        """Capture 2-port S-parameters to Touchstone file. Returns path."""
        ...

    @abstractmethod
    def measure_s4p(self, filepath: str) -> str:
        """Capture 4-port S-parameters to Touchstone file. Returns path."""
        ...

    @abstractmethod
    def get_marker_value(self, marker: int, parameter: str = "S21") -> complex: ...

    @abstractmethod
    def capture_screenshot(self, filepath: str) -> str: ...


# ─── Null / Stub adapters for testing without hardware ─────────


class NullTelemetryPort(TelemetryPort):
    def read(self, instrument_id: str, channel: str) -> float:
        return 0.0

    def is_connected(self, instrument_id: str) -> bool:
        return True


class NullInstrumentPort(InstrumentPort):
    def connect(self, instrument_id: str) -> None:
        pass

    def disconnect(self, instrument_id: str) -> None:
        pass

    def send_command(self, instrument_id: str, command: str) -> str:
        return ""

    def measure(
        self, instrument_id: str, measurement_type: str, channel: str = ""
    ) -> float:
        return 0.0

    def capture_screenshot(self, instrument_id: str, filepath: str) -> str:
        return filepath

    def capture_trace(
        self, instrument_id: str, filepath: str, format: str = "csv"
    ) -> str:
        return filepath


class NullVNAPort(VNAPort):
    def configure_sweep(
        self, freq_start_hz: float, freq_stop_hz: float, points: int = 201
    ) -> None:
        pass

    def measure_s2p(self, filepath: str) -> str:
        return filepath

    def measure_s4p(self, filepath: str) -> str:
        return filepath

    def get_marker_value(self, marker: int, parameter: str = "S21") -> complex:
        return complex(0, 0)

    def capture_screenshot(self, filepath: str) -> str:
        return filepath
