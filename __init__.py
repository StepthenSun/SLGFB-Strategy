"""
SLGFB Strategy Core Library
===============================================================
A quantitative trading framework based on differential geometry, 
algebraic topology, and stochastic calculus.
"""

from .geometry import SE3Manifold, GeometricSignalDetector
from .fiber import FiberBundleStructure
from .stochastic import MalliavinConfidence
from .signals import SLGFBSignalGenerator
from .backtest import SLGFBBacktest

__version__ = "1.0.0"

__all__ = [
    'SE3Manifold',
    'GeometricSignalDetector',
    'FiberBundleStructure',
    'MalliavinConfidence',
    'SLGFBSignalGenerator',
    'SLGFBBacktest',
]
