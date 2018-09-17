"""Module for dark_sky_gateway."""

import requests
from definitions import WeatherSummary

class DarkSkyGateway:
    """Gateway for fetching weather summaries."""
    @staticmethod
    def fetch_weather_summary(subject_location_summary, api_key):
        """Using 'api_key' for authorization, fetch a summary of the weather
        at 'subject_location_summary'.
        """
        request = DarkSkyGateway._make_request(
            subject_location_summary,
            api_key
        )

        response = requests.get(request)

        return DarkSkyGateway._pluck_response(response)

    @staticmethod
    def _make_request(subject_location_summary, api_key):
        """Using 'api_key' for authorization, make a request for fetching weather
        data at 'subject_location_summary'.
        """
        return ('https://api.darksky.net/forecast/{api_key}/{latitude},'
                '{longitude},{date}T00:00:00').format(
                    api_key=api_key,
                    date=subject_location_summary.date.isoformat(),
                    latitude=subject_location_summary.latitude,
                    longitude=subject_location_summary.longitude
                )

    @staticmethod
    def _pluck_response(response):
        """Pluck the WeatherSummary from 'response'."""
        return WeatherSummary(
            -999,
            response['daily']['data']['apparentTemperatureHigh'],
            response['daily']['data']['apparentTemperatureLow'],
            response['daily']['data']['precipIntensity']
        )

