from logging import exception
import trip_func
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
    




#post route for trip planning

# Add these models to the existing models section

class SafetyReportCreate(BaseModel):
    city: str
    neighborhood: str
    safety_rating: int = Field(..., ge=1, le=5, description="Safety rating from 1-5")
    incident_type: Optional[str] = None
    description: str
    reported_by: str
    occurred_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SafetyReport(SafetyReportCreate):
    report_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SafetyTripCreate(BaseModel):
    trip_id: str
    city: str
    neighborhoods: List[str]
    duration_days: int
    travel_mode: str
    traveler_count: int

class SafetyTripResponse(BaseModel):
    trip_id: str
    city: str
    neighborhoods: List[str]
    overall_safety_rating: float
    neighborhood_ratings: Dict[str, float]
    safety_tips: List[str]
    created_at: str


@app.post("/trips/", response_model=Trip)
def create_trip(trip: Trip):
    try:
        trips = load_trips()
        
        
        if not trip.trip_id:
            trip.trip_id = str(uuid.uuid4())
            
        
        trip.created_at = datetime.utcnow().isoformat()
        
        
        trips.append(trip.dict())
        save_trips(trips)
        
        return trip
    except Exception as e:
        print(f"Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/safety/reports/", response_model=SafetyReport)
def create_safety_report(report: SafetyReportCreate):
    try:
        reports = load_safety_reports()
        
        
        new_report = SafetyReport(
            report_id=str(uuid.uuid4()),
            **report.dict()
        )
        
       
        reports.append(new_report.dict())
        save_safety_reports(reports)
        
        return new_report
    except Exception as e:
        print(f"Error creating safety report: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/safety/trips/", response_model=SafetyTripResponse)
def assess_trip_safety(trip_data: SafetyTripCreate):
    try:
        safety_reports = load_safety_reports()
        safety_trips = load_safety_trips()
        
        
        city_reports = [r for r in safety_reports if r["city"].lower() == trip_data.city.lower()]
        
        
        neighborhood_ratings = {}
        for neighborhood in trip_data.neighborhoods:
            neighborhood_reports = [r for r in city_reports if r["neighborhood"].lower() == neighborhood.lower()]
            if neighborhood_reports:
                avg_rating = sum(r["safety_rating"] for r in neighborhood_reports) / len(neighborhood_reports)
                neighborhood_ratings[neighborhood] = round(avg_rating, 1)
            else:
                
                neighborhood_ratings[neighborhood] = 3.0
        
        
        overall_rating = sum(neighborhood_ratings.values()) / len(neighborhood_ratings) if neighborhood_ratings else 3.0
        
       
        safety_tips = trip_func.generate_safety_tips(overall_rating, trip_data.city, trip_data.travel_mode)
        
       
        response = SafetyTripResponse(
            trip_id=trip_data.trip_id,
            city=trip_data.city,
            neighborhoods=trip_data.neighborhoods,
            overall_safety_rating=round(overall_rating, 1),
            neighborhood_ratings=neighborhood_ratings,
            safety_tips=safety_tips,
            created_at=datetime.utcnow().isoformat()
        )
        
       
        safety_trips.append(response.dict())
        save_safety_trips(safety_trips)
        
        return response
    except Exception as e:
        print(f"Error assessing trip safety: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/trips/{trip_id}/plan", response_model=Trip)
def generate_trip_plan(
    trip_id: str = Path(..., description="Trip ID to plan"),
    budget: float = Query(None, description="Budget in INR"),
    preferences: List[str] = Query(None, description="Activity preferences")
):
    try:
        trips = load_trips()
        cities = load_cities()
        
        # Find the trip
        trip = next((t for t in trips if t["trip_id"] == trip_id), None)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
            
       
        city = trip["city"].lower()
        if city not in cities:
            raise HTTPException(status_code=404, detail="City not found")
            
        city_data = cities[city]
        
       
        planned_trip = trip_func.generate_trip_plan(
            trip=trip,
            city_data=city_data,
            budget=budget,
            preferences=preferences or []
        )
        
        # Update the trip
        for i, t in enumerate(trips):
            if t["trip_id"] == trip_id:
                trips[i] = planned_trip
                break
                
        save_trips(trips)
        
        return Trip(**planned_trip)
    except Exception as e:
        print(f"Error generating trip plan: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.put("/trips/{trip_id}", response_model=Trip)
def update_trip(trip_id: str, updated_trip: Trip):
    try:
        trips = load_trips()
        
      
        trip_index = next((i for i, t in enumerate(trips) if t["trip_id"] == trip_id), None)
        if trip_index is None:
            raise HTTPException(status_code=404, detail="Trip not found")
            
        
        updated_trip.trip_id = trip_id
        
       
        trips[trip_index] = updated_trip.dict()
        save_trips(trips)
        
        return updated_trip
    except Exception as e:
        print(f"Error updating trip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")





# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

