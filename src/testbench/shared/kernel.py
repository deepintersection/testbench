"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

# ─── Identifiers ───────────────────────────────────────────────


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ─── Physical Units ────────────────────────────────────────────


class Unit(Enum):
    """Physical dimension and scale."""

    # Voltage
    VOLT = "V"
    MILLIVOLT = "mV"
    MICROVOLT = "μV"
    # Current
    AMPERE = "A"
    MILLIAMPERE = "mA"
    MICROAMPERE = "μA"
    # Power
    WATT = "W"
    MILLIWATT = "mW"
    DBM = "dBm"
    DBMV = "dBmV"
    # Ratio
    DB = "dB"
    # Resistance / Impedance
    OHM = "Ω"
    MEGAOHM = "MΩ"
    # Frequency
    HERTZ = "Hz"
    KILOHERTZ = "kHz"
    MEGAHERTZ = "MHz"
    GIGAHERTZ = "GHz"
    # Time
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "μs"
    NANOSECOND = "ns"
    PICOSECOND = "ps"
    # Temperature
    CELSIUS = "°C"
    # Pressure
    PASCAL = "Pa"
    MILLIBAR = "mbar"
    # Data rate
    BIT_PER_SECOND = "bps"
    MEGABIT_PER_SECOND = "Mbps"
    # Other
    PERCENT = "%"
    PPM = "ppm"
    DEGREE = "°"
    DIMENSIONLESS = ""


class MeasurementMode(str, Enum):
    """How the value was acquired — the measurement coupling/mode."""

    DC = "dc"  # DC average (default for most measurements)
    RMS = "rms"  # True RMS (AC+DC or AC-only depending on coupling)
    PEAK = "peak"  # Single-sided peak
    PEAK_TO_PEAK = "pp"  # Peak-to-peak (Vpp, App)
    AVERAGE = "avg"  # Arithmetic mean over N samples
    MIN = "min"  # Minimum over capture window
    MAX = "max"  # Maximum over capture window
    INSTANTANEOUS = "inst"  # Single-shot sample


# ─── Measurement & Test Result ─────────────────────────────────
# These live in the shared kernel because every subsystem's test
# implementations produce them, every registry consumes them, and
# the execution engine stores them. One definition, not three copies.


@dataclass
class TestMeasurement:
    """A single parameter measured during a test.

    Mutable during test execution (tests append raw_data_ref after capture).
    Becomes immutable once wrapped in a frozen TestResult.
    """

    parameter_name: str
    measured_value: float
    unit: str
    mode: str = "dc"  # MeasurementMode value
    nominal_value: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    raw_data_ref: str = ""  # path to screenshot, trace, waveform


@dataclass(frozen=True)
class TestResult:
    """Final result of a test execution — immutable once returned."""

    passed: bool
    measurements: tuple[TestMeasurement, ...] = ()
    notes: str = ""
    error: str = ""


# ─── Repository Interfaces (Percival: domain defines, infra implements) ──


class TestDefinitionRepository(ABC):
    """Port for persisting test definitions.

    The domain defines this interface; the persistence layer implements it.
    Subsystem registries call this to seed definitions, without knowing
    whether the storage is SQLAlchemy, in-memory, or a flat file.
    """

    @abstractmethod
    def find_by_code(self, code: str) -> dict | None: ...

    @abstractmethod
    def find_by_scope(self, subsystem_scope: str) -> list[dict]: ...

    @abstractmethod
    def save(
        self,
        code: str,
        name: str,
        description: str,
        subsystem_scope: str,
        estimated_duration_seconds: int,
        runnable_during_stress: bool = True,
    ) -> None: ...

    @abstractmethod
    def exists(self, code: str) -> bool: ...


class MonitorChannelRepository(ABC):
    """Port for persisting DUT monitor channels and thresholds."""

    @abstractmethod
    def find_by_dut(self, dut_id: str, channel_name: str) -> dict | None: ...

    @abstractmethod
    def save_channel(
        self,
        dut_id: str,
        channel_name: str,
        channel_type: str,
        unit: str,
        subsystem: str,
        nominal: tuple[float, float],
        warning: tuple[float, float],
        abort: tuple[float, float],
        context: str = "ambient",
    ) -> None: ...


# ─── Physical Quantity ──────────────────────────────────────────


@dataclass(frozen=True)
class PhysicalQuantity:
    """Immutable measured value with unit and mode."""

    value: float
    unit: Unit
    mode: MeasurementMode = MeasurementMode.DC

    def __str__(self) -> str:
        if self.mode == MeasurementMode.DC:
            return f"{self.value:.4g} {self.unit.value}"
        return f"{self.value:.4g} {self.unit.value}{self.mode.value}"


# ─── Tolerance ──────────────────────────────────────────────────


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


# ─── Base Domain Event ──────────────────────────────────────────


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=generate_id)
    occurred_at: datetime = field(default_factory=utc_now)


# ─── Hardware Revision ──────────────────────────────────────────


@dataclass(frozen=True)
class HardwareRevision:
    serial_number: str
    revision: str
    pcb_version: Optional[str] = None
    firmware_version: Optional[str] = None
