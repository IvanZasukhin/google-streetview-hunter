"""
Google Street View Hunter
=========================

Автоматический поиск и сбор панорам Google Street View.
"""

__version__ = "1.0.0"
__author__ = "Иван Засухин"
__email__ = "ivanzasukhin11@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/ваш-username/google-streetview-hunter"

from .core import StreetViewHunter
from .utils import load_config, save_config, validate_coordinates

__all__ = [
    "StreetViewHunter",
    "load_config",
    "save_config",
    "validate_coordinates",
]
