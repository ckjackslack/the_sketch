# Constraint physics

Pure-Python two-dimensional bodies with semi-implicit Euler integration, forces, positional distance constraints, Hooke springs, optional circle collision resolution, walls, pinning and force fields.

```python
from src.physics import PhysicsWorld, Body, Vector, radial_force
world = PhysicsWorld(800,600,gravity=Vector(0,100))
anchor = world.add(Body(Vector(400,50),pinned=True))
bob = world.add(Body(Vector(400,180),radius=12))
world.connect(anchor,bob,length=130)
world.fields.append(radial_force(Vector(450,300),strength=1000))
for _ in range(120):
    world.step(1/60)
```

Demo: `python -m src render elastic --frames 180 --fps 30 -o elastic.gif`.

Constraints modify positions, while force fields and springs affect velocities. Positional constraint projection intentionally prioritizes shape preservation over fully physically accurate velocity reconstruction. Collisions are discrete circles, not continuous swept collision tests. The solver is O(n²) for collision pairs and aimed at modest numbers of bodies. Use `resolve_collisions=False` for lattice simulations; pinned nodes are immovable.

Recommended next improvements: velocity reconstruction, spatial broadphase for collisions, friction, sleeping bodies and a real-time parameter playground.
