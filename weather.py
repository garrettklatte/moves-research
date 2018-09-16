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

logging.basicConfig(filename='weather.log', level=logging.INFO)

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

def get_all_weather_data():
    """ DEPRECATED METHOD.
    
    Fetch a sample weather point for each file and save the weather data for 
    that point in an s3 bucket.
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

def get_weather_info():
    files = os.listdir('/vagrant/Downloaded Files')
    
if __name__ == '__main__':
    get_all_weather_data()
