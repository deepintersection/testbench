from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def generate_id() -> str:
    return str(uuid.uuid4())


class Unit(Enum):
    VOLT = "V"
    MILLIVOLT = "mV"
    AMPERE = "A"
    MILLIAMPERE = "mA"
    WATT = "W"
    OHM = "Ω"
    MEGAOHM = "MΩ"
    DBM = "dBm"
    DB = "dB"
    HERTZ = "Hz"
    MEGAHERTZ = "MHz"
    GIGAHERTZ = "GHz"
    CELSIUS = "°C"
    PASCAL = "Pa"
    MILLIBAR = "mbar"
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "μs"
    NANOSECOND = "ns"
    PERCENT = "%"
    MEGABIT_PER_SECOND = "Mbps"
    DIMENSIONLESS = ""


@dataclass(frozen=True)
class PhysicalQuantity:
    value: float
    unit: Unit

    def __str__(self) -> str:
        return f"{self.value:.4g} {self.unit.value}"


@dataclass(frozen=True)
class Tolerance:
    nominal: float
    upper: float
    lower: float
    unit: Unit

    @classmethod
    def symmetric(cls, nominal: float, delta: float, unit: Unit) -> Tolerance:
        return cls(
            nominal=nominal, upper=nominal + delta, lower=nominal - delta, unit=unit
        )

    @classmethod
    def percentage(cls, nominal: float, pct: float, unit: Unit) -> Tolerance:
        return cls.symmetric(nominal, nominal * pct / 100.0, unit)

    def contains(self, value: float) -> bool:
        return self.lower <= value <= self.upper


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=generate_id)
    occurred_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class HardwareRevision:
    serial_number: str
    revision: str
    pcb_version: Optional[str] = None
    firmware_version: Optional[str] = None
