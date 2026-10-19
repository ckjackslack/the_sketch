"""Scene graph: controllable objects, hierarchical transforms, tags, components."""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import count
from typing import Any
from .events import Event, EventBus

_ids = count(1)

@dataclass
class Transform:
    x: float = 0
    y: float = 0
    rotation: float = 0
    scale_x: float = 1
    scale_y: float = 1

@dataclass
class Node:
    name: str
    transform: Transform = field(default_factory=Transform)
    properties: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    visible: bool = True
    enabled: bool = True
    id: int = field(default_factory=lambda: next(_ids), init=False)
    parent: Node | None = field(default=None, init=False, repr=False)
    children: list[Node] = field(default_factory=list, init=False, repr=False)
    components: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def add(self, child: Node) -> Node:
        if child is self or self.is_descendant_of(child):
            raise ValueError("cyclic scene graph")
        if child.parent is not None:
            child.parent.remove(child)
        if child not in self.children:
            self.children.append(child)
        child.parent = self
        return child

    def remove(self, child: Node) -> None:
        self.children.remove(child)
        child.parent = None

    def is_descendant_of(self, ancestor: Node) -> bool:
        current = self.parent
        while current is not None:
            if current is ancestor:
                return True
            current = current.parent
        return False

    def walk(self):
        yield self
        for child in tuple(self.children):
            yield from child.walk()

    def find(self, name=None, tag=None):
        return [n for n in self.walk() if (name is None or n.name == name)
                and (tag is None or tag in n.tags)]

    def attach(self, name: str, component):
        self.components[name] = component
        return self

    def get(self, path: str):
        current = self
        for part in path.split("."):
            current = current[part] if isinstance(current, dict) else getattr(current, part)
        return current

    def set(self, path: str, value):
        parts = path.split(".")
        if not parts or any(not p for p in parts):
            raise ValueError("invalid property path")
        target = self
        for part in parts[:-1]:
            target = target[part] if isinstance(target, dict) else getattr(target, part)
        if isinstance(target, dict):
            target[parts[-1]] = value
        else:
            if not hasattr(target, parts[-1]):
                raise AttributeError(parts[-1])
            setattr(target, parts[-1], value)
        return self

    def world_position(self):
        """Accumulate parent translation, rotation and scale into a world position."""
        import math
        x, y = self.transform.x, self.transform.y
        parent = self.parent
        while parent is not None:
            t = parent.transform
            x, y = (x*t.scale_x, y*t.scale_y)
            x, y = (x*math.cos(t.rotation)-y*math.sin(t.rotation),
                    x*math.sin(t.rotation)+y*math.cos(t.rotation))
            x += t.x
            y += t.y
            parent = parent.parent
        return x, y

class Scene:
    def __init__(self, name="scene"):
        self.root = Node(name)
        self.events = EventBus()
        self.time = 0.0
        self.frame = 0
        self.systems = []

    def add(self, node: Node):
        return self.root.add(node)

    def find(self, **filters):
        return self.root.find(**filters)

    def on(self, topic, callback, priority=0):
        return self.events.on(topic, callback, priority)

    def emit(self, name, *, source=None, **payload):
        self.events.emit(Event(name, source=source, payload=payload, time=self.time))

    def update(self, dt: float):
        if dt < 0:
            raise ValueError("dt must be nonnegative")
        self.time += dt
        self.frame += 1
        for system in tuple(self.systems):
            system(self, dt)
        self.events.flush()

    def run(self, steps: int, dt=1/60):
        if steps < 0:
            raise ValueError("steps must be nonnegative")
        for _ in range(steps):
            self.update(dt)
        return self
