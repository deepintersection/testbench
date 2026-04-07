"""
DUT monitoring domain — Device Under Test state machine.

State machine:
    registered → powering_up → nominal → degraded → faulted → powered_down
                                                                    ↓
                                                               registered

    registered:  DUT exists in the system, serial number and channels configured,
                 but not powered on. Board is on the bench, waiting.
    powering_up: Power supply enabled, waiting for rails to stabilize.
    nominal:     All monitor channels within nominal range. Ready for testing.
    degraded:    One or more channels in warning range. Tests may continue.
    faulted:     One or more channels in abort range. Tests must stop.
    powered_down: Cleanly shut down after testing or after fault recovery.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from testbench.shared.kernel import utc_now, generate_id

# ─── DUT State (Finding 4: StrEnum) ───────────────────────────


class DUTState(StrEnum):
    REGISTERED = "registered"
    POWERING_UP = "powering_up"
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    FAULTED = "faulted"
    POWERED_DOWN = "powered_down"


VALID_TRANSITIONS = {
    DUTState.REGISTERED: [DUTState.POWERING_UP],
    DUTState.POWERING_UP: [DUTState.NOMINAL, DUTState.FAULTED, DUTState.POWERED_DOWN],
    DUTState.NOMINAL: [DUTState.DEGRADED, DUTState.FAULTED, DUTState.POWERED_DOWN],
    DUTState.DEGRADED: [DUTState.NOMINAL, DUTState.FAULTED, DUTState.POWERED_DOWN],
    DUTState.FAULTED: [DUTState.POWERED_DOWN],
    DUTState.POWERED_DOWN: [DUTState.REGISTERED],
}


# ─── InvalidTransitionError (Finding 3: structured constructor) ─


class InvalidTransitionError(Exception):
    """Raised when a DUT state transition is not allowed.

    Accepts structured arguments so the error message is built centrally,
    not pre-formatted at each raise site.
    """

    def __init__(
        self,
        current_state: DUTState,
        target_state: DUTState,
        allowed_states: list[DUTState] | None = None,
    ):
        self.current_state = current_state
        self.target_state = target_state
        self.allowed_states = allowed_states or []
        allowed_str = ", ".join(s.value for s in self.allowed_states) or "none"
        super().__init__(
            f"Invalid transition: {current_state.value} -> {target_state.value} "
            f"(allowed from {current_state.value}: {allowed_str})"
        )


# ─── ChannelThreshold (Finding 1: __post_init__ validation) ────


@dataclass
class ChannelThreshold:
    """Three-tier threshold for a DUT monitor channel.

    Ordering invariant enforced at creation:
        abort_min ≤ warning_min ≤ nominal_min ≤ nominal_max ≤ warning_max ≤ abort_max
    """

    nominal_min: float
    nominal_max: float
    warning_min: float
    warning_max: float
    abort_min: float
    abort_max: float

    def __post_init__(self):
        if not (
            self.abort_min
            <= self.warning_min
            <= self.nominal_min
            <= self.nominal_max
            <= self.warning_max
            <= self.abort_max
        ):
            raise ValueError(
                "Threshold ordering violated: "
                "abort_min(%.4g) ≤ warning_min(%.4g) ≤ nominal_min(%.4g) ≤ "
                "nominal_max(%.4g) ≤ warning_max(%.4g) ≤ abort_max(%.4g)"
                % (
                    self.abort_min,
                    self.warning_min,
                    self.nominal_min,
                    self.nominal_max,
                    self.warning_max,
                    self.abort_max,
                )
            )

    def evaluate(self, value: float) -> str:
        """Evaluate a reading against thresholds. Assumes validated ordering."""
        if value < self.abort_min or value > self.abort_max:
            return "abort"
        if value < self.warning_min or value > self.warning_max:
            return "warning"
        if self.nominal_min <= value <= self.nominal_max:
            return "nominal"
        return "warning"


# ─── DeviceUnderTest (Finding 2: emit events on transition) ────


@dataclass
class DeviceUnderTest:
    name: str
    serial_number: str
    project_id: str
    state: DUTState = DUTState.REGISTERED
    model_type: str = ""
    hardware_revision: str = ""
    polling_interval_ms: int = 1000
    monitoring_enabled: bool = False
    state_changed_at: datetime = field(default_factory=utc_now)
    state_change_reason: str = ""
    id: str = field(default_factory=generate_id)
    domain_events: list = field(default_factory=list, repr=False)

    def transition_to(self, new_state: DUTState, reason: str = "") -> None:
        """Transition to a new state. Raises InvalidTransitionError if not allowed.

        After a successful transition, appends a DUTStateChanged event to
        self.domain_events. The application service or API layer is responsible
        for publishing these events via the EventBus and then clearing the list.
        """
        allowed = VALID_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            raise InvalidTransitionError(
                current_state=self.state,
                target_state=new_state,
                allowed_states=allowed,
            )

        old_state = self.state
        self.state = new_state
        self.state_changed_at = utc_now()
        self.state_change_reason = reason

        # Collect domain event (Finding 2)
        from testbench.dut_monitoring.domain.events import DUTStateChanged

        self.domain_events.append(
            DUTStateChanged(
                dut_id=self.id,
                from_state=old_state.value,
                to_state=new_state.value,
                reason=reason,
            )
        )

    def collect_events(self) -> list:
        """Return and clear pending domain events.

        Call this after persisting the state change:
            events = dut.collect_events()
            for event in events:
                event_bus.publish(event)
        """
        events = list(self.domain_events)
        self.domain_events.clear()
        return events

    def power_up(self):
        self.transition_to(DUTState.POWERING_UP, "Power-up initiated")

    def confirm_nominal(self):
        self.transition_to(DUTState.NOMINAL, "All channels nominal")

    def mark_degraded(self, reason: str):
        self.transition_to(DUTState.DEGRADED, reason)

    def mark_faulted(self, reason: str):
        self.transition_to(DUTState.FAULTED, reason)

    def power_down(self, reason: str = "Commanded"):
        self.transition_to(DUTState.POWERED_DOWN, reason)

    def reset_to_registered(self):
        self.transition_to(DUTState.REGISTERED, "Reset after power-down")

    @property
    def is_testable(self) -> bool:
        return self.state == DUTState.NOMINAL
