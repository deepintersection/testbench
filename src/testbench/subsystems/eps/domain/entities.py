"""
EPS (Electrical Power System) subsystem domain.

Ubiquitous language:
    - Solar Array Input: raw power from solar panels (lab: simulated by PSU)
    - MPPT: Maximum Power Point Tracker — extracts max power from solar array
    - Battery: Li-ion pack, 2S config, CC/CV charge, UVP/OVP protection
    - Power Rail: regulated DC output feeding satellite bus (3.3V, 5V, 12V)
    - OCP: Over-Current Protection — trips when load exceeds threshold
    - OVP/UVP: Over/Under-Voltage Protection on battery path
    - Inrush: current spike at rail enable (capacitor charge)
    - Ripple: AC component on DC rail (pk-pk, measured with scope AC-coupled)
    - Efficiency: P_out / P_in per converter stage
    - Load transient: voltage response to sudden load step
    - Power sequencing: controlled order of rail enable at startup
    - Telemetry: ADC readings of V, I, T reported over SpaceWire/I2C
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

# ─── Power Rails ──────────────────────────────────────────────


class PowerRailId(StrEnum):
    BUS_3V3 = "3v3_bus"
    BUS_5V = "5v_bus"
    BUS_12V = "12v_bus"
    BATT_CHARGE = "batt_charge"
    BATT_HEATER = "batt_heater"


@dataclass(frozen=True)
class PowerRailSpec:
    rail: PowerRailId
    nominal_voltage: float
    tolerance_percent: float
    max_current_ma: float
    max_ripple_mv: float
    max_startup_time_ms: float
    ocp_threshold_ma: float
    ocp_tolerance_percent: float = 10.0
    enable_sequence_order: int = 0

    @property
    def voltage_upper(self) -> float:
        return self.nominal_voltage * (1 + self.tolerance_percent / 100)

    @property
    def voltage_lower(self) -> float:
        return self.nominal_voltage * (1 - self.tolerance_percent / 100)


EPS_RAIL_SPECS = [
    PowerRailSpec(
        PowerRailId.BUS_3V3,
        3.3,
        5.0,
        2000.0,
        30.0,
        10.0,
        2500.0,
        enable_sequence_order=1,
    ),
    PowerRailSpec(
        PowerRailId.BUS_5V,
        5.0,
        5.0,
        1500.0,
        40.0,
        15.0,
        2000.0,
        enable_sequence_order=2,
    ),
    PowerRailSpec(
        PowerRailId.BUS_12V,
        12.0,
        3.0,
        800.0,
        60.0,
        25.0,
        1000.0,
        enable_sequence_order=3,
    ),
]

SEQUENCING_DELAY_MS_MIN = 5.0  # min delay between consecutive rail enables
SEQUENCING_DELAY_MS_MAX = 50.0


# ─── Solar Array ──────────────────────────────────────────────


@dataclass(frozen=True)
class SolarArraySpec:
    voc_v: float = 22.0
    isc_ma: float = 1200.0
    vmpp_v: float = 18.0
    impp_ma: float = 1000.0
    pmpp_mw: float = 18000.0


# ─── Battery ──────────────────────────────────────────────────


@dataclass(frozen=True)
class BatterySpec:
    chemistry: str = "Li-ion 2S"
    nominal_voltage: float = 7.4
    min_voltage: float = 6.0  # UVP cutoff
    max_voltage: float = 8.4  # OVP / full charge
    capacity_mah: float = 5200.0
    max_charge_current_ma: float = 5200.0  # 1C
    cc_cv_transition_v: float = 8.3  # switch from CC to CV
    charge_termination_ma: float = 260.0  # C/20


# ─── Monitor Channels ─────────────────────────────────────────

EPS_MONITOR_CHANNELS = [
    {
        "channel_name": "eps_solar_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "eps",
        "nominal": (16.0, 22.0),
        "warning": (12.0, 24.0),
        "abort": (0.0, 28.0),
    },
    {
        "channel_name": "eps_solar_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "eps",
        "nominal": (0.0, 1200.0),
        "warning": (0.0, 1500.0),
        "abort": (0.0, 2000.0),
    },
    {
        "channel_name": "eps_battery_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "eps",
        "nominal": (6.4, 8.4),
        "warning": (6.0, 8.6),
        "abort": (5.5, 9.0),
    },
    {
        "channel_name": "eps_battery_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "eps",
        "nominal": (-5200.0, 5200.0),
        "warning": (-6000.0, 6000.0),
        "abort": (-7000.0, 7000.0),
    },
    {
        "channel_name": "eps_battery_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "eps",
        "nominal": (10.0, 45.0),
        "warning": (0.0, 55.0),
        "abort": (-10.0, 65.0),
    },
    {
        "channel_name": "eps_3v3_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "eps",
        "nominal": (3.135, 3.465),
        "warning": (3.0, 3.6),
        "abort": (2.8, 3.8),
    },
    {
        "channel_name": "eps_3v3_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "eps",
        "nominal": (0.0, 2000.0),
        "warning": (0.0, 2300.0),
        "abort": (0.0, 2800.0),
    },
    {
        "channel_name": "eps_5v_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "eps",
        "nominal": (4.75, 5.25),
        "warning": (4.5, 5.5),
        "abort": (4.0, 6.0),
    },
    {
        "channel_name": "eps_5v_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "eps",
        "nominal": (0.0, 1500.0),
        "warning": (0.0, 1800.0),
        "abort": (0.0, 2200.0),
    },
    {
        "channel_name": "eps_12v_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "eps",
        "nominal": (11.64, 12.36),
        "warning": (11.0, 13.0),
        "abort": (10.0, 14.0),
    },
    {
        "channel_name": "eps_12v_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "eps",
        "nominal": (0.0, 800.0),
        "warning": (0.0, 950.0),
        "abort": (0.0, 1200.0),
    },
    {
        "channel_name": "eps_board_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "eps",
        "nominal": (10.0, 60.0),
        "warning": (0.0, 75.0),
        "abort": (-10.0, 90.0),
    },
]


# ─── Test Catalog ─────────────────────────────────────────────


@dataclass(frozen=True)
class EPSTestSpec:
    code: str
    name: str
    description: str
    estimated_duration_seconds: int
    runnable_during_stress: bool = True


EPS_TEST_CATALOG = [
    # Rail regulation
    EPSTestSpec(
        "EPS-RAIL-001",
        "Rail voltage regulation",
        "Enable each power rail. Measure output voltage under no-load, "
        "50%% load, and 100%% load. Verify within ±tolerance at each point.",
        120,
    ),
    EPSTestSpec(
        "EPS-RAIL-002",
        "Rail startup timing and inrush",
        "Enable each rail while capturing with oscilloscope. Measure time from "
        "enable to voltage in regulation band. Measure peak inrush current.",
        60,
    ),
    EPSTestSpec(
        "EPS-RAIL-003",
        "Output ripple measurement",
        "With each rail at nominal load, measure pk-pk ripple using scope "
        "AC-coupled. Verify below max_ripple_mv specification.",
        90,
    ),
    EPSTestSpec(
        "EPS-RAIL-004",
        "Load transient response",
        "Apply sudden load step (0%% to 80%%) on each rail. Capture voltage "
        "transient. Measure overshoot, undershoot, and settling time.",
        90,
    ),
    EPSTestSpec(
        "EPS-SEQ-001",
        "Power sequencing order",
        "From cold start enable all rails. Capture multi-channel scope trace. "
        "Verify rails enable in correct order with correct inter-rail delays.",
        30,
    ),
    # Protection
    EPSTestSpec(
        "EPS-OCP-001",
        "Overcurrent protection",
        "Gradually increase electronic load on each rail until OCP triggers. "
        "Measure trip current. Verify trip point within ±10%% of spec. "
        "Verify rail recovers after load removed.",
        180,
        runnable_during_stress=False,
    ),
    EPSTestSpec(
        "EPS-OVP-001",
        "Battery overvoltage protection",
        "Inject voltage above battery max (8.4V) via solar simulator. "
        "Verify charge path disconnects. Measure actual OVP trip point.",
        60,
        runnable_during_stress=False,
    ),
    EPSTestSpec(
        "EPS-UVP-001",
        "Battery undervoltage lockout",
        "Discharge battery to near UVP threshold (6.0V). Verify rails "
        "shut down cleanly. Measure actual UVP trip voltage.",
        120,
        runnable_during_stress=False,
    ),
    # Efficiency and MPPT
    EPSTestSpec(
        "EPS-EFF-001",
        "Conversion efficiency",
        "Measure input power and output power for each rail at 25%%, 50%%, "
        "75%%, 100%% load. Calculate η = P_out / P_in.",
        240,
    ),
    EPSTestSpec(
        "EPS-MPPT-001",
        "MPPT tracking efficiency",
        "Set solar simulator to known IV curve. Measure power extracted by "
        "MPPT at 100%%, 75%%, 50%%, 25%% illumination. Calculate tracking "
        "efficiency as P_extracted / P_available.",
        180,
    ),
    # Battery
    EPSTestSpec(
        "EPS-BATT-001",
        "Battery charge profile",
        "From known SOC, enable charging from solar simulator. Monitor charge "
        "current, battery voltage, temperature. Verify CC→CV transition. "
        "Verify charge termination at C/20.",
        300,
        runnable_during_stress=False,
    ),
    # Telemetry
    EPSTestSpec(
        "EPS-TM-001",
        "EPS telemetry accuracy",
        "Read all EPS ADC telemetry channels via SpaceWire/I2C. Compare each "
        "reading against calibrated DMM measurement. Verify telemetry accuracy "
        "within ±1%% for voltage, ±2%% for current, ±2°C for temperature.",
        120,
    ),
]
