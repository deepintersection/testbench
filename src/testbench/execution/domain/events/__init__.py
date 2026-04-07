from dataclasses import dataclass
from testbench.shared.kernel import DomainEvent


@dataclass(frozen=True)
class TestStarted(DomainEvent):
    test_run_id: str = ""
    test_definition_code: str = ""
    campaign_id: str = ""
    dut_id: str = ""


@dataclass(frozen=True)
class MeasurementTaken(DomainEvent):
    test_run_id: str = ""
    parameter_name: str = ""
    measured_value: float = 0.0
    unit: str = ""
    verdict: str = ""


@dataclass(frozen=True)
class VerdictReached(DomainEvent):
    test_run_id: str = ""
    test_definition_code: str = ""
    campaign_id: str = ""
    verdict: str = ""
    dut_health_at_verdict: str = ""


@dataclass(frozen=True)
class DriftDetected(DomainEvent):
    test_definition_code: str = ""
    parameter_name: str = ""
    baseline_value: float = 0.0
    current_value: float = 0.0
    drift_percent: float = 0.0
    unit: str = ""


@dataclass(frozen=True)
class TestAborted(DomainEvent):
    test_run_id: str = ""
    reason: str = ""
