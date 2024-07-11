from openmeteopy import OpenMeteo
from openmeteopy.options import DwdOptions
from openmeteopy.hourly import HourlyDwd
from openmeteopy.daily import DailyDwd
from geopy import Nominatim
import json, pytz, requests
from datetime import datetime
from typing import Tuple


class Weather:
    """
    This class implements the retrieval and processing of weatherdata.
    """

    def __init__(self):
        """
        Constructor for the Weather class
        """
        pass

    def get_forecast(self, city:str, country:str) -> Tuple[dict, int]:
        """
        This function retrieves the forecast for a given city and country
        """

        response_dict = {
            'status': '',
            'message': '',
            'data': {}
        }

        try:
            latitude, longitude = self._get_coordinates_for_city(city, country)
        except ValueError as e:
            response_dict['status'] = 'error'
            response_dict['message'] = str(e)
            return response_dict, 400

        uncleaned_data = self._get_weather_data(latitude, longitude)
        try:
            cleaned_data = self._clean_weather_data(uncleaned_data)
        except Exception as e:
            response_dict['status'] = 'error'
            response_dict['message'] = str(e)
            return response_dict, 500
        
        cleaned_data['city'] = city
        cleaned_data['country'] = country
        cleaned_data['ai_text'] = self._get_ai_text(cleaned_data)
        response_dict['status'] = 'success'
        response_dict['data'] = cleaned_data
        response_dict['message'] = 'The weather data was successfully retrieved'

        return response_dict, 200
    

    def _get_coordinates_for_city(self, city:str, country:str) -> tuple:
        """
        This function retrieves the coordinates for a given city and country

        :param city: The city for which the coordinates should be retrieved
        :type city: str
        :param country: The country in which the city is located
        :type country: str
        :return: The latitude and longitude of the city as a tuple `(latitude, longitude)`
        """

        geolocator = Nominatim(user_agent="weather")

        location = geolocator.geocode(f"{city}, {country}")

        if location is None:
            raise ValueError(f"We could not find the coordinates for the City: {city} in the Country: {country}")
        
        return location.latitude, location.longitude
    

    def _get_weather_data(self, latitude:float, longitude:float) -> dict:
        """
        This method is designed to retrieve the weather data for a given latitude and longitude

        :param latitude: the latitude of the location
        :type latitude: float
        :param longitude: the longitude of the location
        :type longitude: float
        :return: a dictionary containing the weather data
        """

        hourly = HourlyDwd()
        daily = DailyDwd()
        options = DwdOptions(latitude, longitude, timezone='Europe/Berlin')

        open_meteo_manager = OpenMeteo(options, hourly.all(), daily.all())
        weather_dict = open_meteo_manager.get_dict()

        return weather_dict
    

    def _clean_weather_data(self, weather_data:dict) -> dict:
        """
        This function is designed to clean the weather data

        :param weather_data: The weather data that should be cleaned
        :type weather_data: dict
        :return: The cleaned weather data
        """

        cleaned_data = {
            'hourly': {},
            'daily': {}
        }
        
        de_timezone = pytz.timezone('Europe/Berlin')
        current_hour = datetime.now(de_timezone).hour

        for i in range(0,len(weather_data['daily']['time'])-1):
            cleaned_data['daily'][weather_data['daily']['time'][i]] = {
                "max_temp": weather_data['daily']['temperature_2m_max'][i],
                "min_temp": weather_data['daily']['temperature_2m_min'][i],
                "niederschlag": weather_data['daily']['precipitation_sum'][i],
                "wetter": self._get_string_for_weather_code(weather_data['daily']['weathercode'][i]),
                "wind_geschwindigkeit": weather_data['daily']['windspeed_10m_max'][i],
                "wind_richtung": weather_data['daily']['winddirection_10m_dominant'][i]
            }

        for i in range(current_hour, current_hour + 12):
            cleaned_data['hourly'][weather_data['hourly']['time'][i]] = {
                "temp": weather_data['hourly']['temperature_2m'][i],
                "niederschlag": weather_data['hourly']['precipitation'][i],
                "wetter": self._get_string_for_weather_code(weather_data['hourly']['weathercode'][i]),
                "wind_geschwindigkeit": weather_data['hourly']['windspeed_10m'][i],
                "wind_richtung": weather_data['hourly']['winddirection_10m'][i],
                "luftdruck": weather_data['hourly']['pressure_msl'][i],
                "luftfeuchte": weather_data['hourly']['relativehumidity_2m'][i]
            }

        return cleaned_data
    
    def _get_ai_text(self, weather_data:dict) -> str:
        """
        This method will be used to actually implement the AI-Text generation
        Here, we'll run the request to the ollama api, and before we do that do the prompt-engineering

        :param weather_data: The weather data for which the AI-Text should be generated
        :type weather_data: dict
        :return: The AI-Text as string
        """

        ret_str = ""
        
        # TODO: Implement the AI-Text generation here

        return ret_str
        

    def _get_string_for_weather_code(self, weather_code:int) -> str:
        """
        This method is designed to return a string representation for a given weather code

        :param weather_code: The weather code for which a string representation should be returned
        :type weather_code: int
        :return: The string representation of the weather code
        """

        weather_dict = {
            0: "Wolkenentwicklung nicht bekannt, letzte Stunde",
            1: "Abnehmende Bewölkung, letzte Stunde",
            2: "Keine Bewölkungsänderung, letzte Stunde",
            3: "Zunehmende Bewölkung, letzte Stunde",
            4: "Sicht durch Rauch reduziert",
            5: "Dunst",
            6: "Schwebender Staub, ohne Windeinwirkung",
            7: "Staub oder Sand, vom Wind gehoben",
            8: "Staubteufel",
            9: "Staub- oder Sandsturm an der Station, oder in Sichtweite",
            10: "feuchter Dunst/schwacher Nebel",
            11: "Nebelschwaden am Boden",
            12: "Durchgehend Bodennebel",
            13: "Wetterleuchten (kein Donner)",
            14: "Niederschlag sichtbar, erreicht nicht den Boden",
            15: "Niederschlag in der Ferne, erreicht Boden",
            16: "Niederschlag in der Nähe, erreicht Boden",
            17: "Gewitter hörbar, kein Niederschlag",
            18: "Markante Windböen",
            19: "Tornado, Wasserhose oder Funnel",
            20: "Nach Sprühregen",
            21: "Nach Regen",
            22: "Nach Schnee",
            23: "Nach Schneeregen",
            24: "Nach gefrierendem Regen",
            25: "Nach Regenschauern",
            26: "Nach Schneeschauern",
            27: "Nach Hagelschauern",
            28: "Nach Nebel",
            29: "Nach Gewitter",
            30: "Leichter/mäßiger Sandsturm, nachlassend",
            31: "Leichter/mäßiger Sandsturm, gleichbleibend",
            32: "Leichter/mäßiger Sandsturm, zunehmend",
            33: "Schwerer Sandsturm, nachlassend",
            34: "Schwerer Sandsturm, gleichbleibend",
            35: "Schwerer Sandsturm, zunehmend",
            36: "Leichtes/mäßiges Schneefegen",
            37: "Starkes Schneefegen",
            38: "Leichtes/mäßiges Schneetreiben",
            39: "Starkes Schneetreiben",
            40: "Nebel in der Ferne",
            41: "Nebelschwaden",
            42: "Nebel, Himmel sichtbar, abnehmend",
            43: "Nebel, Himmel verdeckt, abnehmend",
            44: "Nebel, Himmel sichtbar, gleichbleibend",
            45: "Nebel, Himmel verdeckt, gleichbleibend",
            46: "Nebel, Himmel sichtbar, zunehmend",
            47: "Nebel, Himmel verdeckt, zunehmend",
            48: "Raueis mit Nebel, Himmel sichtbar",
            49: "Raueis mit Nebel, Himmel verdeckt",
            50: "Leichter Sprühregen, unterbrochen",
            51: "Leichter Sprühregen, anhaltend",
            52: "Mäßiger Sprühregen, unterbrochen",
            53: "Mäßiger Sprühregen, anhaltend",
            54: "Starker Sprühregen, unterbrochen",
            55: "Starker Sprühregen, anhaltend",
            56: "Gefrierender Sprühregen, leicht",
            57: "Gefrierender Sprühregen, mäßig/stark",
            58: "Leichter Regen und Sprühregen",
            59: "Mäßiger/Starker Regen und Sprühregen",
            60: "Leichter Regen, unterbrochen",
            61: "Leichter Regen, anhaltend",
            62: "Mäßiger Regen, unterbrochen",
            63: "Mäßiger Regen, anhaltend",
            64: "Starker Regen, unterbrochen",
            65: "Starker Regen, anhaltend",
            66: "Gefrierender leichter Regen",
            67: "Gefrierender mäßiger/starker Regen",
            68: "Leichter Schneeregen",
            69: "Mäßiger/Starker Schneeregen",
            70: "Leichter Schneefall, unterbrochen",
            71: "Leichter Schneefall, anhaltend",
            72: "Mäßiger Schneefall, unterbrochen",
            73: "Mäßiger Schneefall, anhaltend",
            74: "Starker Schneefall, unterbrochen",
            75: "Starker Schneefall, anhaltend",
            76: "Eisnadeln",
            77: "Schneegriesel",
            78: "Schneekristalle",
            79: "Eiskörner",
            80: "Leichte Regenschauer",
            81: "Starke Regenschauer",
            82: "Sintflutartige Regenschauer",
            83: "Leichte Schneeregenschauer",
            84: "Starke Schneeregenschauer",
            85: "Leichte Schneeschauer",
            86: "Starke Schneeschauer",
            87: "Leichte Graupelschauer",
            88: "Starke Graupelschauer",
            89: "Leichte Hagelschauer ohne Gewitter",
            90: "Starke Hagelschauer ohne Gewitter",
            91: "Leichter Regen, letzte Stunde Gewitter hörbar",
            92: "Starker Regen, letzte Stunde Gewitter hörbar",
            93: "Leichter Schnee/Regen-Hagel, letzte Stunde Gewitter hörbar",
            94: "Starker Schnee/Regen-Hagel, letzte Stunde Gewitter hörbar",
            95: "Leichtes/mäßiges Gewitter mit Regen/Schnee",
            96: "Leichtes/mäßiges Gewitter mit Hagel",
            97: "Schweres Gewitter mit Regen/Schnee",
            98: "Gewitter mit Sandsturm",
            99: "Schweres Gewitter mit Hagel"
        }
        return weather_dict.get(weather_code, "unbekannt")
    

if __name__ == "__main__":
    weather = Weather()
    print(weather.get_forecast("Berlin", "Germany"))