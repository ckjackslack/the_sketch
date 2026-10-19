"""Composable creative-coding primitives for Pillow canvases.

Coordinates are pixel based, angles in radians, colors RGB/RGBA tuples.
All generators are lazy; functions drawing onto a canvas return the canvas.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections.abc import Iterable
import colorsys
import math
import random
from PIL import Image, ImageDraw, ImageFilter

TAU = math.tau

def lerp(a, b, t):
    return a + (b - a) * t

def remap(x, a, b, c, d):
    if a == b:
        raise ValueError("source interval must not be zero")
    return c + (x-a) * (d-c)/(b-a)

def clamp(x, lo=0.0, hi=1.0):
    if lo > hi:
        raise ValueError("lo must be <= hi")
    return max(lo, min(hi, x))

def smoothstep(a, b, x):
    t = clamp(remap(x, a, b, 0, 1))
    return t*t*(3-2*t)

def ease_in_out(t):
    t = clamp(t)
    return t*t*(3-2*t)

def pingpong(t):
    return 1-abs((t % 2)-1)

def hsv(h, s=1, v=1, alpha=None):
    rgb = tuple(round(255 * value) for value in colorsys.hsv_to_rgb(h % 1, clamp(s), clamp(v)))
    return rgb if alpha is None else (*rgb, round(255*clamp(alpha)))

def mix_color(a, b, t):
    if len(a) != len(b):
        raise ValueError("colors must have identical channel counts")
    return tuple(round(lerp(x, y, clamp(t))) for x, y in zip(a, b))

def gradient(stops, t):
    """Interpolate evenly spaced palette colors."""
    if not stops:
        raise ValueError("palette needs at least one color")
    if len(stops) == 1:
        return tuple(stops[0])
    pos = clamp(t)*(len(stops)-1)
    i = min(int(pos), len(stops)-2)
    return mix_color(stops[i], stops[i+1], pos-i)

def point_on_circle(cx, cy, radius, angle):
    return (cx + radius*math.cos(angle), cy + radius*math.sin(angle))

def rotate(x, y, angle, origin=(0, 0)):
    dx, dy = x-origin[0], y-origin[1]
    c, s = math.cos(angle), math.sin(angle)
    return origin[0]+dx*c-dy*s, origin[1]+dx*s+dy*c

def polar_grid(cx, cy, rings, spokes, spacing):
    if rings < 0 or spokes < 1:
        raise ValueError("rings >= 0 and spokes >= 1 required")
    for ring in range(1, rings+1):
        for spoke in range(spokes):
            yield point_on_circle(cx, cy, ring*spacing, TAU*spoke/spokes)

def rectangular_grid(width, height, cols, rows, margin=0):
    if cols < 1 or rows < 1:
        raise ValueError("cols and rows must be positive")
    for row in range(rows):
        for col in range(cols):
            yield (margin+(width-2*margin)*(col+.5)/cols,
                   margin+(height-2*margin)*(row+.5)/rows)

def polygon(cx, cy, radius, sides, rotation=0):
    if sides < 3 or radius < 0:
        raise ValueError("polygon needs >=3 sides and nonnegative radius")
    return [point_on_circle(cx, cy, radius, rotation+TAU*i/sides) for i in range(sides)]

def star(cx, cy, outer, inner, tips=5, rotation=-math.pi/2):
    if tips < 2 or inner < 0 or outer < inner:
        raise ValueError("invalid star dimensions")
    return [point_on_circle(cx, cy, outer if i%2 == 0 else inner,
                            rotation+math.pi*i/tips) for i in range(2*tips)]

def spiral(cx, cy, turns=5, radius=100, samples=500, phase=0, power=1):
    if samples < 2 or radius < 0 or power <= 0:
        raise ValueError("invalid spiral parameters")
    return [point_on_circle(cx, cy, radius*(i/(samples-1))**power,
                            phase+TAU*turns*i/(samples-1)) for i in range(samples)]

def rose(cx, cy, radius, petals=5, samples=600, phase=0):
    if samples < 2:
        raise ValueError("samples must be >= 2")
    return [point_on_circle(cx, cy, radius*math.cos(petals*TAU*i/(samples-1)),
                            phase+TAU*i/(samples-1)) for i in range(samples)]

def lissajous(cx, cy, rx, ry, a=3, b=2, phase=math.pi/2, samples=600):
    if samples < 2:
        raise ValueError("samples must be >= 2")
    return [(cx+rx*math.sin(a*TAU*i/(samples-1)+phase),
             cy+ry*math.sin(b*TAU*i/(samples-1))) for i in range(samples)]

def hypotrochoid(cx, cy, R, r, d, turns=10, samples=1000):
    if r == 0 or samples < 2:
        raise ValueError("r must be nonzero; samples >= 2")
    points=[]
    for i in range(samples):
        t=turns*TAU*i/(samples-1)
        points.append((cx+(R-r)*math.cos(t)+d*math.cos((R-r)*t/r),
                       cy+(R-r)*math.sin(t)-d*math.sin((R-r)*t/r)))
    return points

def bezier(p0, p1, p2, p3, samples=100):
    if samples < 2:
        raise ValueError("samples must be >= 2")
    result=[]
    for i in range(samples):
        t=i/(samples-1)
        u=1-t
        result.append(tuple(u**3*p0[k]+3*u*u*t*p1[k]+3*u*t*t*p2[k]+t**3*p3[k] for k in (0,1)))
    return result

def chaikin(points, iterations=2, closed=False):
    """Corner-cutting smooth curve; works for open and closed polylines."""
    points=list(points)
    if iterations < 0:
        raise ValueError("iterations must be nonnegative")
    for _ in range(iterations):
        if len(points)<2:
            return points
        out=[] if closed else [points[0]]
        pairs=zip(points, points[1:]+points[:1] if closed else points[1:])
        for a,b in pairs:
            out.extend(((.75*a[0]+.25*b[0], .75*a[1]+.25*b[1]),
                        (.25*a[0]+.75*b[0], .25*a[1]+.75*b[1])))
        if not closed:
            out.append(points[-1])
        points=out
    return points

def random_walk(start, steps, step=5, seed=None):
    rng=random.Random(seed)
    x,y=start
    yield x,y
    for _ in range(steps):
        theta=rng.random()*TAU
        x+=step*math.cos(theta)
        y+=step*math.sin(theta)
        yield x,y

def noise2(x, y, seed=0):
    """Smooth deterministic value noise; approximately [-1, 1]."""
    def hash2(ix,iy):
        n=(ix*374761393+iy*668265263+seed*1442695041)&0xFFFFFFFF
        n=((n^(n>>13))*1274126177)&0xFFFFFFFF
        return ((n^(n>>16))/4294967295)*2-1
    ix,iy=math.floor(x),math.floor(y)
    tx,ty=ease_in_out(x-ix),ease_in_out(y-iy)
    return lerp(lerp(hash2(ix,iy),hash2(ix+1,iy),tx),
                lerp(hash2(ix,iy+1),hash2(ix+1,iy+1),tx),ty)

def fbm(x, y, octaves=5, lacunarity=2, gain=.5, seed=0):
    if octaves<1 or gain<0 or lacunarity<=0:
        raise ValueError("invalid fractal noise parameters")
    total=norm=0.
    amp=freq=1.
    for o in range(octaves):
        total+=amp*noise2(x*freq,y*freq,seed+o*101)
        norm+=amp
        amp*=gain
        freq*=lacunarity
    return total/norm

def curl(x,y,epsilon=.01,seed=0):
    if epsilon<=0:
        raise ValueError("epsilon must be positive")
    dx=(noise2(x+epsilon,y,seed)-noise2(x-epsilon,y,seed))/(2*epsilon)
    dy=(noise2(x,y+epsilon,seed)-noise2(x,y-epsilon,seed))/(2*epsilon)
    return dy,-dx

@dataclass
class Brush:
    fill: tuple | str | None = None
    stroke: tuple | str | None = (255,255,255)
    width: int = 1

class Painter:
    """Immediate-mode drawing on Pillow RGB or RGBA images."""
    def __init__(self, image):
        self.image=image
        self.draw=ImageDraw.Draw(image)

    def line(self, points, color=(255,255,255), width=1, joint="curve"):
        self.draw.line(list(points),fill=color,width=width,joint=joint)
        return self

    def shape(self, points, fill=None, stroke=None, width=1):
        points=list(points)
        if fill is not None:
            self.draw.polygon(points,fill=fill)
        if stroke is not None and len(points)>1:
            self.draw.line(points+[points[0]],fill=stroke,width=width,joint="curve")
        return self

    def circle(self,x,y,r,fill=None,stroke=None,width=1):
        self.draw.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=width)
        return self

    def ellipse(self,x,y,rx,ry,fill=None,stroke=None,width=1):
        self.draw.ellipse((x-rx,y-ry,x+rx,y+ry),fill=fill,outline=stroke,width=width)
        return self

    def rect(self,x,y,w,h,fill=None,stroke=None,width=1,radius=0):
        box=(x,y,x+w,y+h)
        self.draw.rounded_rectangle(box,radius=radius,fill=fill,outline=stroke,width=width)
        return self

    def regular_polygon(self,x,y,r,sides=6,rotation=0,**style):
        return self.shape(polygon(x,y,r,sides,rotation),**style)

    def star(self,x,y,outer,inner,tips=5,rotation=-math.pi/2,**style):
        return self.shape(star(x,y,outer,inner,tips,rotation),**style)

    def path(self,points,color=(255,255,255),width=1):
        return self.line(points,color,width)

    def arc(self,x,y,r,start,end,color=(255,255,255),width=1):
        self.draw.arc((x-r,y-r,x+r,y+r),math.degrees(start),math.degrees(end),fill=color,width=width)
        return self

    def text(self,xy,text,fill=(255,255,255),font=None,anchor=None):
        self.draw.text(xy,str(text),fill=fill,font=font,anchor=anchor)
        return self

def layer(size, draw_fn, opacity=1):
    """Build a transparent layer from a callback accepting Painter."""
    if not 0<=opacity<=1:
        raise ValueError("opacity must be in [0, 1]")
    image=Image.new("RGBA",size,(0,0,0,0))
    draw_fn(Painter(image))
    if opacity!=1:
        alpha=image.getchannel("A").point(lambda v: round(v*opacity))
        image.putalpha(alpha)
    return image

def composite(base, overlay, xy=(0,0), opacity=1):
    """Non-destructive alpha composition, including overlays partly off-canvas."""
    if not 0<=opacity<=1:
        raise ValueError("opacity must be in [0, 1]")
    canvas=base.convert("RGBA")
    top=overlay.convert("RGBA")
    if opacity != 1:
        top.putalpha(top.getchannel("A").point(lambda a: round(a*opacity)))
    canvas.alpha_composite(top,dest=(int(xy[0]),int(xy[1])))
    return canvas

def glow(image,radius=8,strength=.65):
    if radius<0 or not 0<=strength<=1:
        raise ValueError("invalid glow settings")
    return Image.blend(image.convert("RGBA"),image.convert("RGBA").filter(ImageFilter.GaussianBlur(radius)),strength)
