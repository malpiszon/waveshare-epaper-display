import os
import lnetatmo
import logging


def _module_name(var):
    name = os.getenv(var)
    if not name:
        raise RuntimeError(
            "{} is not set. Set it in env.sh to the Netatmo module name as shown in the Netatmo app.".format(var))
    return name


def get_temp():
    indoor = _module_name("NETATMO_INDOOR_MODULE")
    outdoor = _module_name("NETATMO_OUTDOOR_MODULE")
    base_station = _module_name("NETATMO_BASE_STATION")

    authorization = lnetatmo.ClientAuth()
    devList = lnetatmo.WeatherStationData(authorization)
    netatmo_data = devList.lastData()

    data = {}
    data["indoor_temp"] = netatmo_data[indoor]['Temperature']
    data["indoor_humidity"] = netatmo_data[indoor]['Humidity']
    data["indoor_co2"] = netatmo_data[indoor]['CO2']
    data["outdoor_temp"] = netatmo_data[outdoor]['Temperature']
    data["outdoor_temp_min"] = netatmo_data[outdoor]['min_temp']
    data["outdoor_temp_max"] = netatmo_data[outdoor]['max_temp']
    data["outdoor_humidity"] = netatmo_data[outdoor]['Humidity']
    data["pressure"] = netatmo_data[base_station]['Pressure']

    logging.debug(data)
    return data
