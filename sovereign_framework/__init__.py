"""
Sovereign Framework — The AI Monetization & App Builder SDK
Allows developers and AI agents to manufacture, monetize, and govern full-stack apps
using RevenueCat REST API v2, Gemini AI, and Motoko/Rust core.
"""

from .core import SovereignApp, RevenueCatConfig
from .workflows import (
    Workflow01_CreateMonetizedApp,
    Workflow02_SetupGlobalPPPPaywall,
    Workflow03_CustomerCenterRetention,
    Workflow04_MultiStoreSubscriptionSync,
    Workflow05_DeployEntangledAgent
)

__all__ = [
    "SovereignApp",
    "RevenueCatConfig",
    "Workflow01_CreateMonetizedApp",
    "Workflow02_SetupGlobalPPPPaywall",
    "Workflow03_CustomerCenterRetention",
    "Workflow04_MultiStoreSubscriptionSync",
    "Workflow05_DeployEntangledAgent"
]

__version__ = "1.0.0"
