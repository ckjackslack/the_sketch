"""Deterministic typed, serializable dataflow graph.

Nodes evaluate at a simulation time. Explicit inputs reference constants,
external parameters, or other nodes. DAGs are evaluated once per frame.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import math

@dataclass(frozen=True)
class Ref:
    node: str

@dataclass(frozen=True)
class Param:
    name: str

@dataclass
class Operator:
    fn: Callable
    inputs: dict[str, type] = field(default_factory=dict)
    output: type = object

OPERATORS: dict[str, Operator] = {}

def register(name, fn, inputs=None, output=object):
    if not name or name in OPERATORS:
        raise ValueError("duplicate or empty operator name")
    OPERATORS[name] = Operator(fn, inputs or {}, output)

@dataclass
class GraphNode:
    name: str
    operator: str
    inputs: dict[str, Any] = field(default_factory=dict)

class Graph:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}

    def add(self, name, operator, **inputs):
        if name in self.nodes:
            raise ValueError(f"duplicate node: {name}")
        if operator not in OPERATORS:
            raise KeyError(f"unknown operator: {operator}")
        expected = OPERATORS[operator].inputs
        if set(inputs) != set(expected):
            raise ValueError(f"{operator}: expected {sorted(expected)}, got {sorted(inputs)}")
        self.nodes[name] = GraphNode(name, operator, inputs)
        return Ref(name)

    def _order(self, target):
        visited, active, ordered = set(), set(), []
        def visit(name):
            if name in active:
                raise ValueError(f"dependency cycle at {name}")
            if name in visited:
                return
            if name not in self.nodes:
                raise KeyError(f"missing dependency: {name}")
            active.add(name)
            for item in self.nodes[name].inputs.values():
                if isinstance(item, Ref):
                    visit(item.node)
            active.remove(name)
            visited.add(name)
            ordered.append(name)
        visit(target)
        return ordered

    def evaluate(self, target, *, time=0., parameters=None):
        if not math.isfinite(time):
            raise ValueError("time must be finite")
        parameters = {} if parameters is None else parameters
        cache = {}
        for name in self._order(target):
            node = self.nodes[name]
            op = OPERATORS[node.operator]
            args = {}
            for key, source in node.inputs.items():
                value = (cache[source.node] if isinstance(source, Ref) else
                         parameters[source.name] if isinstance(source, Param) else source)
                typ = op.inputs[key]
                if typ is not object and not isinstance(value, typ):
                    raise TypeError(f"{name}.{key}: expected {getattr(typ, "__name__", " or ".join(t.__name__ for t in typ))}, got {type(value).__name__}")
                args[key] = value
            result = op.fn(**args)
            if op.output is not object and not isinstance(result, op.output):
                raise TypeError(f"{name}: output must be {op.output.__name__}")
            cache[name] = result
        return cache[target]

    def to_dict(self):
        def encode(v):
            if isinstance(v, Ref): return {"$ref":v.node}
            if isinstance(v, Param): return {"$param":v.name}
            if isinstance(v, (int,float,str,bool)) or v is None: return v
            if isinstance(v, (tuple,list)): return [encode(x) for x in v]
            if isinstance(v, dict): return {k:encode(x) for k,x in v.items()}
            raise TypeError(f"unserializable value: {type(v).__name__}")
        return {"version":1,"nodes":[{"name":n.name,"operator":n.operator,
                "inputs":{k:encode(v) for k,v in n.inputs.items()}}
                for n in self.nodes.values()]}

    @classmethod
    def from_dict(cls, data):
        if data.get("version") != 1:
            raise ValueError("unsupported graph version")
        def decode(v):
            if isinstance(v,dict):
                if set(v)=={"$ref"}: return Ref(v["$ref"])
                if set(v)=={"$param"}: return Param(v["$param"])
                return {k:decode(x) for k,x in v.items()}
            if isinstance(v,list): return [decode(x) for x in v]
            return v
        graph = cls()
        for entry in data["nodes"]:
            graph.add(entry["name"],entry["operator"],**{k:decode(v) for k,v in entry["inputs"].items()})
        for name in graph.nodes:
            graph._order(name)
        return graph

register("add",lambda a,b:a+b,{"a":(int,float),"b":(int,float)})
register("multiply",lambda a,b:a*b,{"a":(int,float),"b":(int,float)})
register("sine",lambda x:math.sin(x),{"x":(int,float)},float)
register("mix",lambda a,b,t:a+(b-a)*t,{"a":(int,float),"b":(int,float),"t":(int,float)})
register("clamp",lambda x,lo,hi:max(lo,min(hi,x)),{"x":(int,float),"lo":(int,float),"hi":(int,float)})
