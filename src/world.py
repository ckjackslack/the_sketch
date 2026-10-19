"""Deterministic, headless two-dimensional agent simulation (stdlib only)."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import math
import random
from .events import Event, EventBus

@dataclass(frozen=True)
class Vector:
    x: float = 0.
    y: float = 0.
    def __add__(self,o): return Vector(self.x+o.x,self.y+o.y)
    def __sub__(self,o): return Vector(self.x-o.x,self.y-o.y)
    def __mul__(self,k): return Vector(self.x*k,self.y*k)
    __rmul__=__mul__
    def __truediv__(self,k): return Vector(self.x/k,self.y/k)
    def magnitude(self): return math.hypot(self.x,self.y)
    def normalized(self):
        n=self.magnitude()
        return self/n if n else Vector()
    def limited(self,maximum):
        n=self.magnitude()
        return self* (maximum/n) if n>maximum and n else self
    def distance(self,other): return (self-other).magnitude()

@dataclass
class Agent:
    id: int
    position: Vector
    velocity: Vector = field(default_factory=Vector)
    radius: float = 3
    max_speed: float = 80
    max_force: float = 100
    mass: float = 1
    tags: set[str] = field(default_factory=set)
    state: dict = field(default_factory=dict)
    behaviors: list = field(default_factory=list)
    active: bool = True
    def __post_init__(self):
        if self.radius<0 or self.mass<=0 or self.max_speed<0 or self.max_force<0:
            raise ValueError("invalid agent physics")

class SpatialHash:
    def __init__(self, cell_size):
        if cell_size<=0: raise ValueError("cell_size must be positive")
        self.cell_size=cell_size
        self.cells=defaultdict(list)
    def key(self,p):
        return (math.floor(p.x/self.cell_size), math.floor(p.y/self.cell_size))
    def rebuild(self,agents):
        self.cells.clear()
        for a in agents:
            if a.active:self.cells[self.key(a.position)].append(a)
    def query(self,position,radius):
        if radius<0: raise ValueError("radius cannot be negative")
        s=self.cell_size
        x0,y0=math.floor((position.x-radius)/s),math.floor((position.y-radius)/s)
        x1,y1=math.floor((position.x+radius)/s),math.floor((position.y+radius)/s)
        return [a for y in range(y0,y1+1) for x in range(x0,x1+1)
                for a in self.cells.get((x,y),())
                if a.position.distance(position)<=radius]

class World:
    """Fixed-step Euler motion; forces evaluated from same-frame spatial snapshot."""
    def __init__(self, width=800,height=600,seed=0,cell_size=32,boundary="wrap"):
        if width<=0 or height<=0: raise ValueError("world dimensions must be positive")
        if boundary not in ("wrap","bounce","none"): raise ValueError("invalid boundary")
        self.width,self.height=width,height
        self.rng=random.Random(seed)
        self.index=SpatialHash(cell_size)
        self.boundary=boundary
        self.agents=[]
        self.events=EventBus()
        self.time=0.
        self.frame=0
        self._id=0

    def spawn(self,position=None,**kwargs):
        self._id+=1
        p=position if position is not None else Vector(self.rng.random()*self.width,self.rng.random()*self.height)
        agent=Agent(self._id,p,**kwargs)
        self.agents.append(agent)
        return agent

    def neighbors(self,agent,radius):
        return [other for other in self.index.query(agent.position,radius) if other.id!=agent.id]

    def step(self,dt=1/60):
        if not math.isfinite(dt) or dt<=0: raise ValueError("dt must be finite and positive")
        active=[a for a in self.agents if a.active]
        self.index.rebuild(active)
        accelerations={}
        for agent in active:
            force=Vector()
            for behavior in tuple(agent.behaviors):
                force+=behavior(self,agent)*1
            accelerations[agent.id]=force.limited(agent.max_force)/agent.mass
        for agent in active:
            agent.velocity=(agent.velocity+accelerations[agent.id]*dt).limited(agent.max_speed)
            p=agent.position+agent.velocity*dt
            if self.boundary=="wrap":
                p=Vector(p.x%self.width,p.y%self.height)
            elif self.boundary=="bounce":
                vx,vy=agent.velocity.x,agent.velocity.y
                if p.x<agent.radius or p.x>self.width-agent.radius: vx=-vx
                if p.y<agent.radius or p.y>self.height-agent.radius: vy=-vy
                agent.velocity=Vector(vx,vy)
                p=Vector(min(max(p.x,agent.radius),max(agent.radius,self.width-agent.radius)),
                         min(max(p.y,agent.radius),max(agent.radius,self.height-agent.radius)))
            agent.position=p
        self.time+=dt
        self.frame+=1
        self.index.rebuild(active)
        self._collisions(active)
        self.events.flush()
        return self

    def _collisions(self,active):
        seen=set()
        for a in active:
            for b in self.index.query(a.position,a.radius+max((x.radius for x in active),default=0)):
                pair=(min(a.id,b.id),max(a.id,b.id))
                if a is b or pair in seen:continue
                seen.add(pair)
                if a.position.distance(b.position)<a.radius+b.radius:
                    self.events.emit(Event("collision",source=str(a.id),
                                           payload={"a":a,"b":b},time=self.time))
    def run(self,steps,dt=1/60):
        if steps<0:raise ValueError("steps cannot be negative")
        for _ in range(steps):self.step(dt)
        return self
