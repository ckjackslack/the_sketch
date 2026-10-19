"""Compositional example: timeline, conditional triggers, nodes and event reactions."""
from .scene import Scene, Node
from .automation import Director
from .creative import Painter, hsv, TAU
from .sketch_gif import Sketch, run_sketch
import math

class ChoreographySketch(Sketch):
    def setup(self):
        self.scene = Scene("studio")
        self.director = Director()
        self.scene.systems.append(self.director)
        self.orbs=[]
        for i in range(18):
            node=self.scene.add(Node(f"orb-{i}", tags={"orb"},
                                     properties={"radius": 7+i%4, "hue":i/18}))
            node.transform.x=self.canvas.width/2
            node.transform.y=self.canvas.height/2
            self.orbs.append(node)
            angle=TAU*i/len(range(18))
            distance=50+i*8
            self.director.animate(node,"transform.x",
                                  self.canvas.width/2+distance*math.cos(angle),2.5)
            self.director.animate(node,"transform.y",
                                  self.canvas.height/2+distance*math.sin(angle),2.5)
        self.director.scheduler.after(1, lambda:self.scene.emit("pulse"),repeat=2)
        self.scene.on("pulse",lambda event:self._pulse())
        self.director.when(lambda scene:scene.time>=4,
                           lambda scene:scene.emit("finale"),once=True)
        self.scene.on("finale",lambda event:self._finale())
        self.pulses=0

    def _pulse(self):
        self.pulses+=1
        for n in self.orbs:
            n.properties["radius"]+=2

    def _finale(self):
        for n in self.orbs:
            self.director.animate(n,"properties.radius",20,1.5)

    def update(self):
        self.scene.update(1/30)

    def draw(self):
        self.canvas.clear((5,8,20))
        painter=Painter(self.canvas.image)
        for n in self.scene.find(tag="orb"):
            if n.visible:
                painter.circle(n.transform.x,n.transform.y,
                               n.properties["radius"],fill=hsv(n.properties["hue"],.8,1))

if __name__=="__main__":
    run_sketch(ChoreographySketch,700,500,frame_limit=180,fps=30,
               output="choreography.gif")
