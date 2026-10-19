# Scene orchestration and automation

Three new modules: `src.scene`, `src.events`, `src.automation`. All timings use simulation seconds, not wall-clock time; processing is deterministic with a fixed `dt`.

## Object model

- `Node(name, transform=..., properties={...}, tags={...})`: hierarchical scene object; `add/remove/walk/find`, path-based `get/set`, arbitrary named components and world-space position.
- `Scene`: root, event bus, systems, frame and time counters; `update(dt)`, `run(steps, dt)`, `find`, `emit`, `on`.
- `Event`: immutable envelope with topic, payload, source and simulation timestamp.
- `EventBus`: prioritized listeners, wildcard subscriptions, unsubscribe tokens, queued dispatch, event history.

## Orchestration

- `Scheduler.after(seconds, callback, repeat=...)`, `at(time, callback)`, `cancel(task)`.
- `Tween(node, "transform.x", value, duration, easing=...)` for continuous property animation. Supports nested properties and tuple/list interpolation.
- `Condition(predicate, action, edge="rising", once=False)` for state-based triggers. Edge modes: rising, falling, both, level.
- `Director`: composes scheduler, active tweens and conditions into a scene system.

## Complete example

```python
from src.scene import Scene, Node
from src.automation import Director

scene = Scene()
director = Director()
scene.systems.append(director)
sun = scene.add(Node("sun", tags={"celestial"}, properties={"radius": 10}))

scene.on("bright", lambda event: sun.set("properties.radius", 50))
director.scheduler.after(2, lambda: scene.emit("bright"))
director.animate(sun, "transform.x", 300, duration=5)
director.when(lambda s: sun.transform.x >= 200,
              lambda s: s.emit("milestone"), once=True)
scene.run(300, dt=1/60)
```

## Rendering example

```bash
python -m src render choreography --frames 180 --fps 30 -o choreography.gif
```

The example uses animated scene nodes, repeating pulses, a conditional finale, and event listeners.

## Design notes

All callbacks execute synchronously. Exceptions propagate to the caller. `Scheduler` catches up missed repeat ticks after large time steps and protects against runaway callbacks with a processing limit. Node references can be moved between parents; avoid mutating graph hierarchies while iterating without a snapshot. Systems run in their insertion order, then queued events are flushed. `Director` processes scheduler -> tweens -> conditions.

This package deliberately does not impose a new GUI or rendering backend. Integrate into any existing Pillow Sketch via `setup/update/draw`.
