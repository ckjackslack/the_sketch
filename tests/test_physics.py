import pytest
from src.physics import PhysicsWorld,Body,DistanceConstraint,Spring,Vector,radial_force,vortex_force

def test_distance_constraint_with_pinned_body():
    a=Body(Vector(0,0),pinned=True)
    b=Body(Vector(20,0))
    c=DistanceConstraint(a,b,10)
    c.solve()
    assert a.position==Vector(0,0)
    assert abs(b.position.x-10)<1e-8

def test_distance_constraint_two_free_bodies():
    a,b=Body(Vector(0,0)),Body(Vector(20,0))
    DistanceConstraint(a,b,10).solve()
    assert abs((b.position-a.position).magnitude()-10)<1e-8

def test_spring_attraction():
    a=Body(Vector(0,0),pinned=True)
    b=Body(Vector(50,0))
    w=PhysicsWorld(300,300,gravity=Vector(),resolve_collisions=False)
    w.add(a);w.add(b);w.spring(a,b,20,k=80)
    w.step(.1)
    assert b.position.x<50

def test_collisions_resolved():
    w=PhysicsWorld(200,200,gravity=Vector())
    a=w.add(Body(Vector(50,50),radius=10))
    b=w.add(Body(Vector(55,50),radius=10))
    w.step()
    assert (a.position-b.position).magnitude()>=19.99

def test_pinned_motion():
    w=PhysicsWorld(200,200)
    b=w.add(Body(Vector(40,40),pinned=True))
    w.step(.2)
    assert b.position==Vector(40,40)

def test_boundaries_bounce():
    w=PhysicsWorld(100,100,gravity=Vector())
    b=w.add(Body(Vector(95,50),velocity=Vector(100,0),radius=5))
    w.step(.2)
    assert b.position.x<=95
    assert b.velocity.x<=0

def test_determinism():
    def run():
        w=PhysicsWorld(100,100)
        for x in (30,35,40):w.add(Body(Vector(x,10)))
        for _ in range(20):w.step()
        return [(b.position,b.velocity) for b in w.bodies]
    assert run()==run()

def test_fields():
    b=Body(Vector(10,0))
    assert radial_force(Vector(0,0))(b,0).x<0
    assert vortex_force(Vector(0,0))(b,0).y>0

@pytest.mark.parametrize("dt",[-1,0,float("nan")])
def test_bad_dt(dt):
    with pytest.raises(ValueError):PhysicsWorld().step(dt)
