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

def fetch_spacetime_point(data):
    d = data['Data.Date'][:10]
    return SpacetimePoint(
        Coordinate(
            data['Data.Latitude'],
            data['Data.Longitude']),
        date(int(d[:4]), int(d[5:7]), int(d[8:10]))
        )

def fetch_spacetime_point_by_device_id(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return { filename.split('_')[0] : fetch_spacetime_point(next(reader))}

def write_to_csv(weather_summary_by_device_id):
    with open('natalie-weather-api.csv', 'w') as csvfile:
        fieldnames = ['device_id', 'date', 'mean_temp', 'max_temp', 'min_temp', 'precip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for device_id, weather in weather_summary_by_device_id.iteritems():
            writer.writerow(
                {'device_id': device_id,
                 'date': 'test-date',
                 'mean_temp': weather.mean_temp,
                 'max_temp': weather.max_temp,
                 'min_temp': weather.min_temp,
                 'precip': weather.precipitation}
                )

if __name__ == '__main__':

    point_by_device_id = fetch_spacetime_point_by_device_id('sample.csv')

    
    request_by_device_id = { device_id : make_history_request(
            API_KEY,
            point.date,
            point.coordinate) for device_id, point in point_by_device_id.iteritems() }
    
    response_by_device_id = { device_id: send_request(request)
                              for device_id, request in request_by_device_id.iteritems() }
    
    weather_summary_by_device_id = { device_id : pluck_history_response(response)
                                     for device_id, response in response_by_device_id.iteritems() }

    write_to_csv(weather_summary_by_device_id)

    print(weather_summary_by_device_id)
