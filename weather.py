import argparse
import urllib
import re
import time
import csv
import os
from collections import namedtuple
import json
from datetime import date

WeatherSummary = namedtuple('WeatherSummary', 'mean_temp max_temp min_temp precipitation')
SpacetimePoint = namedtuple('SpacetimePoint', 'latitude longitude date')

API_KEY = '88e2f56333477b74'

def _make_history_request(api_key, point):
    return 'http://api.wunderground.com/api/{0}/history_{1}/q/{2},{3}.json'.format(
        api_key,
        point.date.strftime('%Y%m%d'),
        point.latitude,
        point.longitude)

def _pluck_history_response(response):
    data = json.load(response)['history']['dailysummary'][0]

    return WeatherSummary(
        data['meantempi'],
        data['maxtempi'],
        data['mintempi'],
        data['precipi'])

def _send_request(request):
    return urllib.urlopen(request)

def _fetch_spacetime_point(data):
    d = data['Data.Date'][:10]
    return SpacetimePoint(
        data['Data.Latitude'],
        data['Data.Longitude'],
        date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    )

def fetch_spacetime_point(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return _fetch_spacetime_point(next(reader))

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

def fetch_weather_summary(api_key, spacetime_point):
    history_request = _make_history_request(
        api_key,
        spacetime_point)
    
    history_response = _send_request(history_request)
    
    return _pluck_history_response(history_response)

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('out', help='name of the outputted csv file')
    parser.add_argument('files', nargs='+', help='files to be processed')
    args = parser.parse_args()

    valid_files = [file for file in args.files if valid_file(file)]

    id_and_spacetime_point_list = [(get_device_id(filename), fetch_spacetime_point(filename))
                                   for filename in valid_files]

    weather_by_id_and_spacetime = {(id, point): fetch_weather_summary(API_KEY, point)
                                   for id, point in id_and_spacetime_point_list}

    write_to_csv(weather_by_id_and_spacetime, args.out)
