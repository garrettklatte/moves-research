import argparse
import os
import time

from gateways import CsvGateway, FollowMeeFileGateway, DarkSkyGateway

def get_weather_history(api_key):
    downloaded_files_path = '/vagrant/Downloaded Files'

    files = [os.path.join(downloaded_files_path, downloaded_file)
             for downloaded_file in os.listdir(downloaded_files_path)]

    print('Total number of downloaded files: {}'.format(len(files)))
    
    csvGateway = CsvGateway('dark_sky_data.csv')
    
    locations = [FollowMeeFileGateway.extract_subject_location_summary(f) for f
                 in files if FollowMeeFileGateway.extract_subject_location_summary(f)]

    print('Total number of locations: {}'.format(len(locations)))

    unprocessed_locations = [location for location in locations
                             if not csvGateway.fetch_weather_summary(location)]

    print('Total number of unprocessed data points: {}'.format(len(
        unprocessed_locations
    )))
    
    for unprocessed_location in unprocessed_locations:
        weather_summary = DarkSkyGateway.fetch_weather_summary(
            unprocessed_location,
            api_key
        )
        
        csvGateway.record_weather_summary(
            weather_summary,
            unprocessed_location
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('api_key')
    args = parser.parse_args()
    
    get_weather_history(args.api_key)
