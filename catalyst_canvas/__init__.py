"""Catalyst Canvas canonical domain package."""

from .contract import CanvasContractError, CanvasValidationError, validate_contract
from .engine import generate_canvas
from .version import CONTRACT_VERSION, __version__

__all__ = [
    "CONTRACT_VERSION",
    "CanvasContractError",
    "CanvasValidationError",
    "__version__",
    "generate_canvas",
    "validate_contract",
]
