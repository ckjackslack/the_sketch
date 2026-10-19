# Composition core

Three new domains:

- **Graph**: dependency-ordered operator graph with typed input validation, cycle detection, constant values, external parameter references and JSON-compatible serialization.
- **Signal**: continuous time functions with arithmetic combinators, envelopes, repeat/sample-and-hold and bindings to scene properties.
- **Showcases**: signal garden, graph mandala and flow constellation compositions.

```python
from src.graph import Graph, Ref, Param
g = Graph()
wave = g.add("wave", "sine", x=Param("phase"))
g.add("luminance", "multiply", a=wave, b=0.5)
print(g.evaluate("luminance", parameters={"phase":1.57}))
recipe = g.to_dict()
restored = Graph.from_dict(recipe)
```

```python
from src.scene import Scene, Node
from src.signals import oscillate, bind
scene = Scene()
object = scene.add(Node("orb"))
bind(scene, object, "transform.x", oscillate(.2, amplitude=100, offset=200))
scene.run(120, dt=1/60)
```

Render showcases with the CLI:

```bash
python -m src render signal-garden -o garden.gif --frames 120
python -m src render graph-mandala -o mandala.gif --frames 120
python -m src render flow-constellation -o constellation.gif --frames 120
```

Important design details: Operators are explicitly registered in the Python process; serialized graphs contain operator names and data, **never executable Python source**. Deserialization rejects unknown names and cycles. Only explicitly registered operators are callable. Signal objects are programmatic and intentionally not serialized. Time is simulation time, not wall time.
