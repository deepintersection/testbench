"""
RCU (Remote Control Unit) subsystem domain.

Ubiquitous language:
    - RCU: the device under test, an OBC-class board with SpaceWire
    - RMAP: Remote Memory Access Protocol over SpaceWire
    - HK: Housekeeping telemetry
    - TC/TM: Telecommand / Telemetry
    - Boot sequence: power-on -> bootloader -> OBSW -> ready
    - Watchdog: hardware timer that resets the RCU if not kicked
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

# ─── RCU Boot States ──────────────────────────────────────────


class RCUBootState(str, Enum):
    OFF = "off"
    BOOTLOADER = "bootloader"
    LOADING_OBSW = "loading_obsw"
    OBSW_RUNNING = "obsw_running"
    READY = "ready"
    SAFE_MODE = "safe_mode"


# ─── Memory Map ───────────────────────────────────────────────


@dataclass(frozen=True)
class MemoryRegion:
    """A named region in the RCU address space, accessible via RMAP."""

    name: str
    base_address: int
    size_bytes: int
    access: str = "rw"  # "ro", "rw", "wo"
    description: str = ""

    @property
    def end_address(self) -> int:
        return self.base_address + self.size_bytes - 1


# Standard RCU memory map (adjust per actual hardware)
RCU_MEMORY_MAP = [
    MemoryRegion("bootloader_rom", 0x00000000, 0x00010000, "ro", "Bootloader ROM 64KB"),
    MemoryRegion("obsw_flash", 0x00010000, 0x00080000, "rw", "OBSW flash 512KB"),
    MemoryRegion("sram_main", 0x20000000, 0x00040000, "rw", "Main SRAM 256KB"),
    MemoryRegion("sram_hk", 0x20040000, 0x00004000, "rw", "HK telemetry buffer 16KB"),
    MemoryRegion("tc_mailbox", 0x20050000, 0x00001000, "rw", "Telecommand mailbox 4KB"),
    MemoryRegion("tm_mailbox", 0x20051000, 0x00001000, "ro", "Telemetry mailbox 4KB"),
    MemoryRegion("registers", 0x40000000, 0x00001000, "rw", "Peripheral registers 4KB"),
    MemoryRegion(
        "watchdog_reg", 0x40001000, 0x00000010, "rw", "Watchdog control registers"
    ),
]


# ─── RCU Housekeeping Telemetry ───────────────────────────────


@dataclass
class RCUHousekeeping:
    """Parsed HK telemetry packet from the RCU."""

    boot_state: RCUBootState
    uptime_seconds: int
    cpu_temperature_celsius: float
    supply_voltage_v: float
    supply_current_ma: float
    spw_link_status: int  # 1=Run, 0=other
    spw_error_count: int
    watchdog_remaining_ms: int
    obsw_version: str = ""
    error_flags: int = 0


# ─── RCU Monitor Channel Definitions ─────────────────────────

RCU_MONITOR_CHANNELS = [
    {
        "channel_name": "rcu_supply_voltage",
        "channel_type": "voltage",
        "unit": "V",
        "subsystem": "rcu",
        "nominal": (3.135, 3.465),
        "warning": (3.0, 3.6),
        "abort": (2.8, 3.8),
    },
    {
        "channel_name": "rcu_supply_current",
        "channel_type": "current",
        "unit": "mA",
        "subsystem": "rcu",
        "nominal": (50.0, 500.0),
        "warning": (20.0, 700.0),
        "abort": (0.0, 1000.0),
    },
    {
        "channel_name": "rcu_cpu_temperature",
        "channel_type": "temperature",
        "unit": "°C",
        "subsystem": "rcu",
        "nominal": (10.0, 60.0),
        "warning": (0.0, 75.0),
        "abort": (-10.0, 90.0),
    },
    {
        "channel_name": "rcu_spw_link_status",
        "channel_type": "digital_status",
        "unit": "",
        "subsystem": "rcu",
        "nominal": (1.0, 1.0),
        "warning": (0.0, 1.0),
        "abort": (0.0, 1.0),
    },
    {
        "channel_name": "rcu_spw_error_count",
        "channel_type": "error_count",
        "unit": "",
        "subsystem": "rcu",
        "nominal": (0.0, 0.0),
        "warning": (0.0, 10.0),
        "abort": (0.0, 100.0),
    },
    {
        "channel_name": "rcu_watchdog_remaining",
        "channel_type": "custom",
        "unit": "ms",
        "subsystem": "rcu",
        "nominal": (100.0, 5000.0),
        "warning": (50.0, 5000.0),
        "abort": (0.0, 5000.0),
    },
]


# ─── RCU Test Definitions ────────────────────────────────────


@dataclass(frozen=True)
class RCUTestSpec:
    """Specification for a single RCU test — used to seed TestDefinitionRow."""

    code: str
    name: str
    description: str
    estimated_duration_seconds: int
    runnable_during_stress: bool = True


RCU_TEST_CATALOG = [
    # SpaceWire link tests
    RCUTestSpec(
        code="RCU-SPW-001",
        name="SpaceWire link initialization",
        description=(
            "Power on RCU, verify SpaceWire link reaches Run state within timeout. "
            "Measure actual link speed and compare to expected. "
            "Check error counters are zero after init."
        ),
        estimated_duration_seconds=30,
    ),
    RCUTestSpec(
        code="RCU-SPW-002",
        name="SpaceWire link speed negotiation",
        description=(
            "Test link operation at 10, 50, 100, 200 Mbps. "
            "Verify error-free operation at each speed for 10 seconds. "
            "Measure actual achieved bit rate."
        ),
        estimated_duration_seconds=120,
    ),
    RCUTestSpec(
        code="RCU-SPW-003",
        name="SpaceWire error recovery",
        description=(
            "Inject disconnect error on SpW link. "
            "Verify RCU detects, recovers, and re-establishes link. "
            "Measure recovery time."
        ),
        estimated_duration_seconds=60,
    ),
    # Memory tests via RMAP
    RCUTestSpec(
        code="RCU-MEM-001",
        name="SRAM read/write integrity",
        description=(
            "Write known patterns (0x55, 0xAA, walking 1s, walking 0s, address-as-data) "
            "to SRAM via RMAP. Read back and verify. "
            "Covers sram_main and sram_hk regions."
        ),
        estimated_duration_seconds=60,
    ),
    RCUTestSpec(
        code="RCU-MEM-002",
        name="RMAP read speed benchmark",
        description=(
            "Measure RMAP read throughput: read 256KB from sram_main in 1KB blocks. "
            "Calculate effective data rate. Compare to SpaceWire link speed."
        ),
        estimated_duration_seconds=30,
    ),
    RCUTestSpec(
        code="RCU-MEM-003",
        name="RMAP write speed benchmark",
        description=(
            "Measure RMAP write throughput: write 256KB to sram_main in 1KB blocks. "
            "Read back and verify. Calculate effective data rate."
        ),
        estimated_duration_seconds=30,
    ),
    RCUTestSpec(
        code="RCU-MEM-004",
        name="Flash memory read-only verification",
        description=(
            "Read bootloader ROM via RMAP. Compute CRC-32 and compare to known good. "
            "Verify OBSW flash CRC."
        ),
        estimated_duration_seconds=20,
    ),
    # Boot and command tests
    RCUTestSpec(
        code="RCU-BOOT-001",
        name="Boot sequence timing",
        description=(
            "Power cycle RCU. Measure time from power-on to: "
            "bootloader entry, OBSW load start, OBSW running, ready state. "
            "Verify all within specification."
        ),
        estimated_duration_seconds=45,
    ),
    RCUTestSpec(
        code="RCU-CMD-001",
        name="Telecommand interface",
        description=(
            "Send standardized telecommands via SpaceWire to tc_mailbox. "
            "Verify RCU acknowledges each TC. "
            "Test: NOP, ping, HK request, safe mode entry/exit."
        ),
        estimated_duration_seconds=60,
    ),
    RCUTestSpec(
        code="RCU-TM-001",
        name="Housekeeping telemetry readback",
        description=(
            "Request HK telemetry packet via RMAP read of tm_mailbox. "
            "Parse and validate all fields. "
            "Verify voltage, current, temperature against monitor channels."
        ),
        estimated_duration_seconds=30,
    ),
    # Watchdog test
    RCUTestSpec(
        code="RCU-WDG-001",
        name="Watchdog timeout and recovery",
        description=(
            "Stop kicking the watchdog. Verify RCU resets within specified timeout. "
            "Measure actual reset time. Verify clean reboot after watchdog reset."
        ),
        estimated_duration_seconds=90,
        runnable_during_stress=False,  # Don't run during vibration
    ),
]
