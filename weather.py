"""Utility for retrieving weather summary information."""

import argparse
import csv
from collections import namedtuple
from datetime import date
import requests

WeatherSummary = namedtuple('WeatherSummary', 'mean_temp max_temp min_temp precipitation')
SpacetimePoint = namedtuple('SpacetimePoint', 'latitude longitude date')

API_KEY = '88e2f56333477b74'

class WeatherUndergroundGateway:
    @staticmethod
    def fetch_weather_summary(spacetime_point, api_key=API_KEY):
        """Using 'api_key' for authorization, fetch a summary of the weather
        at 'spacetime_point'.
        """
        history_request = WeatherUndergroundGateway._make_history_request(api_key, spacetime_point)
        history_response = requests.get(history_request).json()
        return WeatherUndergroundGateway._pluck_history_response(history_response)

    @staticmethod
    def fetch_weather_data(spacetime_point, api_key=API_KEY):
        """Using 'api_key' for authorization, fetch all weather data at 'spacetime_point."""
        request = WeatherUndergroundGateway._make_history_request(api_key, spacetime_point)
        response = requests.get(request).text
        return response

    @staticmethod
    def _make_history_request(api_key, point):
        """Using 'api_key' for authorization, make a request for fetching weather
        data at 'point'.

        >>> from datetime import date
        >>> api_key = 123456
        >>> point = SpacetimePoint(34.9, 109.2, date(2018, 1, 1))
        >>> WeatherUndergroundGateway._make_history_request(api_key, point)
        'http://api.wunderground.com/api/123456/history_20180101/q/34.9,109.2.json'
        """
        return 'http://api.wunderground.com/api/{api_key}/history_{date}/q/{latitude},{longitude}.json'.format(
            api_key=api_key,
            date=point.date.strftime('%Y%m%d'),
            latitude=point.latitude,
            longitude=point.longitude
        )

    @staticmethod
    def _pluck_history_response(response):
        """Pluck the WeatherSummary from 'response'.

        >>> resp = {'history': {
        ... 'dailysummary':
        ... [{'meantempi': 70,
        ... 'maxtempi': 80,
        ... 'mintempi': 60,
        ... 'precipi': 3
        ... }]}}
        >>> WeatherUndergroundGateway._pluck_history_response(resp)
        WeatherSummary(mean_temp=70, max_temp=80, min_temp=60, precipitation=3)
        """
        data = response['history']['dailysummary'][0]

        return WeatherSummary(
            data['meantempi'],
            data['maxtempi'],
            data['mintempi'],
            data['precipi']
        )

def extract_spacetime_point(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return _fetch_spacetime_point(next(reader))

def _fetch_spacetime_point(data):
    d = data['Data.Date'][:10]
    return SpacetimePoint(
        data['Data.Latitude'],
        data['Data.Longitude'],
        date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    )

def write_to_csv(weather_by_id_and_spacetime, filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ['device_id', 'date', 'mean_temp', 'max_temp', 'min_temp', 'precip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for (device_id, spacetime_point), weather_summary in weather_by_id_and_spacetime.iteritems():
            writer.writerow(
                {'device_id': device_id,
                 'date': spacetime_point.date,
                 'mean_temp': weather_summary.mean_temp,
                 'max_temp': weather_summary.max_temp,
                 'min_temp': weather_summary.min_temp,
                 'precip': weather_summary.precipitation}
            )

def get_device_id(filename):
    """Returns the ID of the device in 'filename'.

    >>> get_device_id('11423412_2018-22-07_json.csv')
    '11423412'
    """
    return filename.split('_')[0]

def valid_file(filename):
    """Use this function to filter out files that should not be analyzed.

    >>> valid_file('123432_2018-09-03_json.csv')
    True
    >>> valid_file('NA_2016-12-11_json.csv')
    False
    >>> valid_file('cancelled_2015-01-01_json.csv')
    False
    """
    tokens = filename.split('_')

    if tokens[0] == 'NA':
        return False

    if tokens[0] == 'cancelled':
        return False

    return True

def log_spacetime_points():
    parser = argparse.ArgumentParser()
    parser.add_argument('out', help='name of the outputted csv file')
    parser.add_argument('files', nargs='+', help='files to be processed')
    args = parser.parse_args()

    valid_files = [filename for filename in args.files if valid_file(filename)]

    spacetime_points = [extract_spacetime_point(filename) for filename in valid_files]

    with open(args.out, 'w') as out:
        writer = csv.DictWriter(out, fieldnames=['latitude', 'longitude', 'date'])
        writer.writeheader()
        for spacetime_point in spacetime_points:
            writer.writerow({
                'latitude': spacetime_point.latitude,
                'longitude': spacetime_point.longitude,
                'date': spacetime_point.date.isoformat()
            })

if __name__ == '__main__':
    log_spacetime_points()
