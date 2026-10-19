"""Temporal and conditional automation: scheduling, tweening, triggers, behaviors."""
from __future__ import annotations
from dataclasses import dataclass, field
from heapq import heappush, heappop
from itertools import count
from typing import Callable, Any
from .creative import lerp, clamp, ease_in_out
from .scene import Scene, Node

def interpolate(a, b, t):
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        if len(a) != len(b):
            raise ValueError("sequences must have same length")
        return type(a)(interpolate(x, y, t) for x, y in zip(a, b))
    return lerp(a, b, t)

@dataclass
class Tween:
    target: Node
    path: str
    end: Any
    duration: float
    easing: Callable[[float], float] = ease_in_out
    start: Any = None
    elapsed: float = 0.0
    finished: bool = False
    on_complete: Callable[[Node], None] | None = None

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("duration must be positive")
        if self.start is None:
            self.start = self.target.get(self.path)

    def update(self, dt):
        if self.finished:
            return
        self.elapsed = min(self.duration, self.elapsed+dt)
        value = interpolate(self.start, self.end, self.easing(clamp(self.elapsed/self.duration)))
        self.target.set(self.path, value)
        if self.elapsed >= self.duration:
            self.finished = True
            if self.on_complete:
                self.on_complete(self.target)

@dataclass
class Condition:
    predicate: Callable[[Scene], bool]
    action: Callable[[Scene], None]
    edge: str = "rising"
    once: bool = False
    previous: bool = False
    fired: bool = False

    def __post_init__(self):
        if self.edge not in {"rising","falling","both","level"}:
            raise ValueError("edge must be rising, falling, both or level")

    def update(self, scene):
        if self.once and self.fired:
            return
        now = bool(self.predicate(scene))
        fire = ((self.edge == "level" and now)
                or (self.edge == "rising" and now and not self.previous)
                or (self.edge == "falling" and not now and self.previous)
                or (self.edge == "both" and now != self.previous))
        self.previous = now
        if fire:
            self.fired = True
            self.action(scene)

@dataclass(order=True)
class _Task:
    at: float
    serial: int
    action: Callable = field(compare=False)
    repeat: float | None = field(default=None, compare=False)
    cancelled: bool = field(default=False, compare=False)

class Scheduler:
    """Deterministic simulation-clock scheduling, not wall-clock timers."""
    def __init__(self):
        self.now = 0.0
        self._tasks = []
        self._serial = count()

    def at(self, time: float, action, repeat=None):
        if time < self.now:
            raise ValueError("scheduled time cannot be in the past")
        if repeat is not None and repeat <= 0:
            raise ValueError("repeat interval must be positive")
        task = _Task(time, next(self._serial), action, repeat)
        heappush(self._tasks, task)
        return task

    def after(self, delay: float, action, repeat=None):
        if delay < 0:
            raise ValueError("delay must be nonnegative")
        return self.at(self.now + delay, action, repeat)

    def cancel(self, task):
        task.cancelled = True

    def update(self, dt: float, limit=10000):
        if dt < 0:
            raise ValueError("dt must be nonnegative")
        self.now += dt
        executions = 0
        while self._tasks and self._tasks[0].at <= self.now and executions < limit:
            task = heappop(self._tasks)
            if task.cancelled:
                continue
            executions += 1
            task.action()
            if task.repeat is not None and not task.cancelled:
                task.at += task.repeat
                heappush(self._tasks, task)
        if self._tasks and self._tasks[0].at <= self.now:
            raise RuntimeError("scheduler execution limit reached")
        return executions

class Director:
    """Install as scene.systems.append(director). Order: scheduler -> tweens -> conditions."""
    def __init__(self):
        self.scheduler = Scheduler()
        self.tweens: list[Tween] = []
        self.conditions: list[Condition] = []

    def animate(self, target, path, end, duration, **kwargs):
        tween = Tween(target, path, end, duration, **kwargs)
        self.tweens.append(tween)
        return tween

    def when(self, predicate, action, *, edge="rising", once=False):
        condition = Condition(predicate, action, edge=edge, once=once)
        self.conditions.append(condition)
        return condition

    def __call__(self, scene, dt):
        self.scheduler.update(dt)
        for tween in tuple(self.tweens):
            tween.update(dt)
        self.tweens = [t for t in self.tweens if not t.finished]
        for condition in tuple(self.conditions):
            condition.update(scene)
        self.conditions = [c for c in self.conditions if not (c.once and c.fired)]
