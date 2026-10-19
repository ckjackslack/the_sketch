"""Deterministic constraint-based 2D physics, independent of graphics backends.

Semi-implicit Euler integration, positional constraints and impulse collision response.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
from .world import Vector

@dataclass
class Body:
    position: Vector
    velocity: Vector = field(default_factory=Vector)
    radius: float = 5.
    mass: float = 1.
    restitution: float = .4
    pinned: bool = False
    force: Vector = field(default_factory=Vector)
    def __post_init__(self):
        if self.radius < 0 or self.mass <= 0 or not 0 <= self.restitution <= 1:
            raise ValueError("invalid body parameters")
    @property
    def inv_mass(self): return 0. if self.pinned else 1/self.mass
    def apply(self, force):
        self.force = self.force + force

@dataclass
class DistanceConstraint:
    a: Body
    b: Body
    length: float
    stiffness: float = 1.
    def __post_init__(self):
        if self.length < 0 or not 0 <= self.stiffness <= 1:
            raise ValueError("invalid constraint")
    def solve(self):
        delta=self.b.position-self.a.position
        d=delta.magnitude()
        total=self.a.inv_mass+self.b.inv_mass
        if d < 1e-12 or total == 0: return
        correction=delta*((d-self.length)/d*self.stiffness/total)
        self.a.position=self.a.position+correction*self.a.inv_mass
        self.b.position=self.b.position-correction*self.b.inv_mass

@dataclass
class Spring:
    a: Body
    b: Body
    rest_length: float
    k: float = 30.
    damping: float = 2.
    def __post_init__(self):
        if self.rest_length < 0 or self.k < 0 or self.damping < 0:
            raise ValueError("invalid spring parameters")
    def apply(self):
        delta=self.b.position-self.a.position
        d=delta.magnitude()
        if d < 1e-12:return
        axis=delta/d
        relative=(self.b.velocity-self.a.velocity)
        f=axis*(self.k*(d-self.rest_length)+self.damping*(relative.x*axis.x+relative.y*axis.y))
        self.a.apply(f)
        self.b.apply(f*-1)

class PhysicsWorld:
    def __init__(self,width=800,height=600,gravity=Vector(0,100),iterations=6,
                 drag=.999,resolve_collisions=True):
        if width<=0 or height<=0 or iterations<1 or not 0<=drag<=1:
            raise ValueError("invalid world settings")
        self.width,self.height=width,height
        self.gravity=gravity
        self.iterations=iterations
        self.drag=drag
        self.resolve_collisions=resolve_collisions
        self.bodies=[]
        self.constraints=[]
        self.springs=[]
        self.fields=[]
        self.time=0.

    def add(self,body):
        self.bodies.append(body)
        return body
    def connect(self,a,b,length=None,stiffness=1):
        c=DistanceConstraint(a,b,(b.position-a.position).magnitude() if length is None else length,stiffness)
        self.constraints.append(c)
        return c
    def spring(self,a,b,rest_length=None,k=30,damping=2):
        s=Spring(a,b,(b.position-a.position).magnitude() if rest_length is None else rest_length,k,damping)
        self.springs.append(s)
        return s

    def step(self,dt=1/60):
        if not math.isfinite(dt) or dt<=0:raise ValueError("dt must be finite and positive")
        for s in self.springs:s.apply()
        for body in self.bodies:
            if body.pinned:
                body.force=Vector()
                body.velocity=Vector()
                continue
            total=body.force+ self.gravity*body.mass
            for field in self.fields:total=total+field(body,self.time)
            body.velocity=(body.velocity+total*(body.inv_mass*dt))*self.drag
            body.position=body.position+body.velocity*dt
            body.force=Vector()
        for _ in range(self.iterations):
            for constraint in self.constraints:constraint.solve()
            if self.resolve_collisions:
                for i,a in enumerate(self.bodies):
                    for b in self.bodies[i+1:]:
                        self._collide(a,b)
            for b in self.bodies:self._bounds(b)
        self.time+=dt
        return self

    def _bounds(self,b):
        if b.pinned:return
        x,y=b.position.x,b.position.y
        vx,vy=b.velocity.x,b.velocity.y
        lo_x,hi_x=b.radius,max(b.radius,self.width-b.radius)
        lo_y,hi_y=b.radius,max(b.radius,self.height-b.radius)
        if x<lo_x or x>hi_x:
            x=min(max(x,lo_x),hi_x)
            vx=-vx*b.restitution
        if y<lo_y or y>hi_y:
            y=min(max(y,lo_y),hi_y)
            vy=-vy*b.restitution
        b.position=Vector(x,y)
        b.velocity=Vector(vx,vy)

    @staticmethod
    def _collide(a,b):
        delta=b.position-a.position
        d=delta.magnitude()
        overlap=a.radius+b.radius-d
        weight=a.inv_mass+b.inv_mass
        if overlap<=0 or weight==0:return
        normal=delta/d if d>1e-12 else Vector(1,0)
        correction=normal*(overlap/weight)
        a.position=a.position-correction*a.inv_mass
        b.position=b.position+correction*b.inv_mass
        relative=b.velocity-a.velocity
        closing=relative.x*normal.x+relative.y*normal.y
        if closing >= 0:return
        impulse=normal*(-(1+min(a.restitution,b.restitution))*closing/weight)
        a.velocity=a.velocity-impulse*a.inv_mass
        b.velocity=b.velocity+impulse*b.inv_mass

def radial_force(center,strength=1000,softening=20):
    if softening<=0:raise ValueError("softening must be positive")
    def field(body,time):
        delta=center-body.position
        distance=delta.magnitude()
        return delta.normalized()*(strength/(1+(distance/softening)**2))
    return field

def vortex_force(center,strength=1000,softening=20):
    if softening<=0:raise ValueError("softening must be positive")
    def field(body,time):
        delta=body.position-center
        tangent=Vector(-delta.y,delta.x).normalized()
        return tangent*(strength/(1+(delta.magnitude()/softening)**2))
    return field
