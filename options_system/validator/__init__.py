"""Pre-entry real-time validation. Re-checks regime, IV, spread quality, and
M2M proximity right before manual trade entry."""
from .validator import Validator, ValidationResult

__all__ = ["Validator", "ValidationResult"]
