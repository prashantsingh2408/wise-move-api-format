'''
Cost of Living API
Parameters:
    City
    Cost of Living Index
    Rent Index
    Cost of Living Plus Rent Index
    Groceries Index
    Restaurant Price Index
    Local Purchasing Power Index
'''

import json
from typing import List, Optional, Dict
from pathlib import Path

def load_data() -> List[Dict]:
    """Load city data from JSON file"""
    data_file = Path(__file__).parent / "data" / "cost_of_living.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_city_data(city: str) -> Optional[Dict]:
    """Get cost of living data for a specific city"""
    data = load_data()
    for city_data in data:
        if city_data["City"].lower() == city.lower():
            return {
                "city": city_data["City"],
                "cost_of_living_index": city_data["Cost of Living Index"],
                "rent_index": city_data["Rent Index"],
                "cost_of_living_plus_rent_index": city_data["Cost of Living Plus Rent Index"],
                "groceries_index": city_data["Groceries Index"],
                "restaurant_price_index": city_data["Restaurant Price Index"],
                "local_purchasing_power_index": city_data["Local Purchasing Power Index"]
            }
    return None

def get_most_expensive_cities(limit: int = 10) -> List[Dict]:
    """Get the most expensive cities by cost of living index"""
    data = load_data()
    sorted_cities = sorted(data, key=lambda x: float(x["Cost of Living Index"]), reverse=True)
    return format_city_data(sorted_cities[:limit])

def get_cheapest_cities(limit: int = 10) -> List[Dict]:
    """Get the cheapest cities by cost of living index"""
    data = load_data()
    sorted_cities = sorted(data, key=lambda x: float(x["Cost of Living Index"]))
    return format_city_data(sorted_cities[:limit])

def get_best_value_cities(limit: int = 10) -> List[Dict]:
    """
    Get cities with best value (highest local purchasing power relative to cost)
    Calculated as (Local Purchasing Power Index / Cost of Living Index)
    """
    data = load_data()
    
    # Calculate value score for each city
    for city in data:
        try:
            city["value_score"] = float(city["Local Purchasing Power Index"]) / float(city["Cost of Living Index"])
        except ZeroDivisionError:
            city["value_score"] = 0
    
    sorted_cities = sorted(data, key=lambda x: x["value_score"], reverse=True)
    return format_city_data(sorted_cities[:limit])

def format_city_data(cities: List[Dict]) -> List[Dict]:
    """Format city data for consistent API response"""
    return [
        {
            "city": city["City"],
            "cost_of_living_index": city["Cost of Living Index"],
            "rent_index": city["Rent Index"],
            "cost_of_living_plus_rent_index": city["Cost of Living Plus Rent Index"],
            "groceries_index": city["Groceries Index"],
            "restaurant_price_index": city["Restaurant Price Index"],
            "local_purchasing_power_index": city["Local Purchasing Power Index"]
        }
        for city in cities
    ]

def populate():
    """Placeholder for any data population logic if needed"""
    pass