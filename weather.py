"""Utility for retrieving weather summary information."""

import os
import logging
import argparse
import csv
from collections import namedtuple
from datetime import date, datetime, timezone, timedelta
import time
import requests
import boto3

WeatherSummary = namedtuple('WeatherSummary', 'mean_temp max_temp min_temp precipitation')
SpacetimePoint = namedtuple('SpacetimePoint', 'latitude longitude date')

API_KEY = '88e2f56333477b74'

logging.basicConfig(filename='weather.log', level=logging.INFO)

class WeatherUndergroundGateway:
    """Interface for Weather Underground."""
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
        return ('http://api.wunderground.com/api/{api_key}/history_{date}'
                '/q/{latitude},{longitude}.json').format(
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

class FileSystemGateway:
    """Interface for persisting files to local storage."""
    @staticmethod
    def store_weather_data(spacetime_point, weather_data, file_path):
        """Save the data in 'weather_data' to a file named after 'spacetime_point' and located
        at 'file_path'.
        """
        filename = FileSystemGateway._make_filename(spacetime_point, file_path)
        with open(filename, 'w') as out_file:
            out_file.write(weather_data)
        return filename

    @staticmethod
    def fetch_valid_files_in_directory(absolute_directory_name):
        files = os.listdir(path=absolute_directory_name)
        valid_files = [f for f in files if FileSystemGateway._valid_file(f)]
        return [os.path.join(absolute_directory_name, valid_file) for valid_file in valid_files]

    @staticmethod
    def _make_filename(spacetime_point, file_path):
        """
        >>> from weather import SpacetimePoint
        >>> from datetime import date
        >>> point = SpacetimePoint(123.43, -54.345, date(2018, 1, 1))
        >>> FileSystemGateway._make_filename(point, '/home/gklatte')
        '/home/gklatte/123.43_-54.345_2018-01-01.json'
        """
        point_string = '{latitude}_{longitude}_{date_string}.json'.format(
            latitude=spacetime_point.latitude,
            longitude=spacetime_point.longitude,
            date_string=spacetime_point.date.isoformat()
        )
        return '{file_path}/{point_string}'.format(
            file_path=file_path,
            point_string=point_string
        )

    @staticmethod
    def _valid_file(filename):
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

class S3Gateway:
    """Interface for AWS's S3."""
    def __init__(self, access_key_id, secret_access_key):
        """Initialize a s3 client using 'access_key_id' and 'secret_access_key' for
        authentication/authorization."""
        self._s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )

    @staticmethod
    def _get_filename(absolute_filename):
        """Get the nominal file name in 'absolute_filename'.

        >>> S3Gateway._get_filename('/home/gklatte/test.log')
        'test.log'
        """
        return absolute_filename.split('/')[-1]

    def upload_weather_data(self, absolute_filename):
        """Upload the weather data stored in 'absolute_filename' to
        an s3 bucket.
        """
        self._s3.meta.client.upload_file(
            absolute_filename,
            'gklatte-moves-research',
            S3Gateway._get_filename(absolute_filename)
        )

class RateController:
    """Class that controls the rate at which calls are made to the Weather Underground API.

    There are two rates with which we must obide:
    1) make no more than 10 calls/minute
    2) make no more than 500 calls/day
    """

    EST_TIMEZONE = timezone(timedelta(hours=-4))

    def __init__(self):
        self._current_date = RateController._now().date()
        self._calls_today = 0


    @staticmethod
    def _now():
        """Returns the current EST datetime, naively assuming that EST is four hours
        behind UTC.
        """
        return datetime.now(tz=RateController.EST_TIMEZONE)

    @staticmethod
    def _get_seconds_until_tomorrow():
        """Return the number of seconds from EST now until EST midnight."""
        now = RateController._now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(
            year=tomorrow.year,
            month=tomorrow.month,
            day=tomorrow.day,
            tzinfo=timezone(timedelta(hours=-4))
        )
        return (midnight - now).total_seconds()

    def control_rate(self):
        if self._current_date != RateController._now().date():
            self._calls_today = 0
            self._current_date = RateController._now().date()

        self._calls_today += 1

        logging.info('Calls today: {calls}'.format(
            calls=self._calls_today
        ))

        if self._calls_today == 500:
            seconds_until_tomorrow = RateController._get_seconds_until_tomorrow()
            logging.info('Sleeping until tomorrow for {seconds} seconds'.format(
                seconds=seconds_until_tomorrow
            ))
            time.sleep(seconds_until_tomorrow)
        else:
            time.sleep(6.1)

def extract_spacetime_point(filename):
    """Extract the first SpacetimePoint listed in 'filename'."""
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            return _fetch_spacetime_point(next(reader))
        except KeyError:
            return None

def _fetch_spacetime_point(data):
    """Extract the SpacetimePoint in 'data'."""
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

        for (device_id, spacetime_point), weather_summary in weather_by_id_and_spacetime.items():
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

def get_all_weather_data():
    """Fetch a sample weather point for each file and save the weather data for that point
    in an s3 bucket.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('aws_access_key_id')
    parser.add_argument('aws_secret_access_key')
    parser.add_argument(
        'data_file_directory',
        help='directory containing files to be processed'
    )
    args = parser.parse_args()

    valid_files = FileSystemGateway.fetch_valid_files_in_directory(args.data_file_directory)

    logging.info('There are {num_valid_files} valid files (by filename)'.format(
        num_valid_files=len(valid_files)
    ))

    spacetime_points = [extract_spacetime_point(filename) for filename in valid_files]

    valid_points = [point for point in spacetime_points if point]

    logging.info('There are {num_valid_points} valid points (by file content)'.format(
        num_valid_points=len(valid_points)
    ))

    s3_gateway = S3Gateway(args.aws_access_key_id, args.aws_secret_access_key)
    rate_controller = RateController()

    for index, valid_point in enumerate(valid_points):
        weather_data = WeatherUndergroundGateway.fetch_weather_data(valid_point)
        absolute_filename = FileSystemGateway.store_weather_data(
            valid_point,
            weather_data,
            '/home/ec2-user/weather_data'
        )
        s3_gateway.upload_weather_data(absolute_filename)
        logging.info('Processed point #{index}'.format(index=index))

        rate_controller.control_rate()

if __name__ == '__main__':
    get_all_weather_data()
