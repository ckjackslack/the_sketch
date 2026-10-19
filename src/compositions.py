"""Generative compositions built from the creative primitives."""
from .sketch_gif import Sketch,run_sketch
from .creative import Painter,gradient,hsv,spiral,star,TAU
from .dynamics import flow_lines,poisson_disc,ParticleSystem
import math

class FlowFieldSketch(Sketch):
    def setup(self):
        self.frame=0
        self.paths=list(flow_lines(self.canvas.width,self.canvas.height,
                                   count=220,steps=100,seed=17))
    def update(self):
        self.frame+=1
    def draw(self):
        self.canvas.clear((7,9,23))
        p=Painter(self.canvas.image)
        for i,path in enumerate(self.paths):
            n=min(len(path),max(2,self.frame*3))
            p.path(path[:n],hsv(i/len(self.paths),.65,.95),1)

class CelestialSketch(Sketch):
    def setup(self):
        self.t=0
        self.stars=poisson_disc(self.canvas.width,self.canvas.height,17,seed=12)
    def update(self): self.t+=1
    def draw(self):
        self.canvas.clear((4,5,16))
        p=Painter(self.canvas.image)
        for i,(x,y) in enumerate(self.stars):
            p.circle(x,y,(i%3+1)*.6,fill=(125,165,210))
        cx,cy=self.canvas.width/2,self.canvas.height/2
        for i in range(15):
            a=self.t*.011+i*.13
            r=25+i*11
            color=gradient([(55,34,129),(228,85,170),(255,228,140)],i/14)
            p.path(spiral(cx,cy,turns=2+i*.07,radius=r,
                          samples=190,phase=a),color,1)
        p.star(cx,cy,19,8,tips=8,rotation=self.t*.02,fill=(250,240,190))

if __name__=="__main__":
    run_sketch(CelestialSketch,600,600,frame_limit=120,seed=7,output="celestial.gif")
