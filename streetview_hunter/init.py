"""
Google Street View Hunter
=========================

Автоматический поиск и сбор панорам Google Street View.
"""

__version__ = "1.0.0"
__author__ = "Ваше Имя"
__email__ = "ваш.email@example.com"

from .core import StreetViewHunter
from .utils import load_config, save_config, validate_coordinates

__all__ = [
    "StreetViewHunter",
    "load_config",
    "save_config",
    "validate_coordinates",
]
