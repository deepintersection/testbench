from dataclasses import dataclass
from testbench.shared.kernel import DomainEvent


@dataclass(frozen=True)
class ProjectCreated(DomainEvent):
    project_id: str = ""
    project_code: str = ""


@dataclass(frozen=True)
class PhaseAdvanced(DomainEvent):
    project_id: str = ""
    phase_id: str = ""
    phase_type: str = ""
    sequence_number: int = 0


@dataclass(frozen=True)
class SubsystemIntegrated(DomainEvent):
    project_id: str = ""
    phase_id: str = ""
    subsystem_type: str = ""
