"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

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


@dataclass(frozen=True)
class TestMeasurement:
    """A single parameter measured during a test."""

    parameter_name: str
    measured_value: float
    unit: Unit
    mode: MeasurementMode = MeasurementMode.DC
    nominal_value: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    raw_data_ref: str = ""  # path to screenshot, trace, waveform


@dataclass
class TestResult:
    """Final result of a test execution."""

    passed: bool
    measurements: list[TestMeasurement] = field(default_factory=list)
    notes: str = ""
    error: str = ""
