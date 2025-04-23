from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional, List
from pydantic import BaseModel
import population
import cost_of_living

# Define response models for better documentation
class CityPopulation(BaseModel):
    city: str
    population: str
    population_proper: str
    admin_name: str

class CityCostOfLiving(BaseModel):
    city: str
    cost_of_living_index: float
    rent_index: float
    cost_of_living_plus_rent_index: float
    groceries_index: float
    restaurant_price_index: float
    local_purchasing_power_index: float

class Message(BaseModel):
    message: str

class PopulateResponse(BaseModel):
    status: str
    message: str

app = FastAPI(
    title="Population and Cost of Living API",
    description="""
    An API providing population data for cities in India and cost of living data worldwide.
    Data sources: 
    - Population: https://simplemaps.com/data/in-cities
    - Cost of Living: Your cost of living dataset
    """,
    version="1.0.0",
    contact={
        "name": "Population and Cost of Living API Team",
    }
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

@app.get("/", response_model=Message, tags=["General"])
async def root():
    """
    Welcome endpoint for the API.
    
    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to the Population and Cost of Living API"}

# Population endpoints
@app.post("/population/populate", response_model=PopulateResponse, tags=["Population"])
async def populate_population():
    """
    Populate the database with population data.
    
    Returns:
        PopulateResponse: Status and message of the operation
        
    Raises:
        HTTPException: 500 for server errors
    """
    try:
        population.populate()
        return {"status": "success", "message": "Population completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/city/{city_name}", response_model=CityPopulation, tags=["Population"])
async def get_city_population(city_name: str):
    """
    Get population data for a specific city.
    
    Parameters:
        city_name (str): Name of the city to look up
        
    Returns:
        CityPopulation: Population details for the specified city
        
    Raises:
        HTTPException: 404 if city not found, 500 for server errors
    """
    try:
        result = population.get_city_population(city_name)
        if result is None:
            raise HTTPException(status_code=404, detail="City not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/country/{country_name}/cities", response_model=List[CityPopulation], tags=["Population"])
async def get_cities_in_country(country_name: str):
    """
    Get all cities and their population data for a country.
    
    Parameters:
        country_name (str): Name of the country (currently only supports 'India')
        
    Returns:
        List[CityPopulation]: List of cities and their population details
        
    Raises:
        HTTPException: 404 if no cities found, 500 for server errors
    """
    try:
        cities = population.get_cities_by_country(country_name)
        if not cities:
            raise HTTPException(status_code=404, detail="No cities found for this country")
        return cities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/largest-cities", response_model=List[CityPopulation], tags=["Population"])
async def get_largest_cities(limit: Optional[int] = 10):
    """
    Get the largest cities by population.
    
    Parameters:
        limit (int, optional): Number of cities to return. Defaults to 10.
        
    Returns:
        List[CityPopulation]: List of cities sorted by population in descending order
        
    Raises:
        HTTPException: 500 for server errors
    """
    try:
        return population.get_largest_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cost of Living endpoints
@app.post("/cost/populate", response_model=PopulateResponse, tags=["Cost of Living"])
async def populate_cost():
    """Populate the database with cost of living data."""
    try:
        cost_of_living.populate()
        return {"status": "success", "message": "Data populated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/city/{city_name}", response_model=CityCostOfLiving, tags=["Cost of Living"])
async def get_city_cost(city_name: str):
    """
    Get cost of living data for a specific city.
    
    Parameters:
        city_name (str): Name of the city to look up (e.g., 'Hamilton, Bermuda')
        
    Returns:
        CityCostOfLiving: Cost of living details for the specified city
    """
    try:
        result = cost_of_living.get_city_data(city_name)
        if result is None:
            raise HTTPException(status_code=404, detail="City not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/most-expensive-cities", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_most_expensive_cities(limit: Optional[int] = 10):
    """
    Get the most expensive cities by cost of living index.
    
    Parameters:
        limit (int, optional): Number of cities to return. Defaults to 10.
    """
    try:
        return cost_of_living.get_most_expensive_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/cheapest-cities", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_cheapest_cities(limit: Optional[int] = 10):
    """
    Get the cheapest cities by cost of living index.
    
    Parameters:
        limit (int, optional): Number of cities to return. Defaults to 10.
    """
    try:
        return cost_of_living.get_cheapest_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/best-value-cities", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_best_value_cities(limit: Optional[int] = 10):
    """
    Get cities with the best value (highest local purchasing power relative to cost).
    
    Parameters:
        limit (int, optional): Number of cities to return. Defaults to 10.
    """
    try:
        return cost_of_living.get_best_value_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint for Groq
@app.get("/test_groq_get", tags=["Testing"])
async def test_groq_get(query: str):
    """
    Test endpoint for Groq integration.
    
    Parameters:
        query (str): The query string to process
        
    Returns:
        dict: Status and response from Groq
        
    Raises:
        HTTPException: 500 for server errors
    """
    try:
        response = chat_context_api.test_groq_get(query)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))