"""Reusable deterministic simulation, oscillators, and spatial distributions."""
from __future__ import annotations
from dataclasses import dataclass
import math
import random
from .creative import TAU, clamp, fbm, hsv

@dataclass
class Vec2:
    x: float=0
    y: float=0
    def __add__(self,other): return Vec2(self.x+other.x,self.y+other.y)
    def __sub__(self,other): return Vec2(self.x-other.x,self.y-other.y)
    def __mul__(self,k): return Vec2(self.x*k,self.y*k)
    __rmul__=__mul__
    def length(self): return math.hypot(self.x,self.y)
    def normalized(self):
        n=self.length()
        return self*(1/n) if n else Vec2()
    def tuple(self): return self.x,self.y

@dataclass
class Particle:
    pos: Vec2
    vel: Vec2
    life: float=1.
    radius: float=2.
    color: tuple=(255,255,255)

class ParticleSystem:
    def __init__(self,seed=0,gravity=(0,0),drag=1):
        if not 0<=drag<=1:
            raise ValueError("drag must be in [0,1]")
        self.rng=random.Random(seed)
        self.gravity=Vec2(*gravity)
        self.drag=drag
        self.particles=[]

    def emit(self,x,y,count=1,speed=2,spread=TAU,angle=-math.pi/2,
             lifetime=60,radius=2,color=(255,255,255)):
        if count<0 or lifetime<=0:
            raise ValueError("count must be nonnegative and lifetime positive")
        for _ in range(count):
            a=angle+(self.rng.random()-.5)*spread
            s=speed*(.5+self.rng.random()*.5)
            self.particles.append(Particle(Vec2(x,y),
                Vec2(math.cos(a)*s,math.sin(a)*s),lifetime,radius,color))
        return self

    def update(self,dt=1):
        if dt<0:
            raise ValueError("dt must be nonnegative")
        living=[]
        for p in self.particles:
            p.vel=(p.vel+self.gravity*dt)*(self.drag**dt)
            p.pos=p.pos+p.vel*dt
            p.life-=dt
            if p.life>0:
                living.append(p)
        self.particles=living
        return self

    def draw(self,painter):
        for p in self.particles:
            painter.circle(p.pos.x,p.pos.y,p.radius,fill=p.color)
        return painter

def poisson_disc(width,height,radius,seed=0,k=30):
    """Bridson blue-noise sampling; each pair of points >= radius apart."""
    if width<=0 or height<=0 or radius<=0 or k<1:
        raise ValueError("invalid sampling parameters")
    rng=random.Random(seed)
    cell=radius/math.sqrt(2)
    cols=math.ceil(width/cell)
    grid={}
    start=(rng.random()*width,rng.random()*height)
    samples=[start]
    active=[start]
    grid[(int(start[0]/cell),int(start[1]/cell))]=start
    while active:
        idx=rng.randrange(len(active))
        x,y=active[idx]
        found=False
        for _ in range(k):
            theta=rng.random()*TAU
            distance=radius*(1+rng.random())
            nx,ny=x+math.cos(theta)*distance,y+math.sin(theta)*distance
            if not (0<=nx<width and 0<=ny<height):
                continue
            gx,gy=int(nx/cell),int(ny/cell)
            if all((nx-px)**2+(ny-py)**2>=radius*radius
                   for iy in range(gy-2,gy+3) for ix in range(gx-2,gx+3)
                   if (ix,iy) in grid
                   for px,py in [grid[(ix,iy)]]):
                point=(nx,ny)
                samples.append(point)
                active.append(point)
                grid[(gx,gy)]=point
                found=True
                break
        if not found:
            active.pop(idx)
    return samples

def flow_lines(width,height,count=100,steps=120,step=2,scale=.009,seed=0):
    """Yield polylines advected through a multi-octave noise angle field."""
    rng=random.Random(seed)
    for _ in range(count):
        x,y=rng.uniform(0,width),rng.uniform(0,height)
        points=[(x,y)]
        for _ in range(steps):
            angle=TAU*fbm(x*scale,y*scale,seed=seed)
            x+=math.cos(angle)*step
            y+=math.sin(angle)*step
            if not (0<=x<width and 0<=y<height):
                break
            points.append((x,y))
        if len(points)>1:
            yield points

def oscillator(t,frequency=1,phase=0,shape="sine"):
    x=(frequency*t+phase)%1
    if shape=="sine": return math.sin(TAU*x)
    if shape=="triangle": return 1-4*abs(x-.5)
    if shape=="saw": return 2*x-1
    if shape=="square": return 1 if x<.5 else -1
    raise ValueError("unknown waveform")
