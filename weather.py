import requests
import pandas as pd
import matplotlib.pyplot as plt
from config import WEATHER_GOV_API, WEATHER_GOV_HEADERS, WEATHER_GOV_STATIONS_API, WEATHER_GOV_FORECAST_API, WEATHER_GOV_FORECAST_HOURLY_API, WEATHER_GOV_RADAR_STATIONS_API, WEATHER_GOV_OBSERVATIONS_API

def get_radar_stations():
    """
    Fetches radar stations from the National Weather Service API.
    Returns: {
        '@id': 'https://api.weather.gov/radar/stations/TDAY', 
        '@type': 'wx:RadarStation', 
        'id': 'TDAY', 
        'name': 'Dayton', 
        'stationType': 'TDWR', 
        'geometry': 'POINT(-84.123 40.022)', 
        'elevation': {'unitCode': 'wmoUnit:m', 'value': 310.59118}, 
        'timeZone': 'GMT', 
        'latency': {
            'current': {'unitCode': 'nwsUnit:s', 'value': 0.143095}, 
            'average': {'unitCode': 'nwsUnit:s', 'value': 0.28}, 
            'max': {'unitCode': 'nwsUnit:s', 'value': 5}, 
            'levelTwoLastReceivedTime': '2025-07-10T20:16:58+00:00', 
            'maxLatencyTime': '2025-07-10T20:07:24+00:00', 
            'reportingHost': 'rdss', 
            'host': 'ldm4'}, 
            'rda': {
                'timestamp': '2025-07-10T20:14:48+00:00', 
                'reportingHost': 'rdss', 
                'properties': {
                    'resolutionVersion': None, 
                    'nl2Path': 'Default', 
                    'volumeCoveragePattern': 'L80', 
                    'buildNumber': 2, 
                    'alarmSummary': 'No Alarms', 
                    'operabilityStatus': 'RDA - On-line', 
                    'status': 'Operate', 
                    'controlStatus': 'Local Only', 
                    'mode': 'Operational'
                }
            }
        }
    """
    response = requests.get(WEATHER_GOV_RADAR_STATIONS_API, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json().get('@graph', [])
    else:
        print(f"Error fetching radar stations: {response.status_code} - {response.text}")
        return []


def get_stations(state='MA'):
    """
    Fetches weather stations from the National Weather Service API.
    Returns: {
        '@id': 'https://api.weather.gov/stations/022PG',
        '@type': 'wx:ObservationStation',
        'geometry': 'POINT(-120.11951 38.13141)',
        'elevation': {'unitCode': 'wmoUnit:m', 'value': 1615.44},
        'stationIdentifier': '022PG',
        'name': 'Long Barn',
        'timeZone': 'America/Los_Angeles', 
        'forecast': 'https://api.weather.gov/zones/forecast/CAZ069',
        'county': 'https://api.weather.gov/zones/county/CAC109',\
        'fireWeatherZone': 'https://api.weather.gov/zones/fire/CAZ221'
    }
    """
    stations = []
    url = f"{WEATHER_GOV_STATIONS_API}?limit=500&state={state}"

    while url:
        response = requests.get(url, headers=WEATHER_GOV_HEADERS)
        if response.status_code == 200:
            data = response.json()
            station_data = data.get('@graph', [])
            if not station_data:
                break
            # print([{'name': station['name'], 'type': station['@type']} for station in station_data])
            stations.extend(station_data)
            url = data.get('pagination', {}).get('next')
        else:
            print(f"Error fetching stations for state {state}: {response.status_code} - {response.text}")
            break
        
    # Filter by timezone after collecting all stations
    return stations

def get_station(station_id):
    """
    Fetches detailed information about a specific weather station.
    """
    station_url = f"{WEATHER_GOV_STATIONS_API}/{station_id}"
    response = requests.get(station_url, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching station {station_id}: {response.status_code} - {response.text}")
        return None

def get_observations(station_id):
    """
    Fetches observations for a specific weather station.
    Returns: {
        '@id': 'https://api.weather.gov/stations/0258W/observations/2025-06-18T13:10:00+00:00', 
        '@type': 'wx:ObservationStation', 
        'geometry': 'POINT(-71.17 42.33)', 
        'elevation': {'unitCode': 'wmoUnit:m', 'value': 68}, 
        'station': 'https://api.weather.gov/stations/0258W', 
        'stationId': '0258W', 
        'stationName': 'Boston College', 
        'timestamp': '2025-06-18T13:10:00+00:00', 
        'rawMessage': '', 
        'textDescription': '', 
        'icon': None, 
        'presentWeather': [], 
        'temperature': {'unitCode': 'wmoUnit:degC', 'value': 19.67, 'qualityControl': 'V'}, 
        'dewpoint': {'unitCode': 'wmoUnit:degC', 'value': None, 'qualityControl': 'Z'}, 
        'windDirection': {'unitCode': 'wmoUnit:degree_(angle)', 'value': 194, 'qualityControl': 'V'}, 
        'windSpeed': {'unitCode': 'wmoUnit:km_h-1', 'value': 8.028, 'qualityControl': 'V'}, 
        'windGust': {'unitCode': 'wmoUnit:km_h-1', 'value': None, 'qualityControl': 'Z'}, 
        'barometricPressure': {'unitCode': 'wmoUnit:Pa', 'value': None, 'qualityControl': 'Z'}, 
        'seaLevelPressure': {'unitCode': 'wmoUnit:Pa', 'value': None, 'qualityControl': 'Z'}, 
        'visibility': {'unitCode': 'wmoUnit:m', 'value': None, 'qualityControl': 'Z'}, 
        'maxTemperatureLast24Hours': {'unitCode': 'wmoUnit:degC', 'value': None}, 
        'minTemperatureLast24Hours': {'unitCode': 'wmoUnit:degC', 'value': None}, 
        'precipitationLast3Hours': {'unitCode': 'wmoUnit:mm', 'value': None, 'qualityControl': 'Z'},
        'relativeHumidity': {'unitCode': 'wmoUnit:percent', 'value': None, 'qualityControl': 'V'}, 
        'windChill': {'unitCode': 'wmoUnit:degC', 'value': None, 'qualityControl': 'V'}, 
        'heatIndex': {'unitCode': 'wmoUnit:degC', 'value': None, 'qualityControl': 'V'}, 
        'cloudLayers': []
    }
    """
    url = WEATHER_GOV_OBSERVATIONS_API.format(station_id=station_id)
    response = requests.get(url, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json().get('@graph', [])
    else:
        print(f"Error fetching observations for {station_id}: {response.status_code} - {response.text}")
        return []

def get_forecast(station_id, x=0, y=0):
    url = WEATHER_GOV_FORECAST_API.format(station_id=station_id, x=x, y=y)
    response = requests.get(url, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching forecast for {station_id}: {response.status_code} - {response.text}")
        return None
    

if __name__ == "__main__":
    stations = get_stations()
    # filtered_data = [{'id': station['stationIdentifier'], 'name': station['name']} for station in stations if not station['name'].startswith(station['stationIdentifier'])]
    # filtered_data = [{'id': station['stationIdentifier'], 'name': station['name']} for station in stations]
    # print(len([filtered_data]), [station['name'] for station in filtered_data])

    radar_stations = get_radar_stations()
    # print(len(radar_stations), radar_stations)

    # stations = get_stations()
    # simple_stations = [{'id': station['stationIdentifier'], 'name': station['name']} for station in stations]
    # print(len([stations]), [station['name'] for station in stations])

    # print('station data:', get_station(simple_stations[0]['id']))

    station_name = stations[0]['name']
    station_id = stations[0]['stationIdentifier']

    observations = get_observations(station_id)
    observations.pop() # remove last data point because the timestamp is very different from the rest
    temp_wind_data = pd.DataFrame([{
        'temperature': observation['temperature'].get('value'),
        'windSpeed': observation['windSpeed'].get('value'),
        'timestamp': pd.to_datetime(observation['timestamp']
    )} for observation in observations])

    temp_wind_data = temp_wind_data.set_index('timestamp')
    resampled_data = temp_wind_data.resample('10T').mean().interpolate(method='linear')


    print('observations for station {station_name}:\n', temp_wind_data)

    plt.plot(resampled_data.index, resampled_data['temperature'], label='Temperature (°C)')
    plt.plot(resampled_data.index, resampled_data['windSpeed'], label='Wind Speed (km/h)')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.legend()
    plt.tight_layout()
    plt.show()
    