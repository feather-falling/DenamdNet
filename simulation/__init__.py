"""
BRICS Smart Health & Supply Chain Resilience - Complete Input Simulation
Generates complete daily operational telemetry for EVERY PHC x EVERY MEDICINE.
Respects inventory conservation, event truth from events.json, and data leakage protections.
"""

from .generator import DailyInputSimulator

__all__ = ["DailyInputSimulator"]
