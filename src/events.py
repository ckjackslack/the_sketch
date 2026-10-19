"""Typed event envelopes, deterministic dispatch and subscriptions."""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass(frozen=True)
class Event:
    name: str
    source: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    time: float = 0.0

@dataclass(frozen=True)
class Subscription:
    topic: str
    token: int

class EventBus:
    """Priority-aware synchronous events with safe listener mutation and queued delivery."""
    def __init__(self):
        self._listeners: dict[str, dict[int, tuple[int, Callable]]] = defaultdict(dict)
        self._serial = 0
        self._queue = deque()
        self.history: list[Event] = []

    def on(self, topic: str, handler: Callable[[Event], None], priority=0) -> Subscription:
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._serial += 1
        self._listeners[topic][self._serial] = (priority, handler)
        return Subscription(topic, self._serial)

    def off(self, subscription: Subscription) -> bool:
        return self._listeners[subscription.topic].pop(subscription.token, None) is not None

    def emit(self, event: Event) -> None:
        self.history.append(event)
        snapshot = [(priority, token, callback)
                    for topic in (event.name, "*")
                    for token, (priority, callback) in self._listeners.get(topic, {}).items()]
        for _, token, handler in sorted(snapshot, key=lambda x: (-x[0], x[1])):
            # Unsubscribed callbacks don't fire later in the same dispatch.
            if any(token in listeners for listeners in self._listeners.values()):
                handler(event)

    def queue(self, event: Event) -> None:
        self._queue.append(event)

    def flush(self, limit=10000) -> int:
        if limit < 1:
            raise ValueError("limit must be positive")
        processed = 0
        while self._queue and processed < limit:
            self.emit(self._queue.popleft())
            processed += 1
        if self._queue:
            raise RuntimeError("event queue exceeded flush limit; pending events retained")
        return processed

    def clear_history(self):
        self.history.clear()
