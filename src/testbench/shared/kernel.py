"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum

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
