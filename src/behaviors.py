"""Small, composable steering forces for World agents."""
from __future__ import annotations
from dataclasses import dataclass
import math
from .world import Vector

def seek(target,weight=1):
    def apply(world,agent):
        p=target(world,agent) if callable(target) else target
        desired=(p-agent.position).normalized()*agent.max_speed
        return (desired-agent.velocity).limited(agent.max_force)*weight
    return apply

def flee(target,weight=1):
    def apply(world,agent):
        p=target(world,agent) if callable(target) else target
        desired=(agent.position-p).normalized()*agent.max_speed
        return (desired-agent.velocity).limited(agent.max_force)*weight
    return apply

def wander(weight=1):
    def apply(world,agent):
        angle=world.rng.random()*math.tau
        return Vector(math.cos(angle),math.sin(angle))*agent.max_force*weight
    return apply

def separate(radius=20,weight=1):
    def apply(world,agent):
        force=Vector()
        for n in world.neighbors(agent,radius):
            offset=agent.position-n.position
            d=max(offset.magnitude(),1e-9)
            force+=offset.normalized()/d
        return force.normalized()*agent.max_force*weight if force.magnitude() else Vector()
    return apply

def align(radius=40,weight=1):
    def apply(world,agent):
        others=world.neighbors(agent,radius)
        if not others:return Vector()
        avg=sum((n.velocity for n in others),Vector())/len(others)
        return (avg.normalized()*agent.max_speed-agent.velocity).limited(agent.max_force)*weight
    return apply

def cohere(radius=60,weight=1):
    def apply(world,agent):
        others=world.neighbors(agent,radius)
        if not others:return Vector()
        center=sum((n.position for n in others),Vector())/len(others)
        return seek(center,weight)(world,agent)
    return apply
