from collections import namedtuple

WeatherSummary = namedtuple('WeatherSummary', [
    'mean_temp',
    'max_temp',
    'min_temp',
    'precipitation'
])
