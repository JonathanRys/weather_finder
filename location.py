import requests, json
from config import API_KEY, REGIONS_LIST_API, COUNTRIES_LIST_API, ADMIN_AREAS_LIST_API, CITIES_LIST_API, AUTOCOMPLETE_CITIES_LIST_API

def get_regions():
    params = {
        'apikey': API_KEY
    }
    response = requests.get(REGIONS_LIST_API, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
    
def get_countries(region_code):
    url = COUNTRIES_LIST_API.format(region_code=region_code)
    params = {
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {
            **response,
            "error": f"Failed to fetch countries for region {region_code}"
        }
    
def get_admin_areas(country_code):
    url = ADMIN_AREAS_LIST_API.format(country_code=country_code)
    params = {
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
    
def get_cities(country_code, admin_area_code, query=''):
    url = CITIES_LIST_API.format(country_code=country_code, admin_area_code=admin_area_code)
    params = {
        'apikey': API_KEY,
        'q': query  
    }
    print(f"Fetching cities from: {url}")
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def autocomplete_cities(query):
    params = {
        'apikey': API_KEY,
        'q': query
    }
    response = requests.get(AUTOCOMPLETE_CITIES_LIST_API, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    regions = get_regions()
    if not regions:
        print("Failed to fetch regions.")
        exit(1)
    print([name['EnglishName'] for name in regions])

    selected_region_name = 'North America'
    selected_region = next(filter(lambda x: x['EnglishName'] == selected_region_name, regions))

    countries = get_countries(selected_region['ID'])
    if not countries:
        print("Failed to fetch countries.")
        exit(1)
    print([country['EnglishName'] for country in countries])

    selected_country_name = 'United States'
    selected_country = next(filter(lambda x: x['EnglishName'] == selected_country_name, countries))

    admin_areas = get_admin_areas(selected_country['ID'])
    if not admin_areas:
        print("Failed to fetch admin areas.")
        exit(1)
    print([area['EnglishName'] for area in admin_areas])

    selected_admin_area_name = 'Massachusetts'
    selected_admin_area = next(filter(lambda x: x['EnglishName'] == selected_admin_area_name, admin_areas))

    selected_country_code = selected_country['ID']
    selected_admin_area_code = selected_admin_area['ID']

    print(f"Selected Country Code: {selected_country_code}, Admin Area Code: {selected_admin_area_code}")

    # cities = get_cities(selected_country_code, selected_admin_area_code, 'bos')
    cities = autocomplete_cities('bos')
    print([city['EnglishName'] for city in cities] if cities else "No cities found")
    