"""Visual demonstration: deterministic boids with a wandering predator."""
from ..sketch_gif import Sketch
from ..world import World,Vector
from ..behaviors import separate,align,cohere,wander,seek,flee
from ..creative import Painter,hsv

class SwarmSketch(Sketch):
    def setup(self):
        self.world=World(self.canvas.width,self.canvas.height,seed=7,boundary="wrap")
        for i in range(90):
            a=self.world.spawn(radius=3,tags={"boid"},state={"hue":i/90})
            a.behaviors=[separate(18,1.5),align(48,.65),cohere(65,.55),wander(.07)]
        self.predator=self.world.spawn(position=Vector(self.canvas.width/2,self.canvas.height/2),
                                       radius=9,max_speed=100,state={"hue":0})
        self.predator.behaviors=[wander(.35),seek(lambda w,a:w.agents[w.frame//50%90].position,.8)]
        for a in self.world.agents[:-1]:
            a.behaviors.append(flee(lambda w,agent:self.predator.position,.12))
    def update(self):
        self.world.step(1/30)
    def draw(self):
        self.canvas.clear((5,9,22))
        p=Painter(self.canvas.image)
        for a in self.world.agents:
            color=(255,90,70) if a is self.predator else hsv(a.state["hue"],.65,1)
            p.circle(a.position.x,a.position.y,a.radius,fill=color)
