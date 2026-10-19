import pytest
from src.scene import Scene, Node
from src.events import EventBus, Event
from src.automation import Director, Scheduler, Tween, Condition, interpolate

def test_hierarchy_and_paths():
    p=Node("parent")
    c=p.add(Node("child",tags={"star"},properties={"alpha":.1}))
    p.transform.x=10
    c.transform.x=5
    assert c.world_position()==(15,0)
    assert p.find(tag="star")==[c]
    c.set("properties.alpha",.7)
    assert c.get("properties.alpha")==.7
    with pytest.raises(ValueError): c.add(p)

def test_events_priority_and_unsubscription():
    bus=EventBus()
    calls=[]
    token=bus.on("hit",lambda e:calls.append("low"))
    bus.on("*",lambda e:calls.append("high"),priority=10)
    bus.queue(Event("hit"))
    assert bus.flush()==1
    assert calls==["high","low"]
    assert bus.off(token)
    bus.emit(Event("hit"))
    assert calls==["high","low","high"]

def test_scheduler_order_repeat_and_cancel():
    clock=Scheduler()
    calls=[]
    clock.after(1,lambda:calls.append("once"))
    recurring=clock.after(.5,lambda:calls.append("repeat"),repeat=.5)
    clock.update(1)
    assert calls==["repeat","once","repeat"]
    clock.cancel(recurring)
    clock.update(1)
    assert calls==["repeat","once","repeat"]

def test_tween_and_conditions():
    scene=Scene()
    director=Director()
    scene.systems.append(director)
    node=scene.add(Node("dot",properties={"color":(0,0,0)}))
    director.animate(node,"transform.x",100,1)
    director.animate(node,"properties.color",(100,50,0),1)
    events=[]
    director.when(lambda s:node.transform.x>=50,
                  lambda s:events.append(s.frame),once=True)
    scene.update(.5)
    assert node.transform.x==50
    assert node.properties["color"]==(50,25,0)
    scene.update(.5)
    assert node.transform.x==100
    assert events==[1]
    assert director.tweens==[]

def test_tween_rejects_zero_duration():
    with pytest.raises(ValueError):
        Tween(Node("x"),"transform.x",10,0)

def test_event_scene_time():
    scene=Scene()
    seen=[]
    scene.on("go",lambda e:seen.append((e.time,e.payload["n"])))
    scene.update(.25)
    scene.emit("go",n=3)
    assert seen==[(.25,3)]

def test_scheduler_negative_and_conditional_edges():
    s=Scheduler()
    with pytest.raises(ValueError):s.after(-1,lambda:None)
    scene=Scene()
    active=False
    hits=[]
    cond=Condition(lambda s:active,lambda s:hits.append(s.frame),edge="both")
    cond.update(scene)
    active=True
    cond.update(scene)
    active=False
    cond.update(scene)
    assert len(hits)==2

def test_sequence_interpolation():
    assert interpolate([0,2],[10,6],.5)==[5,4]
    with pytest.raises(ValueError):interpolate([1],[1,2],.5)
