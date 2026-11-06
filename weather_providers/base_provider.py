import os
from abc import ABC, abstractmethod
from utility import get_xml_from_url, get_json_from_url
import logging
from astral import LocationInfo
from astral.sun import sun
import datetime
import pytz


class BaseWeatherProvider(ABC):

    ttl = float(os.getenv("WEATHER_TTL", 1 * 60 * 60 - 10))

    @abstractmethod
    def get_daily_weather(self, days=2):
        """
        Implement this method.
        Return a dictionary in this format:
        {0: { "temperatureMin": "2.0", "temperatureMax": "15.1", "icon": "mostly_cloudy", "description": "Cloudy with light breezes" }}
        """
        pass

    @abstractmethod
    def get_hourly_weather(self, hours=4):
        """
        Implement this method.
        Return a dictionary in this format:
        {"1731852000": {"temperature": "2.0", "icon": "mostly_cloudy"}}
        """
        pass

    def f_to_c(self, fahrenheit):
        """
        Return the Celsius value from a given Fahrenheit
        """
        return float((fahrenheit - 32) * 5/9)

    def c_to_f(self, celsius):
        """
        Return the Fahrenheit value from a given Celsius
        """
        return (float(celsius)*9/5) + 32

    def is_daytime(self, location_lat, location_long, dt=None):
        """
        Return whether it's daytime for a given lat/long.
        """

        # adjust icon for sunrise and sunset
        if dt is None:
            dt = datetime.datetime.now(pytz.utc)
        city = LocationInfo(latitude=location_lat, longitude=location_long)
        s = sun(city.observer, date=dt)
        verdict = False
        if dt > s['sunset'] or dt < s['sunrise']:
            verdict = False
        else:
            verdict = True

        logging.debug(
            "is_daytime({}, {}) - {}"
            .format(str(location_lat), str(location_long), str(verdict)))

        return verdict

    def get_response_json(self, url, suffix="generic", headers={}):
        """
        Perform an HTTP GET for a `url` with optional `headers`.
        Caches the response in `cache_file_name` for WEATHER_TTL seconds.
        Returns the response as JSON
        """
        return get_json_from_url(url, headers, f"cache_weather_{suffix}.json", self.ttl)

    def get_response_json_ttl(self, url, ttl, suffix="generic", headers={}):
        """
        Perform an HTTP GET for a `url` with optional `headers`.
        Caches the response in `cache_file_name` for ttl seconds.
        Returns the response as JSON
        """
        return get_json_from_url(url, headers, f"cache_weather_{suffix}.json", ttl)

    def get_response_xml(self, url, suffix="generic", headers={}):
        """
        Perform an HTTP GET for a `url` with optional `headers`.
        Caches the response in `cache_file_name` for WEATHER_TTL seconds.
        Returns the response as an XML ElementTree
        """
        return get_xml_from_url(url, headers, f"cache_weather_{suffix}.xml", self.ttl)

    def get_cache_age(self, cache_file_name):
        """
        Return the age of the cache file in seconds.
        """
        if os.path.exists(cache_file_name):
            return (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cache_file_name))).total_seconds()
        return 0
