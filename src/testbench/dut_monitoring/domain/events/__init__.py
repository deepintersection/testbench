from dataclasses import dataclass
from testbench.shared.kernel import DomainEvent


@dataclass(frozen=True)
class DUTStateChanged(DomainEvent):
    dut_id: str = ""
    from_state: str = ""
    to_state: str = ""
    reason: str = ""


@dataclass(frozen=True)
class DUTFaultDetected(DomainEvent):
    dut_id: str = ""
    channel_name: str = ""
    value: float = 0.0
    abort_threshold: float = 0.0
    reason: str = ""


@dataclass(frozen=True)
class ChannelWarning(DomainEvent):
    dut_id: str = ""
    channel_name: str = ""
    value: float = 0.0
    warning_threshold: float = 0.0


@dataclass(frozen=True)
class SnapshotCaptured(DomainEvent):
    dut_id: str = ""
    snapshot_id: str = ""
    trigger: str = ""
    dut_state: str = ""
