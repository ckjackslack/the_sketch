import itertools
import math
import pytest
from PIL import Image
from src.creative import (
    remap, smoothstep, pingpong, hsv, gradient, polygon, star, spiral,
    rose, lissajous, hypotrochoid, bezier, chaikin, noise2, fbm, curl,
    Painter, layer, composite, rectangular_grid, polar_grid, random_walk
)
from src.dynamics import Vec2, ParticleSystem, poisson_disc, flow_lines, oscillator

def test_math_and_colors():
    assert remap(.5,0,1,10,20)==15
    assert smoothstep(0,1,.5)==.5
    assert pingpong(1)==1
    assert hsv(0)==(255,0,0)
    assert gradient([(0,0,0),(100,100,100)],.5)==(50,50,50)
    with pytest.raises(ValueError): remap(2,1,1,0,10)

@pytest.mark.parametrize("generator,count",[
    (lambda:polygon(0,0,5,7),7),
    (lambda:star(0,0,10,4,5),10),
    (lambda:spiral(0,0,samples=30),30),
    (lambda:rose(0,0,10,samples=30),30),
    (lambda:lissajous(0,0,10,10,samples=30),30),
    (lambda:hypotrochoid(0,0,10,4,5,samples=30),30),
    (lambda:bezier((0,0),(1,1),(3,1),(4,0),samples=30),30),
])
def test_geometry(generator,count):
    pts=generator()
    assert len(pts)==count
    assert all(math.isfinite(v) for pt in pts for v in pt)

def test_chaikin_open_endpoints():
    points=[(0,0),(10,0),(10,10)]
    result=chaikin(points,3)
    assert result[0]==points[0] and result[-1]==points[-1]
    assert len(result)>len(points)

def test_noise_is_deterministic():
    assert noise2(1.3,5.2,4)==noise2(1.3,5.2,4)
    assert fbm(.7,.2,seed=3)==fbm(.7,.2,seed=3)
    assert all(math.isfinite(v) for v in curl(1.2,2.3))

def test_grid_and_walk():
    assert len(list(rectangular_grid(100,50,5,2)))==10
    assert len(list(polar_grid(0,0,2,8,10)))==16
    assert list(random_walk((0,0),20,seed=2))==list(random_walk((0,0),20,seed=2))

def test_painter_and_layers():
    img=Image.new("RGB",(64,64),(0,0,0))
    p=Painter(img)
    p.circle(12,12,5,fill=(255,0,0)).star(40,40,12,5,fill=(0,255,0))
    p.regular_polygon(40,14,9,6,fill=(0,0,255))
    assert img.getpixel((12,12))==(255,0,0)
    overlay=layer((20,20),lambda p:p.rect(0,0,20,20,fill=(255,255,255,255)),opacity=.5)
    out=composite(img,overlay,(0,0))
    assert out.mode=="RGBA" and out.getpixel((0,0))[0]>0
    assert img.mode=="RGB"

def test_particle_lifecycle_and_determinism():
    a=ParticleSystem(seed=2,gravity=(0,.1)).emit(10,10,30,lifetime=3)
    b=ParticleSystem(seed=2,gravity=(0,.1)).emit(10,10,30,lifetime=3)
    assert [(p.vel.x,p.vel.y) for p in a.particles]==[(p.vel.x,p.vel.y) for p in b.particles]
    a.update(3)
    assert not a.particles

def test_poisson_min_distance_and_bounds():
    points=poisson_disc(80,60,8,seed=5)
    assert all(0<=x<80 and 0<=y<60 for x,y in points)
    assert all(math.dist(a,b)>=8-1e-8 for a,b in itertools.combinations(points,2))
    assert points==poisson_disc(80,60,8,seed=5)

def test_flow_lines_and_oscillators():
    paths=list(flow_lines(80,80,count=10,steps=20,seed=7))
    assert paths==list(flow_lines(80,80,count=10,steps=20,seed=7))
    assert oscillator(0,shape="sine")==0
    assert oscillator(.25,shape="square")==1
    with pytest.raises(ValueError): oscillator(0,shape="unknown")
