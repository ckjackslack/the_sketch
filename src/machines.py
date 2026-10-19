"""Event-capable finite-state machines with guarded transitions."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    predicate: Callable
    action: Callable | None = None
    priority: int = 0

class StateMachine:
    def __init__(self, initial):
        self.state=initial
        self.transitions=[]
        self.on_enter={}
        self.on_exit={}
    def add(self,source,target,predicate,action=None,priority=0):
        self.transitions.append(Transition(source,target,predicate,action,priority))
        return self
    def step(self,context):
        for t in sorted(self.transitions,key=lambda t:-t.priority):
            if t.source in (self.state,"*") and t.predicate(context):
                previous=self.state
                if previous in self.on_exit:self.on_exit[previous](context)
                self.state=t.target
                if t.action:t.action(context)
                if self.state in self.on_enter:self.on_enter[self.state](context)
                return True
        return False
