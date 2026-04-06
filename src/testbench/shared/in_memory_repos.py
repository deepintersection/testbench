"""
In-memory repository implementations — zero infrastructure dependency.

Percival pattern: use these for domain-level unit tests where you want
to verify business logic without touching a database. Fast, deterministic,
no setup required.

    from testbench.shared.in_memory_repos import InMemoryTestDefinitionRepository
    repo = InMemoryTestDefinitionRepository()
    seed_rcu_test_definitions(repo)
    assert repo.exists("RCU-SPW-001")
"""

from __future__ import annotations
from testbench.shared.kernel import TestDefinitionRepository, MonitorChannelRepository


class InMemoryTestDefinitionRepository(TestDefinitionRepository):

    def __init__(self):
        self._store: dict[str, dict] = {}

    def find_by_code(self, code: str) -> dict | None:
        return self._store.get(code)

    def find_by_scope(self, subsystem_scope: str) -> list[dict]:
        return [
            v for v in self._store.values() if v["subsystem_scope"] == subsystem_scope
        ]

    def exists(self, code: str) -> bool:
        return code in self._store

    def save(
        self,
        code: str,
        name: str,
        description: str,
        subsystem_scope: str,
        estimated_duration_seconds: int,
        runnable_during_stress: bool = True,
    ) -> None:
        if code in self._store:
            return
        self._store[code] = {
            "code": code,
            "name": name,
            "description": description,
            "subsystem_scope": subsystem_scope,
            "estimated_duration_seconds": estimated_duration_seconds,
            "runnable_during_stress": runnable_during_stress,
        }


class InMemoryMonitorChannelRepository(MonitorChannelRepository):

    def __init__(self):
        self._store: dict[tuple[str, str], dict] = {}

    def find_by_dut(self, dut_id: str, channel_name: str) -> dict | None:
        return self._store.get((dut_id, channel_name))

    def save_channel(
        self,
        dut_id: str,
        channel_name: str,
        channel_type: str,
        unit: str,
        subsystem: str,
        nominal: tuple[float, float],
        warning: tuple[float, float],
        abort: tuple[float, float],
        context: str = "ambient",
    ) -> None:
        key = (dut_id, channel_name)
        if key in self._store:
            return
        self._store[key] = {
            "channel_name": channel_name,
            "channel_type": channel_type,
            "unit": unit,
            "subsystem": subsystem,
            "nominal": nominal,
            "warning": warning,
            "abort": abort,
        }
