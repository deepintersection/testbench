from dataclasses import dataclass
from testbench.shared.kernel import DomainEvent


@dataclass(frozen=True)
class CampaignStarted(DomainEvent):
    campaign_id: str = ""
    project_id: str = ""
    stress_type: str = ""
    stress_phase: str = ""


@dataclass(frozen=True)
class StressPhaseChanged(DomainEvent):
    campaign_id: str = ""
    from_phase: str = ""
    to_phase: str = ""


@dataclass(frozen=True)
class CampaignCompleted(DomainEvent):
    campaign_id: str = ""
    project_id: str = ""
    total_runs: int = 0
    passed: int = 0
    failed: int = 0
