import math
import pytest
from src.world import World,Vector,SpatialHash
from src.behaviors import seek,flee,separate,align,cohere,wander
from src.machines import StateMachine

def test_vector_operations():
    assert Vector(3,4).magnitude()==5
    assert Vector().normalized()==Vector()
    assert Vector(10,0).limited(2)==Vector(2,0)

def test_seed_reproducibility():
    def sample():
        w=World(100,100,seed=22)
        for _ in range(12):w.spawn(behaviors=[wander(.5)])
        w.run(15)
        return [(a.position,a.velocity) for a in w.agents]
    assert sample()==sample()

def test_spatial_hash_negative_cells():
    w=SpatialHash(10)
    a=World().spawn(position=Vector(-2,-3))
    w.rebuild([a])
    assert w.query(Vector(0,0),5)==[a]

def test_neighbors_and_steering():
    w=World(200,200)
    a=w.spawn(Vector(10,10))
    b=w.spawn(Vector(15,10))
    w.index.rebuild(w.agents)
    assert w.neighbors(a,6)==[b]
    assert seek(Vector(100,10))(w,a).x>0
    assert flee(Vector(100,10))(w,a).x<0
    assert separate(20)(w,a).x<0
    assert align(20)(w,a)==Vector()
    assert cohere(20)(w,a).x>0

def test_collision_events():
    w=World(100,100)
    w.spawn(Vector(40,40),radius=8)
    w.spawn(Vector(45,40),radius=8)
    hits=[]
    w.events.on("collision",lambda event:hits.append(event))
    w.step()
    assert len(hits)==1
    assert hits[0].payload["a"].id!=hits[0].payload["b"].id

def test_bounce_and_wrap():
    w=World(100,100,boundary="wrap")
    a=w.spawn(Vector(99,50),velocity=Vector(10,0))
    w.step(.5)
    assert a.position.x<99
    b=World(100,100,boundary="bounce").spawn(Vector(98,50),velocity=Vector(10,0))
    # Standalone agent's world used for update:
    assert b.position.x==98
    bounce=World(100,100,boundary="bounce")
    b=bounce.spawn(Vector(98,50),velocity=Vector(10,0))
    bounce.step(.5)
    assert b.velocity.x<0

def test_state_machine():
    f=StateMachine("idle")
    log=[]
    f.on_enter["running"]=lambda x:log.append("enter")
    f.add("idle","running",lambda x:x>3)
    assert not f.step(1)
    assert f.step(4)
    assert f.state=="running" and log==["enter"]

@pytest.mark.parametrize("dt",[0,-1,float("nan")])
def test_invalid_dt(dt):
    with pytest.raises(ValueError):World().step(dt)
