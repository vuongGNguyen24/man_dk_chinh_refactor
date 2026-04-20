"""
Package for system diagram visual effects.
This package provides managers and specialized classes for rendering
nodes, group boxes, and connections with animations.
"""

from .connection import ConnectionEffect, WaveCalculator, GradientBuilder, PathSegment, ConnectionRender
from .effect_manager import EffectManager


__all__ = [
    "ConnectionEffect",
    "EffectManager",
]