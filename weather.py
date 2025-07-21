import requests
import pandas as pd
from shapely import wkt
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
from config import WEATHER_GOV_API, WEATHER_GOV_HEADERS, WEATHER_GOV_STATIONS_API, WEATHER_GOV_ZONES_API, WEATHER_GOV_FORECAST_API, WEATHER_GOV_FORECAST_HOURLY_API, WEATHER_GOV_RADAR_STATIONS_API, WEATHER_GOV_OBSERVATIONS_API


client_timezone = 'America/New_York'

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

def get_zones():
    """
    Fetches zones from the National Weather Service API.
    Returns a list of zones with their details.
    """
    response = requests.get(WEATHER_GOV_ZONES_API, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json().get('@graph', [])
    else:
        print(f"Error fetching zones: {response.status_code} - {response.text}")
        return []

def get_stations(state='MA'):
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

def get_observations(station_id):
    url = WEATHER_GOV_OBSERVATIONS_API.format(station_id=station_id)
    response = requests.get(url, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json().get('@graph', [])
    else:
        print(f"Error fetching observations for {station_id}: {response.status_code} - {response.text}")
        return []
    
def fetch(url):
    response = requests.get(url, headers=WEATHER_GOV_HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from {url}: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print('Fetching observation stations...')
    stations = get_stations()
    if not stations:
        print('No stations found.')
        exit()

    print(f'Found {len(stations)} stations.')

    # 260
    selected_station_index = 260

    station_name = stations[selected_station_index]['name']
    station_county_url = stations[selected_station_index]['county']
    station_id = stations[selected_station_index]['stationIdentifier']

    zone = fetch(station_county_url)
    # print(zone)
    print(f"zone info: ({zone['type']}) name: {zone['name']}, {zone['state']} - wfo: {zone['gridIdentifier']}")

    zone_wfo = zone['gridIdentifier']
    zone_geometry = wkt.loads(zone['geometry'])
    x, y = zone_geometry.exterior.xy
    
    # Create a GeoDataFrame from your polygon
    gdf = gpd.GeoDataFrame({'geometry': [zone_geometry]}, crs='EPSG:4326')  # WGS84

    # Convert to Web Mercator for contextily
    gdf = gdf.to_crs(epsg=3857)

    # Plot
    ax = gdf.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')
    print(ctx.providers)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Polygon on World Map')
    plt.show()

    exit(1)

    # print('forecast URL:', WEATHER_GOV_FORECAST_API.format(wfo=zone_wfo, x=zone_x, y=zone_y))

    print(f'\nFetching observations for station "{station_name}" ({station_id})...')

    observations = get_observations(station_id)
    observations.pop() # remove last data point because the timestamp is very different from the rest
    temp_wind_data = pd.DataFrame([{
        'temperature': observation['temperature'].get('value'),
        'windSpeed': observation['windSpeed'].get('value'),
        'timestamp': pd.to_datetime(observation['timestamp'], utc=True).tz_convert(client_timezone
    )} for observation in observations])

    print(f'observations for station {station_name}:\n', temp_wind_data)

    temp_wind_data = temp_wind_data.set_index('timestamp')
    resampled_data = temp_wind_data.resample('10min').mean().interpolate(method='linear')

    # print(f'observations for station {station_name}:\n', temp_wind_data)

    plt.plot(resampled_data.index, resampled_data['temperature'], label='Temperature (°C)')
    plt.plot(resampled_data.index, resampled_data['windSpeed'], label='Wind Speed (km/h)')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.tight_layout()
    plt.show()
    