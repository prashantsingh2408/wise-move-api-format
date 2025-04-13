'''
Population API
Parameter 
    Country
    City
Source: https://simplemaps.com/data/in-cities
'''

import json
from typing import List, Optional
from pathlib import Path

def load_data() -> List[dict]:
    """Load city data from JSON file"""
    data_file = Path(__file__).parent / "data" / "in.json"
    with open(data_file, 'r') as f:
        return json.load(f)

def get_city_population(city: str) -> Optional[dict]:
    """Get population data for a specific city"""
    data = load_data()
    for city_data in data:
        if city_data["city"].lower() == city.lower():
            return {
                "city": city_data["city"],
                "population": city_data["population"],
                "population_proper": city_data["population_proper"],
                "admin_name": city_data["admin_name"]
            }
    return None

def get_cities_by_country(country: str) -> List[dict]:
    """Get all cities and their population for a country"""
    data = load_data()
    cities = [
        {
            "city": city["city"],
            "population": city["population"],
            "population_proper": city["population_proper"],
            "admin_name": city["admin_name"]
        }
        for city in data
        if city["country"].lower() == country.lower()
    ]
    return cities

def get_largest_cities(limit: int = 10) -> List[dict]:
    """Get the largest cities by population"""
    data = load_data()
    sorted_cities = sorted(data, key=lambda x: int(x["population"]), reverse=True)
    return [
        {
            "city": city["city"],
            "population": city["population"],
            "population_proper": city["population_proper"],
            "admin_name": city["admin_name"]
        }
        for city in sorted_cities[:limit]
    ]

