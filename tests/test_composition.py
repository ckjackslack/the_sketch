import json
import math
import pytest
from src.graph import Graph,Ref,Param
from src.signals import as_signal,oscillate,envelope,repeat,hold,bind
from src.scene import Scene,Node

def test_graph_and_roundtrip():
    g=Graph()
    a=g.add("a","multiply",a=Param("x"),b=4)
    g.add("sum","add",a=a,b=2)
    assert g.evaluate("sum",parameters={"x":3})==14
    restored=Graph.from_dict(json.loads(json.dumps(g.to_dict())))
    assert restored.evaluate("sum",parameters={"x":3})==14

def test_graph_rejects_cycle():
    g=Graph()
    g.add("a","add",a=Ref("b"),b=1)
    g.add("b","add",a=Ref("a"),b=1)
    with pytest.raises(ValueError):g.evaluate("a")

def test_graph_missing_dependencies():
    g=Graph();g.add("a","add",a=Ref("missing"),b=1)
    with pytest.raises(KeyError):g.evaluate("a")

def test_type_validation():
    g=Graph();g.add("a","add",a="bad",b=4)
    with pytest.raises(TypeError):g.evaluate("a")

def test_signal_composition():
    s=oscillate(.25,amplitude=2,offset=3)
    assert math.isclose(s.at(1),5)
    assert math.isclose((s*2+1).at(1),11)
    assert envelope([(0,0),(2,10)]).at(1)==5
    assert repeat(envelope([(0,0),(1,10)]),2).at(2.5)==5
    assert hold(envelope([(0,0),(2,10)]),1).at(1.8)==5

def test_signal_bindings():
    scene=Scene();node=scene.add(Node("n"))
    bind(scene,node,"transform.x",envelope([(0,0),(2,20)]))
    scene.update(1)
    assert node.transform.x==10

def test_invalid_graph_operator_and_keyframes():
    g=Graph()
    with pytest.raises(KeyError):g.add("x","imaginary",value=1)
    with pytest.raises(ValueError):envelope([])
    with pytest.raises(ValueError):envelope([(1,2),(1,3)])
