"""
FastAPI endpoints for restaurant booking system.
Handles restaurant search and reservation management.
"""

#Basic imports
import json
from typing import List, Optional, Dict, Any, Union
import uvicorn
import os

#Third party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Setting up Basic Logging
import logging

# Setup API logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('goodfoods.api')

#Global Variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DATA_DIR = os.path.join(BASE_DIR, "data")

#All Functions Available
# RestaurantQuery, Reservation - Pydantic models for API requests
# search_restaurant_information(query)
# review_information_before_order(order_info)
# check_capacity(restaurant_id, requested_party_size, reservation_date, reservation_time, debug)
# detect_placeholder_values(order_info)
# make_new_order(order_info, capacity_debug)
# api_search_restaurants(query)
# api_make_reservation(query)

try:
    with open(os.path.join(BASE_DIR, 'bookings_list.json'), 'r') as f:
        order_management_table: List[Dict[str, Any]] = json.load(f)
    logger.info("Successfully loaded bookings_list.json")
except FileNotFoundError:
    logger.error("Error: bookings_list.json not found")
    order_management_table = []

try:
    with open(os.path.join(BASE_DIR, 'restaurant_list.json'), 'r') as f:
        restaurant_information_table: List[Dict[str, Any]] = json.load(f)
    logger.info("Successfully loaded restaurant_list.json")
except FileNotFoundError:
    logger.error("Error: restaurant_list.json not found")
    restaurant_information_table = []

app = FastAPI()

class RestaurantQuery(BaseModel):
    """
    Pydantic model for restaurant search query parameters.
    All fields are optional to allow flexible searching.
    """

    location: Optional[str] = None
    cuisine: Optional[Union[str, List[str]]] = None
    operating_days: Optional[str] = None
    operating_hours: Optional[Dict[str, str]] = None
    restaurant_max_seating_capacity: Optional[int] = None
    max_booking_party_size: Optional[int] = None
    
class Reservation(BaseModel):
    """
    Pydantic model for restaurant reservation requests.
    All fields are required for making a reservation.
    """

    restaurant_id: str
    orderer_name: str
    orderer_contact: str
    party_size: int
    reservation_date: str
    reservation_time: str


def search_restaurant_information(query: Dict[str, Any]) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
   """
    Search for restaurants based on query parameters.

    Parameters:
        query (Dict[str, Any]): Search criteria including location, cuisine, operating hours, etc.

    Returns:
        Dict[str, Union[str, List[Dict[str, Any]]]]: Search results containing:
            - status: Search status ('empty query', 'no_matches', 'matches_found')
            - message: Human readable result description
            - restaurants: List of matching restaurants with match details
    """
   
   logger.info(f"Received search query: {query}")

   query = {k: v for k, v in query.items() if v}  
   logger.info(f"SEARCH QUERY after removing empty values: {query}")

   top_restaurant_info = restaurant_information_table[:10]
   
   if not query:
       logger.info("EMPTY QUERY: Returning top restaurants")
       return {
           "status": "empty query",
           "message": "Since the query was empty, here are some top most preferred options. Collect additional info from user to match.",
           "restaurants": top_restaurant_info
       }
       
   restaurant_matches = []
   logger.info(f"Starting restaurant matching process for {len(restaurant_information_table)} restaurants")
   for restaurant in restaurant_information_table:
       logger.info(f"\nTesting restaurant: {restaurant['name']}")
       match_count = 0
       matches = {}
       
       for key, value in query.items():
        logger.info(f"  Checking field: {key} = {value}")
        if key == "cuisine":
               
                if isinstance(value, str):
                   cuisine_match = any(value.lower() in cuisine.lower() for cuisine in restaurant.get("cuisine", []))
                else:
                   cuisine_match = any(c in restaurant.get("cuisine", []) for c in value)
                if cuisine_match:
                    logger.info(f"  Cuisine match: {cuisine_match}")
                    match_count += 1
                    matches[key] = True
               
        elif key == "location":
               loc_info = restaurant.get("location", {})
               location_query_str = str(value)
               
               
               location_matches = (
                   location_query_str.lower() in loc_info.get("address", "").lower() or
                   location_query_str.lower() in loc_info.get("landmark", "").lower()
               )
               if location_matches:
                logger.info(f"  Location match: {location_matches}")
                match_count += 1
                matches[key] = True
                   
        elif key == "operating_days":
               days = restaurant.get("operating_days", [])
               day_match = any(value.lower() in day.lower() for day in days)
               if day_match:
                logger.info(f"  Operating day match: {day_match}")
                match_count += 1
                matches[key] = True
                   
        elif key == "operating_hours":
               rest_hours = restaurant.get("operating_hours", {})
               hours_match = True
               if "open" in value and rest_hours.get("open") != value["open"]:
                   hours_match = False
               if "close" in value and rest_hours.get("close") != value["close"]:
                   hours_match = False
               if hours_match:
                logger.info(f"Operating hours match: {hours_match}")
                match_count += 1
                matches[key] = True
               
        elif key in ["restaurant_max_seating_capacity", "max_booking_party_size"]:
               try:
                value_int = int(str(value).strip())
                restaurant_capacity = restaurant.get(key, 0)
                capacity_match = restaurant_capacity >= value_int
                logger.info(f"Comparing capacity: restaurant {restaurant_capacity} >= requested {value_int}")
                if capacity_match:
                   logger.info(f"  Capacity match: {capacity_match}")
                   match_count += 1
                   matches[key] = True
               except (ValueError, TypeError) as e:
                logger.info(f"Error converting capacity value '{value}' to integer for {restaurant['name']}: {e}")
                continue   
        else:
               field_match = restaurant.get(key) == value
               logger.info(f"  Field match for {key}: {field_match}")
               if not field_match:
                   match = False
                   break
                   
       if match_count > 0:
            logger.info(f"Restaurant {restaurant['name']} matched {match_count} criteria: {matches}")
            restaurant_matches.append({
                "restaurant": restaurant,
                "match_count": match_count,
                "matched_fields": matches
            })
           
   restaurant_matches.sort(key=lambda x: x["match_count"], reverse=True)
   logger.info(f"Found {len(restaurant_matches)} matching restaurants")
   
   if not restaurant_matches:
       logger.info("NO MATCHES: Returning top 10 restaurants with status message")
       return {
           "status": "no_matches",
           "message": "No matching restaurants found. Here are some top most preferred options. Collect additional info from user to match.",
           "restaurants": top_restaurant_info
       }

   logger.info(f"Returning {len(restaurant_matches)} matched restaurants")    
   return {
    "status": "matches_found",
    "message": f"Found {len(restaurant_matches)} restaurants matching your criteria.",
    "restaurants": [
        {
            **match["restaurant"],  
            "matched_fields": match["matched_fields"],
            "match_count": match["match_count"]
        } for match in restaurant_matches
    ]
}


def review_information_before_order(order_info: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
   """
    Validates order information for completeness and valid values.

    Parameters:
        order_info (Dict[str, Any]): Order information containing customer and reservation details

    Returns:
        Dict[str, Union[str, List[str]]]: Validation result containing:
            - status: 'complete' or 'invalid'
            - missing_fields: List of required fields that are missing (if any)
            - placeholder_fields: List of fields containing placeholder values (if any)
    """

   required_fields = ["restaurant_id", "orderer_name", "orderer_contact", "party_size", "reservation_date", "reservation_time"]

   missing_fields = [field for field in required_fields if field not in order_info or not order_info[field]]

   placeholder_check = detect_placeholder_values(order_info)
   placeholder_fields = placeholder_check["placeholder_fields"]

   if missing_fields or placeholder_fields:
        return {
            "status": "invalid",
            "missing_fields": missing_fields,
            "placeholder_fields": placeholder_fields
        }
   
   return {"status": "complete"}


def check_capacity(restaurant_id: str, requested_party_size: int, reservation_date: str, reservation_time: str, debug: bool) -> Union[bool, Dict[str, Any]]:
    """
    Checks if restaurant can accommodate the requested party size at specified time.

    Parameters:
        restaurant_id (str): Unique identifier of the restaurant
        requested_party_size (int): Number of people in the party
        reservation_date (str): Date of reservation in YYYY-MM-DD format
        reservation_time (str): Time of reservation in HH:MM format
        debug (bool): If True, returns detailed capacity information

    Returns:
        Union[bool, Dict[str, Any]]: 
            - If debug=False: Boolean indicating if capacity is available
            - If debug=True: Dictionary with detailed capacity information
    """

    restaurant = next((r for r in restaurant_information_table if r["restaurant_id"] == restaurant_id), None)
    if not restaurant:
        return False
    
    max_capacity = restaurant["restaurant_max_seating_capacity"]
    
    current_total = sum(order["party_size"] for order in order_management_table 
                        if order["restaurant_id"] == restaurant_id and 
                        order["reservation_date"] == reservation_date and 
                        order["reservation_time"] == reservation_time)
    available_capacity = max_capacity - current_total
    is_within_capacity = (current_total + requested_party_size) <= max_capacity
    if debug:
        return {
            "is_within_capacity": is_within_capacity,
            "restaurant_id": restaurant_id,
            "max_capacity": max_capacity,
            "current_total": current_total,
            "requested_party_size": requested_party_size,
            "available_capacity": available_capacity
        }
    else:
        return is_within_capacity


def detect_placeholder_values(order_info: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
    """
    Detects common placeholder values in order information.

    Parameters:
        order_info (Dict[str, Any]): Order information to check for placeholders

    Returns:
        Dict[str, Union[bool, List[str]]]: Detection results containing:
            - has_placeholders: Boolean indicating if any placeholders were found
            - placeholder_fields: List of fields containing placeholder values
    """

    placeholder_values = {
        "orderer_name": [
            "user", "your name", "your full name", "name", "customer", "customer name",
            "customer's name", "the user", "the customer", "placeholder", "john doe", 
            "jane doe", "user name", "username", "[name]", "(name)", "customer_name", 
            "orderer", "person", "guest", "guest name", "your_name"
        ],
        "orderer_contact": [
            "contact", "your contact", "your phone", "your number", "your phone number",
            "your contact number", "phone", "phone number", "contact number", "mobile",
            "mobile number", "user contact", "user phone", "user number", "123456789",
            "1234567890", "9876543210", "user's contact", "user's phone", "customer contact",
            "customer phone", "customer number", "phone_number", "contact_number", 
            "your_phone_number", "your_contact"
        ]
    }
    
    has_placeholders = False
    placeholder_fields = []
    
    for field, placeholders in placeholder_values.items():
        if field in order_info:
            value = str(order_info[field]).lower().strip()
            if any(placeholder.lower() in value for placeholder in placeholders):
                has_placeholders = True
                placeholder_fields.append(field)
            
            elif field == "orderer_contact":
                # Require strictly numeric and exactly 10 digits
                if (not value.isdigit()) or (len(value) != 10):
                    has_placeholders = True
                    placeholder_fields.append(field)
    
    for field in ["reservation_date", "reservation_time"]:
        if field in order_info:
            value = str(order_info[field]).lower()
            if "tomorrow" in value or "tonight" in value or "today" in value or "next" in value:
                has_placeholders = True
                placeholder_fields.append(field)
    
    return {
        "has_placeholders": has_placeholders,
        "placeholder_fields": placeholder_fields
    }


def make_new_order(order_info: dict, capacity_debug: bool = False) ->  Dict[str, Any]:
    """
    Creates a new restaurant reservation after validating information and checking capacity.

    Parameters:
        order_info (Dict[str, Any]): Complete order information including customer and reservation details
        capacity_debug (bool, optional): If True, includes detailed capacity check information. Defaults to False.

    Returns:
        Dict[str, Any]: Order result containing:
            - status: 'success' or 'error'
            - message: Human readable result description
            - order: Complete order details if successful
            - missing_fields: List of missing fields if validation fails
            - placeholder_fields: List of fields with placeholders if validation fails
            - capacity_details: Detailed capacity information if capacity check fails and debug=True
    """

    logger.info(f"ORDER REQUEST: {order_info}")

    review = review_information_before_order(order_info)
    if review["status"] == "invalid":
        logger.info(f"ORDER VALIDATION FAILED: Missing fields: {review['missing_fields']}")
        return {
            "status": "error",
            "message": "Information validation failed",
            "missing_fields": review.get("missing_fields", []),
            "placeholder_fields": review.get("placeholder_fields", [])
        }
    
    logger.info(f"ORDER VALIDATION PASSED: All required fields present")

    logger.info("CHECKING CAPACITY")
    capacity_result = check_capacity(
        order_info["restaurant_id"],
        order_info["party_size"],
        order_info["reservation_date"],
        order_info["reservation_time"],
        debug=capacity_debug
    )
    logger.info("CAPACITY CHECK COMPLETE")
    logger.info(capacity_result)
    
    if isinstance(capacity_result, dict):
        logger.info(f"CAPACITY CHECK RESULT: {capacity_result}")
        if not capacity_result["is_within_capacity"]:
            logger.info(f"CAPACITY EXCEEDED: Restaurant {order_info['restaurant_id']} cannot accommodate {order_info['party_size']} people")
            return {
                "status": "error",
                "message": "Capacity exceeded. Please choose a different time or reduce party size.",
                "capacity_details": capacity_result
            }
    else:
        if not capacity_result:
            logger.info(f"CAPACITY EXCEEDED: Restaurant {order_info['restaurant_id']} cannot accommodate {order_info['party_size']} people")
            return {
                "status": "error",
                "message": "Capacity exceeded. Please choose a different time slot or reduce party size."
            }
    
    logger.info("CREATING NEW ORDER")
    order_id = f"ord{len(order_management_table) + 1:03d}"
    new_order = order_info.copy()
    new_order["order_id"] = order_id
    new_order["status"] = "confirmed"
    logger.info("NEW ORDER CREATED")

    try:
        order_management_table.append(new_order)
        logger.info(f"ORDER CONFIRMED: {order_id} for {order_info['orderer_name']}")

        with open('data/bookings_list.json', 'w') as f:
            json.dump(order_management_table, f, indent=2)

        logger.info(f"ORDER SAVED TO DATABASE")

    except Exception as e:
        logger.info(f"ERROR SAVING ORDER: {str(e)}")
    
    return {
        "status": "success",
        "message": "Reservation confirmed",
        "order": new_order
    }


@app.post("/restaurants/search")
async def api_search_restaurants(query: RestaurantQuery):
    """
    API endpoint for searching restaurants based on query parameters.

    Parameters:
        query (RestaurantQuery): Search criteria in Pydantic model format

    Returns:
        JSON response with search results
    """
    results = search_restaurant_information(query.dict())
    return results


@app.post("/reservations")
async def api_make_reservation(reservation: Reservation):
    """
    API endpoint for creating new restaurant reservations.

    Parameters:
        reservation (Reservation): Reservation details in Pydantic model format

    Returns:
        JSON response with reservation result
    Raises:
        HTTPException: 400 status code if reservation cannot be completed
    """

    result = make_new_order(reservation.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


