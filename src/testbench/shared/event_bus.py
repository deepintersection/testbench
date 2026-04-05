from __future__ import annotations
import logging
from collections import defaultdict
from typing import Callable, Type
from testbench.shared.kernel import DomainEvent

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._handlers: dict[Type[DomainEvent], list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            try:
                handler(event)
            except Exception:
                logger.exception("Handler %s failed", handler.__qualname__)

    def clear(self) -> None:
        self._handlers.clear()


event_bus = EventBus()
