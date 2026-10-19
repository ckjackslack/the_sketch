"""Spring lattice and magnetic vortex composition."""
from ..sketch_gif import Sketch
from ..physics import PhysicsWorld,Body,Vector,vortex_force
from ..creative import Painter,hsv

class ElasticSketch(Sketch):
    def setup(self):
        w,h=self.canvas.width,self.canvas.height
        self.world=PhysicsWorld(w,h,gravity=Vector(0,65),iterations=8,resolve_collisions=False)
        self.grid=[]
        cols,rows=13,8
        dx=min(35,(w-40)/(cols-1));dy=min(34,(h-40)/(rows-1))
        for j in range(rows):
            line=[]
            for i in range(cols):
                body=self.world.add(Body(Vector(w/2+(i-(cols-1)/2)*dx,50+j*dy),
                                         radius=2,pinned=(j==0)))
                line.append(body)
            self.grid.append(line)
        for j in range(rows):
            for i in range(cols):
                if i: self.world.connect(self.grid[j][i-1],self.grid[j][i],stiffness=.95)
                if j: self.world.connect(self.grid[j-1][i],self.grid[j][i],stiffness=.95)
        self.world.fields.append(vortex_force(Vector(w/2,h/2),strength=8000,softening=160))
    def update(self):
        self.world.step(1/30)
    def draw(self):
        self.canvas.clear((6,8,25))
        p=Painter(self.canvas.image)
        for j,line in enumerate(self.grid):
            for i,b in enumerate(line):
                if i:
                    a=line[i-1]
                    p.line([(a.position.x,a.position.y),(b.position.x,b.position.y)],hsv(j/len(self.grid),.65,1),2)
                if j:
                    a=self.grid[j-1][i]
                    p.line([(a.position.x,a.position.y),(b.position.x,b.position.y)],hsv(j/len(self.grid),.65,1),2)
                p.circle(b.position.x,b.position.y,2.5,fill=(255,235,195))
