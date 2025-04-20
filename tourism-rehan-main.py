from logging import exception
import function
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import os
import uuid
from enum import Enum
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Local Explorer API",
    description="API for providing cost estimation, safety assessment, and trip planning for travelers",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load sample data
if not os.path.exists("data"):
    os.makedirs("data")

# Sample data structures
sample_cities = {
    "delhi": {
        "name": "Delhi",
        "country": "India",
        "currency": "INR",
        "transportation": {
            "auto_rickshaw": {
                "base_fare": 25,
                "per_km": 8,
                "typical_short_trip": "40-60 INR",
                "typical_medium_trip": "80-120 INR"
            },
            "taxi": {
                "base_fare": 50,
                "per_km": 14, 
                "typical_short_trip": "100-150 INR",
                "typical_medium_trip": "200-300 INR"
            },
            "metro": {
                "base_fare": 10,
                "typical_trip": "20-40 INR"
            }
        },
        "food": {
            "street_food": "30-100 INR",
            "budget_restaurant": "150-300 INR per person",
            "mid_range_restaurant": "500-1000 INR per person",
            "luxury_restaurant": "1500+ INR per person"
        },
        "accommodation": {
            "hostel": "300-800 INR per night",
            "budget_hotel": "800-2000 INR per night",
            "mid_range_hotel": "2000-5000 INR per night",
            "luxury_hotel": "5000+ INR per night"
        },
        "neighborhoods": {
            "connaught_place": {
                "name": "Connaught Place",
                "safety_rating": 4.2,
                "safety_notes": "Central business district, generally safe during day, moderate caution at night",
                "tourist_friendly": 5,
                "attractions": ["Jantar Mantar", "Palika Bazaar", "Central Park"]
            },
            "chandni_chowk": {
                "name": "Chandni Chowk",
                "safety_rating": 3.5,
                "safety_notes": "Crowded historic area, watch for pickpockets, avoid isolated areas at night",
                "tourist_friendly": 4,
                "attractions": ["Red Fort", "Jama Masjid", "Spice Market"]
            },
            "hauz_khas": {
                "name": "Hauz Khas",
                "safety_rating": 4.5,
                "safety_notes": "Upscale area, generally safe, popular nightlife district",
                "tourist_friendly": 4.8,
                "attractions": ["Hauz Khas Fort", "Deer Park", "Trendy Cafes and Boutiques"]
            }
        },
        "attractions": {
            "red_fort": {
                "name": "Red Fort",
                "entry_fee": "45 INR (Indians), 600 INR (Foreigners)",
                "best_time": "Morning",
                "avg_time_spent": "2-3 hours"
            },
            "qutub_minar": {
                "name": "Qutub Minar",
                "entry_fee": "35 INR (Indians), 550 INR (Foreigners)",
                "best_time": "Late afternoon",
                "avg_time_spent": "1-2 hours"
            },
            "india_gate": {
                "name": "India Gate",
                "entry_fee": "Free",
                "best_time": "Evening",
                "avg_time_spent": "1 hour"
            }
        }
    },
    "mumbai": {
        "name": "Mumbai",
        "country": "India",
        "currency": "INR",
        "transportation": {
            "auto_rickshaw": {
                "base_fare": 18,
                "per_km": 12,
                "typical_short_trip": "50-80 INR",
                "typical_medium_trip": "100-150 INR"
            },
            "taxi": {
                "base_fare": 25,
                "per_km": 16,
                "typical_short_trip": "80-120 INR",
                "typical_medium_trip": "150-250 INR"
            },
            "local_train": {
                "base_fare": 5,
                "typical_trip": "10-30 INR"
            }
        },
        "food": {
            "street_food": "40-120 INR",
            "budget_restaurant": "200-400 INR per person",
            "mid_range_restaurant": "600-1200 INR per person",
            "luxury_restaurant": "2000+ INR per person"
        },
        "accommodation": {
            "hostel": "400-1000 INR per night",
            "budget_hotel": "1000-3000 INR per night",
            "mid_range_hotel": "3000-7000 INR per night",
            "luxury_hotel": "7000+ INR per night"
        },
        "neighborhoods": {
            "colaba": {
                "name": "Colaba",
                "safety_rating": 4.5,
                "safety_notes": "Tourist-friendly area, generally safe but be cautious in crowded places",
                "tourist_friendly": 5,
                "attractions": ["Gateway of India", "Colaba Causeway", "Taj Mahal Palace Hotel"]
            },
            "bandra": {
                "name": "Bandra",
                "safety_rating": 4.7,
                "safety_notes": "Upscale residential area, very safe, popular with expats",
                "tourist_friendly": 4.5,
                "attractions": ["Bandstand Promenade", "Mount Mary Church", "Bandra-Worli Sea Link"]
            }
        },
        "attractions": {
            "gateway_of_india": {
                "name": "Gateway of India",
                "entry_fee": "Free",
                "best_time": "Early morning or evening",
                "avg_time_spent": "1 hour"
            },
            "elephanta_caves": {
                "name": "Elephanta Caves",
                "entry_fee": "40 INR (Indians), 600 INR (Foreigners)",
                "ferry_cost": "130-150 INR return trip",
                "best_time": "Morning",
                "avg_time_spent": "3-4 hours including ferry ride"
            }
        }
    }
}

# Load data
def load_cities():
    with open("data/cities.json", "r") as f:
        return json.load(f)

def load_trips():
    with open("data/trips.json", "r") as f:
        return json.load(f)

def load_safety_reports():
    with open(r"data\safety_trips.json", "r") as f:
        return json.load(f)

def load_safety_trips():
    with open(r"data\safety_reports.json", "r") as f:
        return json.load(f)

def save_trips(trips):
    with open(r"data\trips.json", "w") as f:
        json.dump(trips, f, indent=4)

def save_safety_reports(reports):
    with open(r"data\safety_reports.json", "w") as f:
        json.dump(reports, f, indent=4)

def save_safety_trips(safety_trips):
    with open(r"data/safety_trips.json", "w") as f:
        json.dump(safety_trips, f, indent=4)


def save_json(data: Any, filename: str) -> None:
    path = os.path.join("data", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)        

# Models
# class SafetyReport(BaseModel):
#     location: str
#     neighborhood: str
#     incident_type: str
#     description: str
#     date: str
#     time: str
#     severity: int = Field(..., ge=1, le=5)

class TripDay(BaseModel):
    day_number: int
    activities: List[Dict[str, Any]]
    accommodation: Dict[str, Any]
    transportation: List[Dict[str, Any]]
    estimated_cost: float

class Trip(BaseModel):
    trip_id: Optional[str] = None
    user: str
    city: str
    duration_days: int
    trip_notes: str
    travel_mode: str
    places_visited: List[TripDay]
    total_cost_estimate_inr: float
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())  
    

# class SafetyRating(BaseModel):
#     overall: float
#     day: float
#     night: float
#     for_women: float
#     for_solo_travelers: float
#     for_families: float
#     notes: str

# class SafetyMetrics(BaseModel):
#     overall_safety: float
#     women_safety: float
#     transportation_safety: float
#     night_safety: float

# class SafetyTrip(BaseModel):
#     trip_id: Optional[str] = None
#     user: str
#     city_name: str
#     state: str
#     population: int
#     duration_days: int
#     places_visited: List[str]
#     trip_notes: str
#     travel_mode: str
#     total_cost_estimate_inr: float
#     safety_metrics: SafetyMetrics
#     safe_areas: List[str]
#     areas_to_avoid: List[str]
#     emergency_contacts: Dict[str, str]
#     transportation_tips: List[str]

# API Routes
@app.get("/")#✔
def read_root():
    return {"message": "Welcome to Local Explorer API"}

# Cost Estimation Endpoints
@app.get("/costs/{city}") #✔
def get_city_costs(city: str = Path(..., description="City name (lowercase)")):
    try:
        cities = load_cities()
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        return cities[city.lower()]
    except exception as e:
        print(f"Error loading cities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/costs/{city}/transportation") #✔
def get_transportation_costs(city: str = Path(..., description="City name (lowercase)")):
    try: 
        cities = load_cities()
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        return cities[city.lower()]["transportation"]
    except exception as e:
        print(f"Error loading cities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@app.get("/costs/{city}/food") #✔
def get_food_costs(city: str = Path(..., description="City name (lowercase)")):
    try:
        cities = load_cities()
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        return cities[city.lower()]["food"]
    except exception as e:
            print(f"Error loading cities: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
@app.get("/costs/{city}/accommodation") #✔
def get_accommodation_costs(city: str = Path(..., description="City name (lowercase)")):
    try:
        cities = load_cities()
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        return cities[city.lower()]["accommodation"]
    except exception as e:
        print(f"Error loading cities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/attractions/{city}") #✔
def get_city_attractions(city: str = Path(..., description="City name (lowercase)")):
    try:
        cities = load_cities()
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        return cities[city.lower()]["attractions"]
    except exception as e:
        print(f"Error loading cities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Trip cost estimation endpoint
@app.get("/estimate-trip-cost/{city}")
def estimate_trip_cost(
    city: str = Path(..., description="City name (lowercase)"),
    days: int = Query(..., description="Number of days for the trip"),
    travelers: int = Query(..., description="Number of travelers"),
    accommodation_type: str = Query(..., description="Type of accommodation (hostel, budget_hotel, mid_range_hotel, luxury_hotel)"),
    food_preferences: str = Query(..., description="Food preferences (street_food, budget_restaurant, mid_range_restaurant, luxury_restaurant)")
):
    try:
        cities = load_cities()
        
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        city_data = cities[city.lower()]
        
        # Extract cost ranges and convert to average values
        def extract_cost(cost_range):
            if isinstance(cost_range, str) and "-" in cost_range:
                parts = cost_range.split()
                for part in parts:
                    if "-" in part:
                        lower, upper = part.split("-")
                        # Strip any non-numeric characters
                        lower = ''.join(filter(str.isdigit, lower))
                        upper = ''.join(filter(str.isdigit, upper))
                        if lower and upper:
                            return (float(lower) + float(upper)) / 2
            return 0
        
        # Calculate accommodation costs
        accommodation_cost = 0
        if accommodation_type in city_data["accommodation"]:
            accommodation_cost = extract_cost(city_data["accommodation"][accommodation_type]) * days * (travelers / 2 + 0.5)  # Assuming some rooms are shared
        
        # Calculate food costs
        food_cost = 0
        if food_preferences in city_data["food"]:
            food_cost = extract_cost(city_data["food"][food_preferences]) * days * travelers * 3  # Assuming 3 meals per day
        
        # Estimate transportation costs (very rough estimate)
        transportation_cost = 0
        if "taxi" in city_data["transportation"]:
            # Assuming 2 medium taxi trips per day
            transportation_cost = extract_cost(city_data["transportation"]["taxi"]["typical_medium_trip"]) * days * 2
        
        # Estimate attraction costs (very rough estimate)
        attraction_cost = 500 * days * travelers  # Just a placeholder
        
        # Total estimated cost
        total_cost = accommodation_cost + food_cost + transportation_cost + attraction_cost
        
        return {
            "city": city_data["name"],
            "days": days,
            "travelers": travelers,
            "accommodation_type": accommodation_type,
            "food_preferences": food_preferences,
            "estimated_costs": {
                "accommodation": round(accommodation_cost, 2),
                "food": round(food_cost, 2),
                "transportation": round(transportation_cost, 2),
                "attractions": round(attraction_cost, 2),
                "total": round(total_cost, 2)
            },
            "currency": city_data["currency"]
        }
    except exception as e:
        print(f"Error estimating trip cost: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# Trip suggestions endpoint
@app.get("/trip-suggestions/{city}")
def get_trip_suggestions(
    city: str = Path(..., description="City name (lowercase)"),
    days: int = Query(..., description="Number of days for the trip")
):
    try:
        cities = load_cities()
        
        if city.lower() not in cities:
            raise HTTPException(status_code=404, detail="City not found")
        
        city_data = cities[city.lower()]
        
        # Create a simple itinerary based on available attractions
        itinerary = []
        attractions = list(city_data["attractions"].values())
        neighborhoods = list(city_data["neighborhoods"].values())
        
        for day in range(1, min(days + 1, 8)):  # Cap at 7 days for simplicity
            day_plan = {
                "day": day,
                "morning": attractions[day % len(attractions)]["name"] if attractions else "Explore local area",
                "afternoon": attractions[(day + 1) % len(attractions)]["name"] if attractions else "Local cuisine exploration",
                "evening": f"Explore {neighborhoods[day % len(neighborhoods)]['name']}" if neighborhoods else "Dinner and relaxation",
                "suggested_areas": [neighborhoods[day % len(neighborhoods)]["name"]] if neighborhoods else ["City center"]
            }
            itinerary.append(day_plan)
        
        return {
            "city": city_data["name"],
            "days": days,
            "itinerary": itinerary,
            "safety_tips": [
                "Keep your belongings secure, especially in crowded areas",
                "Use registered transportation services",
                "Keep digital copies of important documents",
                "Learn basic local phrases",
                "Research local customs and dress appropriately"
            ]

        }
    except exception as e:  
    
            print(f"Error getting trip suggestions: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

