import logging
from weather_providers.base_provider import BaseWeatherProvider


class AccuWeather(BaseWeatherProvider):
    def __init__(self, accuweather_apikey, location_lat, location_long, location_key, units):
        self.accuweather_apikey = accuweather_apikey
        self.location_lat = location_lat
        self.location_long = location_long
        self.location_key = location_key
        self.units = units
        self.headers = { "Authorization" : "Bearer {}".format(self.accuweather_apikey),  "Accept-Encoding": "gzip,deflate" }

    # TODO use expire response header https://developer.accuweather.com/documentation/best-practices#use-the-expires-header

    # Map Accuweather icons to local icons
    # Reference: https://developer.accuweather.com/weather-icons
    def get_icon_from_accuweather_weathercode(self, weathercode, is_daytime):

        icon_dict = {
            1: "clear_sky_day" if is_daytime else "clearnight",  # Day - Sunny
            2: "clear_sky_day" if is_daytime else "clearnight",  # Day - Mostly Sunny
            3: "few_clouds" if is_daytime else "partlycloudynight",  # Day - Partly Sunny
            4: "scattered_clouds" if is_daytime else "partlycloudynight",  # Day - Intermittent Clouds
            5: "haze",  # Day - Hazy Sunshine
            6: "mostly_cloudy" if is_daytime else "mostly_cloudy_night",  # Day - Mostly Cloudy
            7: "climacell_cloudy" if is_daytime else 'mostly_cloudy_night',  # DayNight - Cloudy
            8: "overcast",  # DayNight - Dreary (Overcast)
            11: "climacell_fog",  # DayNight - Fog
            12: 'climacell_rain_light' if is_daytime else 'rain_night_light',  # DayNight - Showers
            13: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',
            # Day - Mostly Cloudy w/ Showers
            14: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',  # Day - Partly Sunny w/ Showers
            15: "thundershower_rain",  # DayNight - T-Storms
            16: "scattered_thundershowers",  # Day - Mostly Cloudy w/ T-Storms
            17: "scattered_thundershowers",  # Day - Partly Sunny w/ T-Storms
            18: "climacell_rain" if is_daytime else "rain_night",  # DayNight - Rain
            19: "climacell_flurries",  # DayNight - Flurries
            20: "climacell_flurries",  # Day - Mostly Cloudy w/ Flurries
            21: "climacell_flurries",  # Day - Partly Sunny w/ Flurries
            22: "snow",  # DayNight - Snow
            23: "snow",  # Day - Mostly Cloudy w/ Snow
            24: "climacell_freezing_rain",  # DayNight - Ice
            25: "sleet",  # DayNight - Sleet
            26: "climacell_freezing_rain",  # DayNight - Freezing Rain
            29: "sleet",  # DayNight - Rain and Snow
            30: "very_hot",  # DayNight - Hot
            31: "cold",  # DayNight - Cold
            32: "wind",  # DayNight - Windy
            33: "clear_sky_day" if is_daytime else "clearnight",  # Night - Clear
            34: "clear_sky_day" if is_daytime else "clearnight",  # Night - Mostly Clear
            35: "few_clouds" if is_daytime else "partlycloudynight",  # Night - Partly Cloudy
            36: "scattered_clouds" if is_daytime else "partlycloudynight",  # Night - Intermittent Clouds
            37: "haze",  # Night - Hazy Moonlight
            38: "mostly_cloudy" if is_daytime else "mostly_cloudy_night",  # Night - Mostly Cloudy
            39: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',
            # Night - Partly Cloudy w/ Showers
            40: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',
            # Night - Mostly Cloudy w/ Showers
            41: "thundershower_rain",  # Night - Partly Cloudy w/ T-Storms
            42: "thundershower_rain",  # Night - Mostly Cloudy w/ T-Storms
            43: "climacell_flurries",  # Night - Mostly Cloudy w/ Flurries
            44: "snow"  # Night - Mostly Cloudy w/ Snow
        }

        icon = icon_dict[weathercode]
        logging.debug(
            "get_icon_by_weathercode({}, {}) - {}"
            .format(weathercode, is_daytime, icon))

        return icon

    def get_weather_icon(self, weather_data, day_no=0, daytime: bool = True):
        if day_no == 0:
            accuweather_icon = weather_data["DailyForecasts"][0]["Day"]["Icon"] if daytime else weather_data[
                "DailyForecasts"][0]["Night"]["Icon"]
        else:
            accuweather_icon = weather_data["DailyForecasts"][day_no]["Day"]["Icon"]

        return accuweather_icon

    # Get weather from Accuweather Daily Forecast API
    # https://developer.accuweather.com/accuweather-forecast-api/apis/get/forecasts/v1/daily/1day/%7BlocationKey%7D
    def get_daily_weather(self, days=2):
        url = ("http://dataservice.accuweather.com/forecasts/v1/daily/5day/{}?details=true&metric={}"
               .format(self.location_key, "true" if self.units == "metric" else "false"))

        response_data = self.get_response_json(url, "daily", self.headers)
        weather_data = response_data
        logging.debug("get_daily_weather() - {}".format(weather_data))

        # {0: { "temperatureMin": "2.0", "temperatureMax": "15.1", "icon": "mostly_cloudy", "description":"Cloudy with light breezes" }}
        weather = {}
        daytime = self.is_daytime(self.location_lat, self.location_long)
        for day_no in range(days + 1):
            weather[day_no] = {}
            forecast_daytime = daytime if day_no == 0 else True
            weather[day_no]["temperatureMin"] = weather_data["DailyForecasts"][day_no]["Temperature"]["Minimum"]["Value"]
            weather[day_no]["temperatureMax"] = weather_data["DailyForecasts"][day_no]["Temperature"]["Maximum"]["Value"]
            weather[day_no]["sunRise"] = weather_data["DailyForecasts"][day_no]["Sun"]["EpochRise"]
            weather[day_no]["sunSet"] = weather_data["DailyForecasts"][day_no]["Sun"]["EpochSet"]
            weather[day_no]["hoursOfSun"] = weather_data["DailyForecasts"][day_no]["HoursOfSun"]
            weather[day_no]["icon"] = self.get_icon_from_accuweather_weathercode(self.get_weather_icon(weather_data, day_no, daytime), forecast_daytime)
            weather[day_no]["description"] = weather_data["DailyForecasts"][day_no]["Day"]["ShortPhrase"] if forecast_daytime else weather_data["DailyForecasts"][day_no]["Night"]["ShortPhrase"]
            weather[day_no]["windSpeed"] = weather_data["DailyForecasts"][day_no]["Day"]["Wind"]["Speed"]["Value"] if forecast_daytime else weather_data["DailyForecasts"][day_no]["Night"]["Wind"]["Speed"]["Value"]
            weather[day_no]["windDirection"] = weather_data["DailyForecasts"][day_no]["Day"]["Wind"]["Direction"]["English"] if forecast_daytime else weather_data["DailyForecasts"][day_no]["Night"]["Wind"]["Direction"]["English"]
            weather[day_no]["windGustSpeed"] = weather_data["DailyForecasts"][day_no]["Day"]["WindGust"]["Speed"]["Value"] if forecast_daytime else weather_data["DailyForecasts"][day_no]["Night"]["WindGust"]["Speed"]["Value"]
            weather[day_no]["windGustDirection"] = weather_data["DailyForecasts"][day_no]["Day"]["WindGust"]["Direction"]["English"] if forecast_daytime else weather_data["DailyForecasts"][day_no]["Night"]["WindGust"]["Direction"]["English"]
            weather[day_no]["rainValue"] = weather_data["DailyForecasts"][day_no]["Day"]["Rain"]["Value"]
            weather[day_no]["rainUnit"] = weather_data["DailyForecasts"][day_no]["Day"]["Rain"]["Unit"]
            weather[day_no]["rainProbability"] = weather_data["DailyForecasts"][day_no]["Day"]["RainProbability"]
            weather[day_no]["snowValue"] = weather_data["DailyForecasts"][day_no]["Day"]["Snow"]["Value"]
            weather[day_no]["snowUnit"] = weather_data["DailyForecasts"][day_no]["Day"]["Snow"]["Unit"]
            weather[day_no]["snowProbability"] = weather_data["DailyForecasts"][day_no]["Day"]["SnowProbability"]
            weather[day_no]["precipitationProbability"] = weather_data["DailyForecasts"][day_no]["Day"]["PrecipitationProbability"]

        weather['cache_daily_age'] = self.get_cache_age("cache_weather_daily.json")
        logging.debug(weather)
        return weather

    # Get weather from Accuweather Hourly Forecast API
    # https://developer.accuweather.com/accuweather-forecast-api/apis/get/forecasts/v1/hourly/12hour/%7BlocationKey%7D
    def get_hourly_weather(self, hours=4):
        url = ("http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{}?details=true&metric={}"
               .format(self.location_key, "true" if self.units == "metric" else "false"))

        response_data = self.get_response_json(url, "hourly", self.headers)
        weather_data = response_data
        logging.debug("get_hourly_weather() - {}".format(weather_data))

        # {"1731852000": {"temperature": "2.0", "icon": "mostly_cloudy"}}
        weather = {}
        hour = 0
        for hour_weather_data in weather_data:
            if hour >= hours:
                break

            date_time = hour_weather_data["EpochDateTime"]
            daytime = (hour_weather_data["IsDaylight"] or hour_weather_data["IsDaylight"] == "true")
            weather[date_time] = {}
            weather[date_time]["temperature"] = hour_weather_data["Temperature"]["Value"]
            weather[date_time]["icon"] = self.get_icon_from_accuweather_weathercode(hour_weather_data["WeatherIcon"],
                                                                                    daytime)
            weather[date_time]["precipitation_probability"] = hour_weather_data["PrecipitationProbability"]
            weather[date_time]["rft_value"] = hour_weather_data["RealFeelTemperature"]["Value"]

            hour = hour + 1

        weather['cache_hourly_age'] = self.get_cache_age("cache_weather_hourly.json")
        logging.debug(weather)
        return weather

    # Get weather from Accuweather Current Conditions API
    # https://dataservice.accuweather.com/currentconditions/v1/{locationKey}
    def get_current_conditions(self, hours=4):
        current_weather_ttl = 60 * 15 - 10
        url = ("https://dataservice.accuweather.com/currentconditions/v1/{}?details=true&metric={}"
               .format(self.location_key, "true" if self.units == "metric" else "false"))

        response_data = self.get_response_json_ttl(url, current_weather_ttl, "current", self.headers)
        weather_data = response_data
        logging.debug("get_current_conditions() - {}".format(weather_data))

        weather = {}
        weather["rft_phrase"] = weather_data[0]["RealFeelTemperature"]["Metric"]["Phrase"]
        weather["rft_value"] = weather_data[0]["RealFeelTemperature"]["Metric"]["Value"]
        weather["rft_unit"] = weather_data[0]["RealFeelTemperature"]["Metric"]["Unit"]

        weather['cache_current_age'] = self.get_cache_age("cache_weather_current.json")
        logging.debug(weather)
        return weather
