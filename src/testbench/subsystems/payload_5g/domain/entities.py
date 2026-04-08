"""
Payload 5G NTN (Non-Terrestrial Network) subsystem domain.

Ubiquitous language:
    - NTN: Non-Terrestrial Network — 3GPP extension for satellite 5G
    - gNB: gNodeB — the 5G base station function running on the satellite
    - UE: User Equipment — ground-side IoT device connecting through the sat
    - EIRP: Effective Isotropic Radiated Power — total TX power including antenna gain
    - EVM: Error Vector Magnitude — TX modulation quality metric
    - ACLR: Adjacent Channel Leakage Ratio — TX spectral cleanliness
    - Sensitivity: minimum RX power for target BER
    - BER: Bit Error Rate — received data error rate
    - NF: Noise Figure — RX chain noise performance
    - PA: Power Amplifier — final TX stage
    - LNA: Low Noise Amplifier — first RX stage
    - Duplex: FDD (frequency division) or TDD (time division)
    - Band: NTN operating band (n256 for S-band, n255 for L-band)
    - Doppler: frequency shift due to satellite motion (~48 kHz max for LEO)
    - Timing advance: propagation delay compensation for LEO (~10-20 ms RTT)
    - IoT session: NB-IoT or LTE-M device attach, data transfer, detach
    - Feeder link: ground station ↔ satellite backhaul link
    - Service link: satellite ↔ UE access link
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

# ─── RF Configuration ─────────────────────────────────────────


class NTNBand(StrEnum):
    """3GPP NTN frequency bands."""

    N255_L_BAND = "n255"  # 1626.5-1660.5 MHz (L-band, service link)
    N256_S_BAND = "n256"  # 1980-2010 / 2170-2200 MHz (S-band)
    N5_850MHZ = "n5"  # 824-849 / 869-894 MHz (sub-1GHz IoT)


class ModulationType(StrEnum):
    QPSK = "QPSK"
    PI2_BPSK = "pi/2-BPSK"  # NB-IoT uplink
    QAM16 = "16QAM"
    QAM64 = "64QAM"


class DuplexMode(StrEnum):
    FDD = "FDD"
    TDD = "TDD"


@dataclass(frozen=True)
class RFChannelConfig:
    """Configuration for a single RF test channel."""

    name: str
    center_freq_mhz: float
    bandwidth_mhz: float
    band: NTNBand
    duplex: DuplexMode
    direction: str  # "tx" or "rx"


# Standard test channels for S-band NTN
PAYLOAD_TEST_CHANNELS = [
    RFChannelConfig(
        "S-band UL low", 1980.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "rx"
    ),
    RFChannelConfig(
        "S-band UL mid", 1995.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "rx"
    ),
    RFChannelConfig(
        "S-band UL high", 2010.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "rx"
    ),
    RFChannelConfig(
        "S-band DL low", 2170.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "tx"
    ),
    RFChannelConfig(
        "S-band DL mid", 2185.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "tx"
    ),
    RFChannelConfig(
        "S-band DL high", 2200.0, 5.0, NTNBand.N256_S_BAND, DuplexMode.FDD, "tx"
    ),
]


# ─── Payload Hardware Specs ───────────────────────────────────


@dataclass(frozen=True)
class PASpec:
    """Power Amplifier specification."""

    max_output_power_dbm: float = 33.0  # ~2W
    p1db_dbm: float = 35.0  # 1dB compression point
    gain_db: float = 30.0
    efficiency_percent_min: float = 25.0  # PAE at rated power


@dataclass(frozen=True)
class LNASpec:
    """Low Noise Amplifier specification."""

    gain_db: float = 18.0
    noise_figure_db_max: float = 1.5
    p1db_input_dbm: float = -15.0


@dataclass(frozen=True)
class TxSpec:
    """Transmitter chain specifications."""

    eirp_dbm_target: float = 40.0  # with antenna gain
    eirp_tolerance_db: float = 2.0
    evm_max_percent: float = 8.0  # for QPSK
    evm_max_16qam_percent: float = 12.5
    aclr_min_db: float = 30.0  # adjacent channel leakage
    spurious_max_dbm: float = -36.0
    frequency_accuracy_ppm: float = 0.1  # critical for NTN Doppler pre-comp
    max_power_variation_db: float = 2.0  # across operating band


@dataclass(frozen=True)
class RxSpec:
    """Receiver chain specifications."""

    sensitivity_dbm: float = -110.0  # for NB-IoT at 1% BER
    noise_figure_db_max: float = 3.0  # full RX chain
    dynamic_range_db: float = 80.0
    image_rejection_db_min: float = 40.0
    blocking_dbm: float = -30.0  # in-band blocker tolerance


@dataclass(frozen=True)
class NTNProtocolSpec:
    """NTN-specific protocol parameters."""

    max_doppler_hz: float = 48000.0  # LEO worst-case
    max_doppler_rate_hz_per_s: float = 800.0
    timing_advance_range_ms: tuple[float, float] = (5.0, 25.0)  # LEO RTT range
    harq_rtt_ms: float = 40.0  # NTN extended HARQ
    max_ue_sessions: int = 200  # concurrent IoT devices

# ─── Monitor Channels ─────────────────────────────────────────

PAYLOAD_MONITOR_CHANNELS = [
    {
        "channel_name": "payload_pa_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "payload_5g",
        "nominal": (20.0, 65.0),
        "warning": (10.0, 80.0),
        "abort": (0.0, 95.0),
    },
    {
        "channel_name": "payload_pa_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "payload_5g",
        "nominal": (200.0, 1800.0),
        "warning": (100.0, 2200.0),
        "abort": (0.0, 2800.0),
    },
    {
        "channel_name": "payload_lna_bias_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "payload_5g",
        "nominal": (3.0, 3.6),
        "warning": (2.8, 3.8),
        "abort": (2.5, 4.0),
    },
    {
        "channel_name": "payload_supply_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "payload_5g",
        "nominal": (4.75, 5.25),
        "warning": (4.5, 5.5),
        "abort": (4.0, 6.0),
    },
    {
        "channel_name": "payload_supply_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "payload_5g",
        "nominal": (500.0, 3000.0),
        "warning": (200.0, 3500.0),
        "abort": (0.0, 4500.0),
    },
    {
        "channel_name": "payload_ref_clock_lock",
        "channel_type": "digital_status",
        "unit": "",
        "subsystem": "payload_5g",
        "nominal": (1.0, 1.0),
        "warning": (0.0, 1.0),
        "abort": (0.0, 1.0),
    },
    {
        "channel_name": "payload_board_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "payload_5g",
        "nominal": (10.0, 55.0),
        "warning": (0.0, 70.0),
        "abort": (-10.0, 85.0),
    },
    {
        "channel_name": "payload_fpga_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "payload_5g",
        "nominal": (20.0, 70.0),
        "warning": (10.0, 85.0),
        "abort": (0.0, 100.0),
    },
]


# ─── Test Catalog ─────────────────────────────────────────────


@dataclass(frozen=True)
class PayloadTestSpec:
    code: str
    name: str
    description: str
    estimated_duration_seconds: int
    runnable_during_stress: bool = True


PAYLOAD_TEST_CATALOG = [
    # ── TX chain tests ──────────────────────────────────────
    PayloadTestSpec(
        code="PL-TX-001",
        name="TX output power and EIRP",
        description=(
            "Measure transmitted power at PA output across all test channels "
            "(low/mid/high in DL band). Verify output power within spec at each "
            "frequency. Calculate EIRP with known antenna gain. "
            "Check power flatness across the band."
        ),
        estimated_duration_seconds=120,
    ),
    PayloadTestSpec(
        code="PL-TX-002",
        name="TX EVM measurement",
        description=(
            "Transmit known modulated signal (QPSK, then 16QAM) at each test channel. "
            "Measure Error Vector Magnitude using signal analyzer. "
            "Verify EVM below spec limit for each modulation scheme."
        ),
        estimated_duration_seconds=180,
    ),
    PayloadTestSpec(
        code="PL-TX-003",
        name="TX ACLR and spurious emissions",
        description=(
            "Transmit at rated power on each DL channel. Measure adjacent channel "
            "leakage ratio and out-of-band spurious emissions using spectrum analyzer. "
            "Verify compliance with 3GPP emission mask."
        ),
        estimated_duration_seconds=180,
    ),
    PayloadTestSpec(
        code="PL-TX-004",
        name="TX frequency accuracy",
        description=(
            "Measure TX carrier frequency error using signal analyzer. "
            "Critical for NTN where Doppler pre-compensation accuracy depends on "
            "the reference oscillator. Verify within ±0.1 ppm."
        ),
        estimated_duration_seconds=60,
    ),
    PayloadTestSpec(
        code="PL-TX-005",
        name="PA linearity (AM/AM, AM/PM)",
        description=(
            "Sweep PA input power from -30 dBm to P1dB. Measure gain compression "
            "and phase distortion at each point. Identify P1dB and IP3. "
            "Verify PA operates in linear region at rated power."
        ),
        estimated_duration_seconds=120,
        runnable_during_stress=False,
    ),
    # ── RX chain tests ──────────────────────────────────────
    PayloadTestSpec(
        code="PL-RX-001",
        name="RX sensitivity",
        description=(
            "Inject calibrated signal at decreasing power levels into RX input "
            "across all UL test channels. Measure BER at each level. "
            "Find minimum power for 1%% BER (NB-IoT) and 0.1%% BER (LTE-M). "
            "Verify sensitivity meets spec."
        ),
        estimated_duration_seconds=300,
    ),
    PayloadTestSpec(
        code="PL-RX-002",
        name="RX noise figure",
        description=(
            "Measure receiver noise figure using Y-factor method (hot/cold source). "
            "Verify LNA NF and full chain NF across operating band. "
            "Measure at low/mid/high channel frequencies."
        ),
        estimated_duration_seconds=120,
    ),
    PayloadTestSpec(
        code="PL-RX-003",
        name="RX blocking and selectivity",
        description=(
            "Inject wanted signal at sensitivity + 6 dB. Add CW blocker at "
            "specified offsets and power levels. Verify BER remains below threshold "
            "with blocker present. Test in-band and out-of-band blocking."
        ),
        estimated_duration_seconds=240,
    ),
    PayloadTestSpec(
        code="PL-RX-004",
        name="RX dynamic range",
        description=(
            "Inject signal from sensitivity level to maximum input power. "
            "Verify demodulation works across full dynamic range without "
            "saturation or AGC failure."
        ),
        estimated_duration_seconds=120,
    ),
    # ── NTN-specific tests ──────────────────────────────────
    PayloadTestSpec(
        code="PL-NTN-001",
        name="Doppler pre-compensation",
        description=(
            "Simulate Doppler shift profile (0 to ±48 kHz sweep at 800 Hz/s rate). "
            "Verify payload pre-compensates TX frequency. "
            "Measure residual frequency error at UE receiver. "
            "Must be within ±0.1 ppm after compensation."
        ),
        estimated_duration_seconds=180,
    ),
    PayloadTestSpec(
        code="PL-NTN-002",
        name="Timing advance range",
        description=(
            "Simulate varying propagation delays (5 ms to 25 ms round-trip). "
            "Verify gNB correctly handles timing advance for each delay. "
            "Check HARQ process timing with extended RTT."
        ),
        estimated_duration_seconds=120,
    ),
    PayloadTestSpec(
        code="PL-NTN-003",
        name="IoT device session lifecycle",
        description=(
            "Using UE simulator: perform full NB-IoT session lifecycle. "
            "1) Random access, 2) RRC connection, 3) Attach, 4) PDU session, "
            "5) Uplink data transfer (100 bytes), 6) Downlink data transfer, "
            "7) Detach. Verify each step completes and data integrity."
        ),
        estimated_duration_seconds=120,
    ),
    PayloadTestSpec(
        code="PL-NTN-004",
        name="Concurrent IoT session capacity",
        description=(
            "Attach IoT UE simulators incrementally (10, 50, 100, 150, 200). "
            "At each level, all UEs send 50-byte uplink. Measure throughput, "
            "latency, and error rate. Verify system handles max session count."
        ),
        estimated_duration_seconds=600,
        runnable_during_stress=False,
    ),
    # ── Integration / system-level ──────────────────────────
    PayloadTestSpec(
        code="PL-INT-001",
        name="SpaceWire command interface",
        description=(
            "Send TC commands to payload via SpaceWire from OBC. "
            "Verify: power mode transitions (standby/active/TX-only/RX-only), "
            "frequency channel change, TX power adjustment, "
            "status telemetry readback."
        ),
        estimated_duration_seconds=90,
    ),
    PayloadTestSpec(
        code="PL-INT-002",
        name="Payload power consumption profile",
        description=(
            "Measure supply current in each mode: standby, RX-only, TX-only, "
            "full duplex, full duplex + max sessions. "
            "Verify power budget matches EPS allocation."
        ),
        estimated_duration_seconds=120,
    ),
]
