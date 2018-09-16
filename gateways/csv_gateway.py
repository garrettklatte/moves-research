"""Module for csv_gateway."""

import csv
from datetime import date
from definitions import SubjectLocationSummary, WeatherSummary

class CsvGateway:
    def __init__(self, filename):
        """'filename' is the name of file containing all of the persisted data.
        """
        self._filename = filename
        self.fieldnames = [
            'subject_id',
            'longitude',
            'latitude',
            'date',
            'mean_temp',
            'max_temp',
            'min_temp',
            'precipitation'
        ]

        try:
            with open(self._filename, 'x') as csvfile:
                writer = csv.DictWriter(csvfile, self.fieldnames)
                writer.writeheader()
        except FileExistsError:
            pass
        
    def record_weather_summary(self, weather_summary, subject_location_summary):
        """Record 'weather_summary' and associate it with
        'subject_location_summary'.
        """
        with open(self._filename, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, self.fieldnames)

            row = CsvGateway._make_row(weather_summary, subject_location_summary)

            writer.writerow(row)

    def fetch_weather_summary(self, subject_location_summary):
        """Fetch the weather summary associated with
        'subject_location_summary'. Return None if no such weather summary
        exists.
        """
        with open(self._filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                extracted_summary = CsvGateway._extract_subject_location_summary(
                    row
                )
                if extracted_summary == subject_location_summary:
                    return CsvGateway._extract_weather_summary(row)
            else:
                return None    

    @staticmethod
    def _extract_subject_location_summary(row):
        print(row)
        return SubjectLocationSummary(
            row['subject_id'],
            float(row['longitude']),
            float(row['latitude']),
            date.fromisoformat(row['date'])
        )

    @staticmethod
    def _extract_weather_summary(row):
        return WeatherSummary(
            float(row['mean_temp']),
            float(row['max_temp']),
            float(row['min_temp']),
            float(row['precipitation'])
        )

    @staticmethod
    def _make_row(weather_summary, subject_location_summary):
        return {
            'subject_id': subject_location_summary.subject_id,
            'longitude': subject_location_summary.longitude,
            'latitude': subject_location_summary.latitude,
            'date': subject_location_summary.date.isoformat(),
            'mean_temp': weather_summary.mean_temp,
            'max_temp': weather_summary.max_temp,
            'min_temp': weather_summary.min_temp,
            'precipitation': weather_summary.precipitation
        }