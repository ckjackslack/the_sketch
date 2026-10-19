"""Three animated example compositions demonstrating graph, signals and scene systems."""
from .sketch_gif import Sketch
from .scene import Scene,Node
from .signals import oscillate,envelope,bind
from .graph import Graph,Ref,Param
from .creative import Painter,hsv,TAU,spiral,rose,lissajous
from .dynamics import flow_lines,poisson_disc
import math

class SignalGardenSketch(Sketch):
    def setup(self):
        self.scene=Scene("garden")
        self.flow=oscillate(.15,amplitude=35)
        self.orbs=[]
        for i in range(24):
            n=self.scene.add(Node(str(i),properties={"radius":6,"hue":i/24}))
            n.transform.x=self.canvas.width/2
            n.transform.y=self.canvas.height/2
            bind(self.scene,n,"properties.radius",oscillate(.2+i*.003,amplitude=3,offset=7))
            self.orbs.append(n)
    def update(self):self.scene.update(1/30)
    def draw(self):
        self.canvas.clear((8,10,25));p=Painter(self.canvas.image)
        t=self.scene.time
        for i,n in enumerate(self.orbs):
            a=TAU*i/len(self.orbs)+t*.5
            r=75+40*math.sin(t+i*.18)
            p.circle(self.canvas.width/2+r*math.cos(a),self.canvas.height/2+r*math.sin(a),
                     n.properties["radius"],fill=hsv(n.properties["hue"]+t*.04,.8,1))

class GraphMandalaSketch(Sketch):
    def setup(self):
        self.frame=0
        self.graph=Graph()
        sine=self.graph.add("wave","sine",x=Param("phase"))
        self.graph.add("radius","mix",a=35,b=200,t=Ref("wave"))
    def update(self):self.frame+=1
    def draw(self):
        self.canvas.clear((9,5,22));p=Painter(self.canvas.image)
        cx,cy=self.canvas.width/2,self.canvas.height/2
        t=self.frame/30
        for i in range(20):
            v=self.graph.evaluate("radius",parameters={"phase":t+i*.15})
            r=60+abs(v)
            p.path(rose(cx,cy,r,petals=5+i%7,samples=280,phase=t*.1+i*.07),
                   hsv(i/20,.8,.95),1)

class FlowConstellationSketch(Sketch):
    def setup(self):
        self.t=0
        self.paths=list(flow_lines(self.canvas.width,self.canvas.height,
                                    count=130,steps=150,seed=22))
        self.stars=poisson_disc(self.canvas.width,self.canvas.height,26,seed=7)
    def update(self):self.t+=1
    def draw(self):
        self.canvas.clear((3,8,18));p=Painter(self.canvas.image)
        for i,path in enumerate(self.paths):
            p.path(path[:min(len(path),max(2,self.t*4))],
                   hsv(.55+i/len(self.paths)*.3,.6,.8))
        for x,y in self.stars:
            p.circle(x,y,1.4,fill=(180,210,255))
