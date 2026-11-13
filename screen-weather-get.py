#!/usr/bin/python

import datetime
import sys
import os
import logging
from weather_providers import climacell, openweathermap, metofficedatahub, metno, meteireann, accuweather, visualcrossing, weathergov, smhi, netatmo
from alert_providers import metofficerssfeed, weathergovalerts
from alert_providers import meteireann as meteireannalertprovider
from utility import get_formatted_time, update_svg, configure_logging, configure_locale
import textwrap
import html

configure_locale()
configure_logging()


def format_weather_description(weather_description):
    if len(weather_description) < 20:
        return {1: weather_description, 2: ''}

    splits = textwrap.fill(weather_description, 20, break_long_words=False, max_lines=2, placeholder='...').split('\n')
    weather_dict = {1: splits[0], 2: splits[1] if len(splits) > 1 else ''}
    return weather_dict


def get_weather_provider(location_lat, location_long, units):
    # gather relevant environment configs
    climacell_apikey = os.getenv("CLIMACELL_APIKEY")
    openweathermap_apikey = os.getenv("OPENWEATHERMAP_APIKEY")
    metoffice_apikey = os.getenv("METOFFICEDATAHUB_API_KEY")
    accuweather_apikey = os.getenv("ACCUWEATHER_APIKEY")
    accuweather_locationkey = os.getenv("ACCUWEATHER_LOCATIONKEY")
    metno_self_id = os.getenv("METNO_SELF_IDENTIFICATION")
    visualcrossing_apikey = os.getenv("VISUALCROSSING_APIKEY")
    use_met_eireann = os.getenv("WEATHER_MET_EIREANN")
    weathergov_self_id = os.getenv("WEATHERGOV_SELF_IDENTIFICATION")
    smhi_self_id = os.getenv("SMHI_SELF_IDENTIFICATION")

    if (
            not climacell_apikey
            and not openweathermap_apikey
            and not metoffice_apikey
            and not accuweather_apikey
            and not metno_self_id
            and not visualcrossing_apikey
            and not use_met_eireann
            and not weathergov_self_id
            and not smhi_self_id
    ):
        logging.error(
            "No weather provider has been configured (Climacell, OpenWeatherMap, Weather.gov, MetOffice, AccuWeather, Met.no, Met Eireann, VisualCrossing...)")
        sys.exit(1)

    if visualcrossing_apikey:
        logging.info("Getting weather from Visual Crossing")
        weather_provider = visualcrossing.VisualCrossing(visualcrossing_apikey, location_lat, location_long, units)

    elif use_met_eireann:
        logging.info("Getting weather from Met Eireann")
        weather_provider = meteireann.MetEireann(location_lat, location_long, units)

    elif weathergov_self_id:
        logging.info("Getting weather from Weather.gov")
        weather_provider = weathergov.WeatherGov(weathergov_self_id, location_lat, location_long, units)

    elif metno_self_id:
        logging.info("Getting weather from Met.no")
        weather_provider = metno.MetNo(metno_self_id, location_lat, location_long, units)

    elif accuweather_apikey:
        logging.info("Getting weather from Accuweather")
        weather_provider = accuweather.AccuWeather(accuweather_apikey, location_lat,
                                                   location_long,
                                                   accuweather_locationkey,
                                                   units)

    elif metoffice_apikey:
        logging.info("Getting weather from Met Office Weather Datahub")
        weather_provider = metofficedatahub.MetOffice(metoffice_apikey,
                                                      location_lat,
                                                      location_long,
                                                      units)

    elif openweathermap_apikey:
        logging.info("Getting weather from OpenWeatherMap")
        weather_provider = openweathermap.OpenWeatherMap(openweathermap_apikey,
                                                         location_lat,
                                                         location_long,
                                                         units)

    elif climacell_apikey:
        logging.info("Getting weather from Climacell")
        weather_provider = climacell.Climacell(climacell_apikey, location_lat, location_long, units)

    elif smhi_self_id:
        logging.info("Getting weather from SMHI")
        weather_provider = smhi.SMHI(smhi_self_id, location_lat, location_long, units)

    return weather_provider


def get_daily_weather(location_lat, location_long, units):
    weather = get_weather_provider(location_lat, location_long, units).get_daily_weather()
    logging.info("daily weather - {}".format(weather))
    return weather


def get_hourly_weather(location_lat, location_long, units):
    weather = get_weather_provider(location_lat, location_long, units).get_hourly_weather()
    logging.info("hourly weather - {}".format(weather))
    return weather

def get_current_weather(location_lat, location_long, units):
    weather = get_weather_provider(location_lat, location_long, units).get_current_conditions()
    logging.info("current conditions - {}".format(weather))
    return weather


def get_netatmo_weather():
    netatmo_data = netatmo.get_temp()
    logging.info("netatmo weather - {}".format(netatmo_data))
    return netatmo_data


def format_alert_description(alert_message):
    return html.escape(alert_message)


def get_wind_direction_icon(direction):
    if not direction or not isinstance(direction, str):
        logging.warning("Wind direction is missing or not a string.")
        return ''

    # Normalize to lowercase for case-insensitive matching
    direction = direction.lower().strip()

    # Mapping from detailed to 8-point compass
    if 'n' in direction and 'e' in direction:
        icon_name = 'ne'
    elif 's' in direction and 'e' in direction:
        icon_name = 'se'
    elif 's' in direction and 'w' in direction:
        icon_name = 'sw'
    elif 'n' in direction and 'w' in direction:
        icon_name = 'nw'
    elif 'n' in direction:
        icon_name = 'n'
    elif 'e' in direction:
        icon_name = 'e'
    elif 's' in direction:
        icon_name = 's'
    elif 'w' in direction:
        icon_name = 'w'
    else:
        logging.warning(f"Could not determine a direction from '{direction}'.")
        return ''

    return f'icons2/arrow_{icon_name}.svg'


def get_alert_message(location_lat, location_long):
    alert_message = ""
    alert_metoffice_feed_url = os.getenv("ALERT_METOFFICE_FEED_URL")
    alert_weathergov_self_id = os.getenv("ALERT_WEATHERGOV_SELF_IDENTIFICATION")
    alert_meteireann_feed_url = os.getenv("ALERT_MET_EIREANN_FEED_URL")

    if alert_weathergov_self_id:
        logging.info("Getting weather alert from Weather.gov API")
        alert_provider = weathergovalerts.WeatherGovAlerts(location_lat, location_long, alert_weathergov_self_id)
        alert_message = alert_provider.get_alert()

    elif alert_metoffice_feed_url:
        logging.info("Getting weather alert from Met Office RSS Feed")
        alert_provider = metofficerssfeed.MetOfficeRssFeed(alert_metoffice_feed_url)
        alert_message = alert_provider.get_alert()

    elif alert_meteireann_feed_url:
        logging.info("Getting weather alert from Met Eireann")
        alert_provider = meteireannalertprovider.MetEireannAlertProvider(alert_meteireann_feed_url)
        alert_message = alert_provider.get_alert()

    logging.info("alert - {}".format(alert_message))
    return alert_message


def current_time_plus_hours(curr_datetime, plus_hours):
    return (curr_datetime + datetime.timedelta(hours=plus_hours)).replace(minute=0, second=0)


def current_time_plus_hours_as_timestamp(curr_datetime, plus_hours):
    return int(current_time_plus_hours(curr_datetime, plus_hours).timestamp())


def main():

    template_name = os.getenv("SCREEN_LAYOUT", "1")
    location_lat = os.getenv("WEATHER_LATITUDE", "51.5077")
    location_long = os.getenv("WEATHER_LONGITUDE", "-0.1277")
    weather_format = os.getenv("WEATHER_FORMAT", "CELSIUS")

    if weather_format == "CELSIUS":
        units = "metric"
        degrees = "°C"
    else:
        units = "imperial"
        degrees = "°F"

    daily_weather = get_daily_weather(location_lat, location_long, units)

    if not daily_weather:
        logging.error("Unable to fetch daily weather payload. SVG will not be updated.")
        sys.exit(1)

    hourly_weather = get_hourly_weather(location_lat, location_long, units)

    if not hourly_weather:
        logging.error("Unable to fetch hourly weather payload. SVG will not be updated.")
        sys.exit(1)

    current_weather = get_current_weather(location_lat, location_long, units)

    if not current_weather:
        logging.error("Unable to fetch current conditions payload. SVG will not be updated.")
        sys.exit(1)

    logging.info("Getting weather from Netatmo")
    netatmo_data = get_netatmo_weather()

    if not netatmo_data:
        logging.error("Unable to fetch Netatmo payload. SVG will not be updated.")
        sys.exit(1)

    weather_0_desc = format_weather_description(daily_weather[0]["description"])
    weather_1_desc = format_weather_description(daily_weather[1]["description"])
    weather_2_desc = format_weather_description(daily_weather[2]["description"])
    only_rain = daily_weather[0]['snowValue'] == 0
    rather_rain_than_snow = (daily_weather[0]['rainProbability'] > daily_weather[0]['snowProbability']) or (daily_weather[0]['rainProbability'] == daily_weather[0]['snowProbability'] and float(netatmo_data['outdoor_temp']) >= 0)
    rain_snow_icon = 'rain' if (only_rain and float(netatmo_data['outdoor_temp']) >= 0) else ('snow' if not rather_rain_than_snow else 'sleet')
    rain_and_snow_value = daily_weather[0]['rainValue'] if rather_rain_than_snow else daily_weather[0]['snowValue']
    rain_and_snow_unit = daily_weather[0]['rainUnit'] if rather_rain_than_snow else daily_weather[0]['snowUnit']
    wind_direction_icon_path = get_wind_direction_icon(str(daily_weather[0]['windDirection']))

    curr_datetime = datetime.datetime.now()
    hplus1timestamp = current_time_plus_hours_as_timestamp(curr_datetime, 1)
    hplus2timestamp = current_time_plus_hours_as_timestamp(curr_datetime, 2)
    hplus3timestamp = current_time_plus_hours_as_timestamp(curr_datetime, 3)
    time_now = "Updated: {}, cache age: {:.0f} min".format(get_formatted_time(curr_datetime), daily_weather['cache_daily_age'] // 60)

    output_dict = {
        'CURR_INS': "Inside: {:.1f}{}".format(netatmo_data['indoor_temp'], degrees),
        'CO2': "{}ppm".format(str(netatmo_data['indoor_co2'])),
        'INSIDE_HUMIDITY': "{}%".format(str(netatmo_data['indoor_humidity'])),
        'CURR_OUT': "Outside: {:.1f}{}".format(netatmo_data['outdoor_temp'], degrees),
        'FEELS_LIKE_TEXT': "{:.1f}{}".format(current_weather['rft_value'], degrees),
        'MIN_TEMP_TEXT': "{:.1f}{}".format(netatmo_data['outdoor_temp_min'], degrees),
        'MAX_TEMP_TEXT': "{:.1f}{}".format(netatmo_data['outdoor_temp_max'], degrees),
        'SUNRISE_TEXT': get_formatted_time(datetime.datetime.fromtimestamp(daily_weather[0]['sunRise'])),
        'SUNSET_TEXT': get_formatted_time(datetime.datetime.fromtimestamp(daily_weather[0]['sunSet'])),
        'SUNTIME_TEXT': "{:.1f}h".format(daily_weather[0]['hoursOfSun']),
        'RAIN_SNOW_TEXT': "{:.1f}{}".format(rain_and_snow_value, rain_and_snow_unit),
        'RAIN_SNOW_ICON': rain_snow_icon,
        'HUMIDITY': "{}%".format(str(netatmo_data['outdoor_humidity'])),
        'PRECIPITATION': "{}%".format(daily_weather[0]['precipitationProbability']),
        'PRESSURE': "Pressure: {}mbar".format(str(netatmo_data['pressure'])),
        'WIND_TEXT': "{:.0f}|{:.0f} km/h".format(daily_weather[0]['windSpeed'], daily_weather[0]['windGustSpeed']),
        'WIND_DIRECTION_ICON': wind_direction_icon_path,
        'LOW_ONE': "{:.1f}{}".format(daily_weather[0]['temperatureMin'], degrees),
        'HIGH_ONE': "{:.1f}".format(daily_weather[0]['temperatureMax']),
        'ICON_ONE': daily_weather[0]["icon"],
        'WEATHER_DESC_1': weather_0_desc[1],
        'WEATHER_DESC_2': weather_0_desc[2],
        'HPLUS1_NAME': get_formatted_time(current_time_plus_hours(curr_datetime, 1)),
        'HPLUS1_TEMP': "{:.1f}{}".format(hourly_weather[hplus1timestamp]['temperature'], degrees),
        'ICON_HPLUS1': hourly_weather[hplus1timestamp]["icon"],
        'HPLUS1_PRECIP': "{}%".format(hourly_weather[hplus1timestamp]['precipitation_probability']),
        'HPLUS1_RFT': "{:.1f}{}".format(hourly_weather[hplus1timestamp]['rft_value'], degrees),
        'HPLUS2_NAME': get_formatted_time(current_time_plus_hours(curr_datetime, 2)),
        'HPLUS2_TEMP': "{:.1f}{}".format(hourly_weather[hplus2timestamp]['temperature'], degrees),
        'ICON_HPLUS2': hourly_weather[hplus2timestamp]["icon"],
        'HPLUS2_PRECIP': "{}%".format(hourly_weather[hplus2timestamp]['precipitation_probability']),
        'HPLUS2_RFT': "{:.1f}{}".format(hourly_weather[hplus2timestamp]['rft_value'], degrees),
        'HPLUS3_NAME': get_formatted_time(current_time_plus_hours(curr_datetime, 3)),
        'HPLUS3_TEMP': "{:.1f}{}".format(hourly_weather[hplus3timestamp]['temperature'], degrees),
        'ICON_HPLUS3': hourly_weather[hplus3timestamp]["icon"],
        'HPLUS3_PRECIP': "{}%".format(hourly_weather[hplus3timestamp]['precipitation_probability']),
        'HPLUS3_RFT': "{:.1f}{}".format(hourly_weather[hplus3timestamp]['rft_value'], degrees),
        'DPLUS1_NAME': (curr_datetime + datetime.timedelta(days=1)).strftime("%A"),
        'LOW_DPLUS1': "{:.1f}{}".format(daily_weather[1]['temperatureMin'], degrees),
        'HIGH_DPLUS1': "{:.1f}".format(daily_weather[1]['temperatureMax']),
        'ICON_DPLUS1': daily_weather[1]["icon"],
        'PRECIP_DPLUS1_TEXT': "{}%".format(daily_weather[1]['precipitationProbability']),
        'SUNTIME_DPLUS1_TEXT': "{:.1f}h".format(daily_weather[1]['hoursOfSun']),
        'WIND_DPLUS1_TEXT': "{:.0f}|{:.0f} km/h".format(daily_weather[1]['windSpeed'], daily_weather[1]['windGustSpeed']),
        'WEATHER_DESC_DPLUS1_1': weather_1_desc[1],
        'WEATHER_DESC_DPLUS1_2': weather_1_desc[2],
        'DPLUS2_NAME': (curr_datetime + datetime.timedelta(days=2)).strftime("%A"),
        'LOW_DPLUS2': "{:.1f}{}".format(daily_weather[2]['temperatureMin'], degrees),
        'HIGH_DPLUS2': "{:.1f}".format(daily_weather[2]['temperatureMax']),
        'ICON_DPLUS2': daily_weather[2]["icon"],
        'PRECIP_DPLUS2_TEXT': "{}%".format(daily_weather[2]['precipitationProbability']),
        'SUNTIME_DPLUS2_TEXT': "{:.1f}h".format(daily_weather[2]['hoursOfSun']),
        'WIND_DPLUS2_TEXT': "{:.0f}|{:.0f} km/h".format(daily_weather[2]['windSpeed'], daily_weather[2]['windGustSpeed']),
        'WEATHER_DESC_DPLUS2_1': weather_2_desc[1],
        'WEATHER_DESC_DPLUS2_2': weather_2_desc[2],
        'TIME_NOW': time_now,
        'HOUR_NOW': curr_datetime.strftime("%-I %p"),
        'DAY_NAME': "{}, {}".format(curr_datetime.strftime("%A"), curr_datetime.strftime("%b %-d")),
    }

    logging.info(output_dict)

    logging.info("Updating SVG")

    template_svg_filename = f'screen-template.{template_name}.svg'
    output_svg_filename = 'screen-output-weather.svg'
    update_svg(template_svg_filename, output_svg_filename, output_dict)


if __name__ == "__main__":
    main()
