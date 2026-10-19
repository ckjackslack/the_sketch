"""Built-in visual examples, kept separate from reusable engine modules."""
from importlib import import_module

PRESETS = {
    "abstract": ("abstract", "AbstractLineSketch"),
    "arkanoid": ("arkanoid", "ArkanoidSketch"),
    "circles": ("circles", "CirclesSketch"),
    "example": ("example", "MySketch"),
    "fancy": ("fancy", "FancySketch"),
    "matrix": ("matrix", "MatrixSketch"),
    "rectangles": ("rectangles", "RectanglesSketch"),
    "screensaver": ("old_screensaver", "WindowsScreensaverSketch"),
    "celestial": ("compositions", "CelestialSketch"),
    "flow-field": ("compositions", "FlowFieldSketch"),
    "choreography": ("choreography", "ChoreographySketch"),
    "signal-garden": ("showcases", "SignalGardenSketch"),
    "graph-mandala": ("showcases", "GraphMandalaSketch"),
    "flow-constellation": ("showcases", "FlowConstellationSketch"),
    "swarm": ("swarm", "SwarmSketch"),
    "elastic": ("elastic", "ElasticSketch"),
}

def load_preset(name):
    if name not in PRESETS:
        raise KeyError(f"unknown preset: {name}")
    module, symbol = PRESETS[name]
    return getattr(import_module(f"src.examples.{module}"), symbol)
