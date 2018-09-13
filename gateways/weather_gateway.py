"""Module for weather_gateway."""

import requests
from definitions import WeatherSummary

API_KEY = '88e2f56333477b74'

class WeatherGateway:
    """Gateway for fetching weather summaries."""
    @staticmethod
    def fetch_weather_summary(spacetime_point, api_key=API_KEY):
        """Using 'api_key' for authorization, fetch a summary of the weather
        at 'spacetime_point'.
        """
        history_request = WeatherGateway._make_history_request(
            api_key,
            spacetime_point
        )
        history_response = requests.get(history_request).json()
        return WeatherGateway._pluck_history_response(history_response)

    @staticmethod
    def fetch_weather_data(spacetime_point, api_key=API_KEY):
        """Using 'api_key' for authorization, fetch all weather data at
        'spacetime_point.
        """
        request = WeatherGateway._make_history_request(
            api_key,
            spacetime_point
        )
        response = requests.get(request).text
        return response

    @staticmethod
    def _make_history_request(api_key, point):
        """Using 'api_key' for authorization, make a request for fetching weather
        data at 'point'.
        """
        return ('http://api.wunderground.com/api/{api_key}/history_{date}'
                '/q/{latitude},{longitude}.json').format(
                    api_key=api_key,
                    date=point.date.strftime('%Y%m%d'),
                    latitude=point.latitude,
                    longitude=point.longitude
                )

    @staticmethod
    def _pluck_history_response(response):
        """Pluck the WeatherSummary from 'response'."""
        data = response['history']['dailysummary'][0]

        return WeatherSummary(
            data['meantempi'],
            data['maxtempi'],
            data['mintempi'],
            data['precipi']
        )
