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

        response = requests.get(request).json()

        return DarkSkyGateway._pluck_response(response)

    @staticmethod
    def _make_request(subject_location_summary, api_key):
        """Using 'api_key' for authorization, make a request for fetching weather
        data at 'subject_location_summary'.
        """
        return ('https://api.darksky.net/forecast/{api_key}/{latitude},'
                '{longitude},{date}T00:00:00?exclude=currently,minutely,'
                'alerts,flags').format(
                    api_key=api_key,
                    date=subject_location_summary.date.isoformat(),
                    latitude=subject_location_summary.latitude,
                    longitude=subject_location_summary.longitude
                )

    @staticmethod
    def _pluck_response(response):
        """Pluck the WeatherSummary from 'response'."""
        try:
            temperatures = [data['temperature'] for data in
                            response['hourly']['data']]
            mean_temp = sum(temperatures)/len(temperatures)
        except:
            mean_temp = None
        try:
            max_temp = response['daily']['data'][0]['temperatureHigh']
        except KeyError:
            max_temp = None
        try:
            min_temp = response['daily']['data'][0]['temperatureLow']
        except KeyError:
            min_temp = None
        try:
            apparent_temperatures = [data['apparentTemperature'] for data in
                                     response['hourly']['data']]
            apparent_mean_temp = sum(apparent_temperatures)/len(apparent_temperatures)
        except:
            apparent_mean_temp = None
        try:
            apparent_max_temp = response['daily']['data'][0]['apparentTemperatureHigh']
        except KeyError:
            apparent_max_temp = None
        try:
            apparent_min_temp = response['daily']['data'][0]['apparentTemperatureLow']
        except KeyError:
            apparent_min_temp = None
        try:
            precip_intensities = [data['precipIntensity'] for data in
                                  response['hourly']['data']] 
            precipitation = sum(precip_intensities)
        except KeyError:
            precipitation = None
            
        return WeatherSummary(
            mean_temp,
            max_temp,
            min_temp,
            precipitation,
            apparent_mean_temp,
            apparent_max_temp,
            apparent_min_temp
        )

