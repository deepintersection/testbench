from abc import ABC, abstractmethod


class TelemetryPort(ABC):
    @abstractmethod
    def read(self, instrument_id: str, channel: str) -> float: ...
    @abstractmethod
    def is_connected(self, instrument_id: str) -> bool: ...


class InstrumentPort(ABC):
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


class SpaceWirePort(ABC):
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
