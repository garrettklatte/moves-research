"""Module for weather_summary."""

from dataclasses import dataclass

@dataclass
class WeatherSummary:
    """Class that represents a summary of the weather."""
    mean_temp: float
    max_temp: float
    min_temp: float
    precipitation: float
    apparent_mean_temp: float = None
    apparent_max_temp: float = None
    apparent_min_temp: float = None
