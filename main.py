# from dotenv import load_dotenv
# load_dotenv()

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import os
# from typing import Optional, List
# from pydantic import BaseModel
# import population

# # Define response models for better documentation
# class CityPopulation(BaseModel):
#     city: str
#     population: str
#     population_proper: str
#     admin_name: str

# class Message(BaseModel):
#     message: str

# class PopulateResponse(BaseModel):
#     status: str
#     message: str

# app = FastAPI(
#     title="India Population API",
#     description="""
#     An API providing population data for cities in India.
#     Data source: https://simplemaps.com/data/in-cities
#     """,
#     version="1.0.0",
#     contact={
#         "name": "Population API Team",
#     }
# )

# # Add CORS middleware to allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
# )

# @app.get("/", response_model=Message, tags=["General"])
# async def root():
#     """
#     Welcome endpoint for the Population API.
    
#     Returns:
#         dict: A welcome message
#     """
#     return {"message": "Welcome to the Population API"}

# @app.post("/populate", response_model=PopulateResponse, tags=["Population"])
# async def populate():
#     """
#     Populate the database with population data.
    
#     Returns:
#         PopulateResponse: Status and message of the operation
        
#     Raises:
#         HTTPException: 500 for server errors
#     """
#     try:
#         population.populate()
#         return {"status": "success", "message": "Population completed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/city/{city_name}", response_model=CityPopulation, tags=["Cities"])
# async def get_city_population(city_name: str):
#     """
#     Get population data for a specific city.
    
#     Parameters:
#         city_name (str): Name of the city to look up
        
#     Returns:
#         CityPopulation: Population details for the specified city
        
#     Raises:
#         HTTPException: 404 if city not found, 500 for server errors
#     """
#     try:
#         result = population.get_city_population(city_name)
#         if result is None:
#             raise HTTPException(status_code=404, detail="City not found")
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/country/{country_name}/cities", response_model=List[CityPopulation], tags=["Cities"])
# async def get_cities_in_country(country_name: str):
#     """
#     Get all cities and their population data for a country.
    
#     Parameters:
#         country_name (str): Name of the country (currently only supports 'India')
        
#     Returns:
#         List[CityPopulation]: List of cities and their population details
        
#     Raises:
#         HTTPException: 404 if no cities found, 500 for server errors
#     """
#     try:
#         cities = population.get_cities_by_country(country_name)
#         if not cities:
#             raise HTTPException(status_code=404, detail="No cities found for this country")
#         return cities
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/largest-cities", response_model=List[CityPopulation], tags=["Cities"])
# async def get_largest_cities(limit: Optional[int] = 10):
#     """
#     Get the largest cities by population.
    
#     Parameters:
#         limit (int, optional): Number of cities to return. Defaults to 10.
        
#     Returns:
#         List[CityPopulation]: List of cities sorted by population in descending order
        
#     Raises:
#         HTTPException: 500 for server errors
#     """
#     try:
#         return population.get_largest_cities(limit)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Test endpoint for Groq
# @app.get("/test_groq_get", tags=["Testing"])
# async def test_groq_get(query: str):
#     """
#     Test endpoint for Groq integration.
    
#     Parameters:
#         query (str): The query string to process
        
#     Returns:
#         dict: Status and response from Groq
        
#     Raises:
#         HTTPException: 500 for server errors
#     """
#     try:
#         response = chat_context_api.test_groq_get(query)
#         return {
#             "status": "success",
#             "response": response
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from pydantic import BaseModel
import population
import cost_of_living

app = FastAPI(
    title="Global Cities API",
    description="""
    Combined API providing both population and cost of living data for cities worldwide.
    
    Data Sources:
    - Population: https://simplemaps.com/data/in-cities
    - Cost of Living: Your cost of living dataset
    """,
    version="2.0.0",
    contact={
        "name": "Global Cities API Team",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# MODELS

class Message(BaseModel):
    message: str

class PopulateResponse(BaseModel):
    status: str
    message: str

# Population Models
class CityPopulation(BaseModel):
    city: str
    population: str
    population_proper: str
    admin_name: str

# Cost of Living Models
class CityCostOfLiving(BaseModel):
    city: str
    cost_of_living_index: float
    rent_index: float
    cost_of_living_plus_rent_index: float
    groceries_index: float
    restaurant_price_index: float
    local_purchasing_power_index: float

# Comparison Models
class CityComparisonResult(BaseModel):
    metric: str
    city1_value: float
    city2_value: float
    difference: float
    percentage_diff: float

class CitiesComparison(BaseModel):
    city1: CityCostOfLiving
    city2: CityCostOfLiving
    comparisons: List[CityComparisonResult]

# MIDDLEWARE

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GENERAL ENDPOINTS

@app.get("/", response_model=Message, tags=["General"])
async def root():
    """Welcome endpoint for the Global Cities API"""
    return {"message": "Welcome to the Global Cities API"}

# POPULATION ENDPOINTS

@app.post("/population/populate", response_model=PopulateResponse, tags=["Population"])
async def populate_population():
    """Populate the database with population data"""
    try:
        population.populate()
        return {"status": "success", "message": "Population data populated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/city/{city_name}", response_model=CityPopulation, tags=["Population"])
async def get_city_population(city_name: str):
    """Get population data for a specific city"""
    try:
        result = population.get_city_population(city_name)
        if result is None:
            raise HTTPException(status_code=404, detail="City not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/country/{country_name}", response_model=List[CityPopulation], tags=["Population"])
async def get_cities_by_country(country_name: str):
    """Get all cities and their population data for a country"""
    try:
        cities = population.get_cities_by_country(country_name)
        if not cities:
            raise HTTPException(status_code=404, detail="No cities found for this country")
        return cities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/population/largest-cities", response_model=List[CityPopulation], tags=["Population"])
async def get_largest_cities(limit: int = Query(10, ge=1, le=100)):
    """Get the largest cities by population"""
    try:
        return population.get_largest_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# COST OF LIVING ENDPOINTS

@app.post("/cost/populate", response_model=PopulateResponse, tags=["Cost of Living"])
async def populate_cost():
    """Populate the database with cost of living data"""
    try:
        cost_of_living.populate()
        return {"status": "success", "message": "Cost of living data populated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/city/{city_name}", response_model=CityCostOfLiving, tags=["Cost of Living"])
async def get_city_cost(city_name: str):
    """Get cost of living data for a specific city"""
    try:
        result = cost_of_living.get_city_data(city_name)
        if result is None:
            available = cost_of_living.list_available_cities()
            raise HTTPException(
                status_code=404, 
                detail=f"City not found. Available cities: {available}"
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/most-expensive", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_most_expensive_cities(limit: int = Query(10, ge=1, le=50)):
    """Get the most expensive cities by cost of living index"""
    try:
        return cost_of_living.get_most_expensive_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/cheapest", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_cheapest_cities(limit: int = Query(10, ge=1, le=50)):
    """Get the cheapest cities by cost of living index"""
    try:
        return cost_of_living.get_cheapest_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost/best-value", response_model=List[CityCostOfLiving], tags=["Cost of Living"])
async def get_best_value_cities(limit: int = Query(10, ge=1, le=50)):
    """Get cities with best value (purchasing power relative to cost)"""
    try:
        return cost_of_living.get_best_value_cities(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cost/compare", response_model=CitiesComparison, tags=["Cost of Living"])
async def compare_cities(cities: Dict[str, str] = Body(..., example={"city1": "New York, NY", "city2": "London, UK"})):
    """Compare cost of living between two cities"""
    try:
        city1 = cities.get("city1")
        city2 = cities.get("city2")
        
        if not city1 or not city2:
            raise HTTPException(status_code=400, detail="Both city1 and city2 are required")
            
        city1_data = cost_of_living.get_city_data(city1)
        city2_data = cost_of_living.get_city_data(city2)
        
        if not city1_data or not city2_data:
            available = cost_of_living.list_available_cities()
            raise HTTPException(
                status_code=404,
                detail=f"One or both cities not found. Available cities: {available}"
            )
        
        comparisons = []
        metrics = [
            ('cost_of_living_index', 'Cost of Living Index'),
            ('rent_index', 'Rent Index'),
            ('cost_of_living_plus_rent_index', 'Cost of Living Plus Rent Index'),
            ('groceries_index', 'Groceries Index'),
            ('restaurant_price_index', 'Restaurant Price Index'),
            ('local_purchasing_power_index', 'Local Purchasing Power Index')
        ]
        
        for field, display_name in metrics:
            val1 = city1_data.get(field, 0)
            val2 = city2_data.get(field, 0)
            diff = val1 - val2
            percentage = (diff / val2) * 100 if val2 != 0 else 0
            
            comparisons.append({
                "metric": display_name,
                "city1_value": round(val1, 2),
                "city2_value": round(val2, 2),
                "difference": round(diff, 2),
                "percentage_diff": round(percentage, 2)
            })
        
        return {
            "city1": city1_data,
            "city2": city2_data,
            "comparisons": comparisons
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# TESTING ENDPOINTS
# ========================

@app.get("/test/groq", tags=["Testing"])
async def test_groq_get(query: str):
    """Test endpoint for Groq integration"""
    try:
        response = chat_context_api.test_groq_get(query)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))