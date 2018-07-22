import urllib
import re
import time
import csv
import os
from collections import namedtuple
import json
from datetime import date

Coordinate = namedtuple('Coordinate', 'latitude longitude')
WeatherSummary = namedtuple('WeatherSummary', 'mean_temp max_temp min_temp precipitation')
SpacetimePoint = namedtuple('SpacetimePoint', 'coordinate date')

API_KEY = '88e2f56333477b74'

def make_history_request(api_key, date, coordinate):
    return 'http://api.wunderground.com/api/{0}/history_{1}/q/{2},{3}.json'.format(
        api_key,
        date.strftime('%Y%m%d'),
        coordinate.latitude,
        coordinate.longitude)

def pluck_history_response(response):
    data = json.load(response)['history']['dailysummary'][0]
    return WeatherSummary(
        data['meantempi'],
        data['maxtempi'],
        data['mintempi'],
        data['precipi'])

def send_request(request):
    return urllib.urlopen(request)

def _fetch_spacetime_point(data):
    d = data['Data.Date'][:10]
    return SpacetimePoint(
        Coordinate(
            data['Data.Latitude'],
            data['Data.Longitude']),
        date(int(d[:4]), int(d[5:7]), int(d[8:10]))
        )

def fetch_spacetime_point(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return _fetch_spacetime_point(next(reader))

def write_to_csv(device_id, date, weather):
    with open('natalie-weather-api.csv', 'w') as csvfile:
        fieldnames = ['device_id', 'date', 'mean_temp', 'max_temp', 'min_temp', 'precip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow(
            {'device_id': device_id,
             'date': date,
             'mean_temp': weather.mean_temp,
             'max_temp': weather.max_temp,
             'min_temp': weather.min_temp,
             'precip': weather.precipitation}
        )

def get_device_id(filename):
    """Returns the ID of the device in 'filename'.

    >>> get_device_id('11423412_2018-22-07_json.csv')
    11423412
    """
    return filename.split('_')[0]

if __name__ == '__main__':

    filename = '11643577_2017-08-03_json.csv'
    
    device_id = get_device_id(filename)
    
    spacetime_point = fetch_spacetime_point(filename)
    
    history_request = make_history_request(
            API_KEY,
            spacetime_point.date,
            spacetime_point.coordinate)
    
    history_response = send_request(history_request)
    
    weather_summary = pluck_history_response(history_response)

    write_to_csv(device_id, spacetime_point.date, weather_summary)
