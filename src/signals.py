"""Functional time-varying signals and reusable modulation combinators."""
from dataclasses import dataclass
import math
from .creative import lerp, clamp

@dataclass(frozen=True)
class Signal:
    fn: object
    def at(self,t): return self.fn(t)
    def map(self,fn): return Signal(lambda t:fn(self.at(t)))
    def __add__(self,other):
        rhs=as_signal(other)
        return Signal(lambda t:self.at(t)+rhs.at(t))
    __radd__=__add__
    def __mul__(self,other):
        rhs=as_signal(other)
        return Signal(lambda t:self.at(t)*rhs.at(t))
    __rmul__=__mul__

def as_signal(value):
    return value if isinstance(value,Signal) else Signal(lambda t:value)

def oscillate(frequency=1,phase=0,amplitude=1,offset=0):
    return Signal(lambda t:offset+amplitude*math.sin(math.tau*(frequency*t+phase)))

def envelope(points):
    """Piecewise-linear keyframes (time,value) with clamped endpoints."""
    points=sorted(points)
    if not points:
        raise ValueError("envelope requires points")
    if len({x for x,_ in points})!=len(points):
        raise ValueError("duplicate keyframe times")
    def sample(t):
        if t<=points[0][0]:return points[0][1]
        for (a,va),(b,vb) in zip(points,points[1:]):
            if t<=b:return lerp(va,vb,(t-a)/(b-a))
        return points[-1][1]
    return Signal(sample)

def hold(signal,period):
    if period<=0:raise ValueError("period must be positive")
    return Signal(lambda t:signal.at(math.floor(t/period)*period))

def repeat(signal,period):
    if period<=0:raise ValueError("period must be positive")
    return Signal(lambda t:signal.at(t%period))

def bind(scene,node,path,signal):
    """Update a node path each scene tick using simulation time."""
    def system(current,dt):
        node.set(path,signal.at(current.time))
    scene.systems.append(system)
    return system
