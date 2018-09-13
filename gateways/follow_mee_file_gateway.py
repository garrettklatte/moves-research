"""Module for follow_mee_file_gateway."""

import csv
from datetime import date
from definitions import SubjectLocationSummary

class FollowMeeFileGateway:
    """Gateway class that understands files produced by 'FollowMee'."""

    @staticmethod
    def extract_subject_location_summary(filename):
        """Extract the SubjectLocationSummary contained in 'filename'."""
        with open(filename, 'r') as follow_mee_file:
            reader = csv.DictReader(follow_mee_file)
            first_row_record = list(reader)[0]
            try:
                longitude, latitude = FollowMeeFileGateway._extract_location(
                    first_row_record
                )
                date = FollowMeeFileGateway._extract_date(first_row_record)
            except KeyError:
                print('Invalid data in {filename}'.format(filename=filename))
                return None
            
        subject_id = FollowMeeFileGateway._extract_subject_id(filename)
        return SubjectLocationSummary(
            subject_id,
            longitude,
            latitude,
            date
        )

    @staticmethod
    def _extract_location(row_record):
        """Extract the subject's location as a (longitude, latitude) tuple from
        'row_record'."""
        return float(row_record['Data.Longitude']), float(row_record['Data.Latitude'])

    @staticmethod
    def _extract_date(row_record):
        """Extract the date from 'row_record'."""
        record_date = row_record['Data.Date'][:10]
        return date(
            int(record_date[:4]),
            int(record_date[5:7]),
            int(record_date[8:10])
        )

    @staticmethod
    def _extract_subject_id(filename):
        """Returns the ID of the subject in 'filename'."""
        return filename.split('/')[-1].split('_')[0]
