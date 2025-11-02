"""
Restaurant booking system tool definitions and configurations.
Contains function specifications for restaurant search and order management.
"""

#Basic type imports
from typing import List, Dict, Union

#Setting up basic logging
import logging
logger = logging.getLogger('goodfoods')
logger.info("Prompts loaded")

restaurant_tools: List[Dict[str, Union[str, Dict[str, Union[str, Dict[str, Union[str, List[str], Dict[str, Union[str, Dict]]]]]]]]] = [
    {
        "type": "function",
        "function": {
            "name": "lookup_dining_options",
            "description": (
                '''
                "Search for restaurants based on user-provided criteria. Use any specific information the user mentions to find the best matches.

                Core Function:
                - Returns matching restaurants sorted by relevance
                - When specific criteria are mentioned, uses them to find the best matches
                - Without specific criteria, returns top 10 recommended restaurants
                - All searches return complete restaurant details including restaurant_id

                Valid Parameters:
                - name: Restaurant name as mentioned by user
                - location: Areas or landmarks user mentions (e.g., 'Koramangala', 'MG Road')
                - cuisine: Common cuisine types (Indian, Italian, Mediterranean, Asian, Continental, American)
                - operating_hours: Time in HH:MM format
                - operating_days: Days of operation
                - restaurant_max_seating_capacity: Total capacity (30-120) - useful when discussing venue size or large groups
                - max_booking_party_size: Group size limits (6-20) - relevant for booking discussions

                Usage Guidelines:
                1. Search Approach:
                - Use any specific details the user mentions
                - Perform focused searches with clear criteria
                - Only use empty search when user gives no specific preferences

                2. Parameter Best Practices:
                - Include all relevant details mentioned by user
                - Use terms as mentioned by user
                - When user mentions group size or capacity needs, use appropriate capacity parameters

                3. Capacity Context:
                - restaurant_max_seating_capacity helps find venues suitable for larger gatherings
                - max_booking_party_size helps match restaurants to specific group booking needs

                The function returns matching restaurants with all details needed for reservations."
                '''
            ),
            "parameters": {
                "type": "object",
                "required": [],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the restaurant."
                    },
                    "location": {
                        "type": "string",
                        "description": "Keywords or location details of the restarurant which can include street address or nearby landmark mentioned by the user."
                    },
                    "cuisine": {
                        "type": "string",
                        "description": "Keywords of cuisine types served by the restaurant."
                    },
                    "operating_hours": {
                        "type": "object",
                        "properties": {
                            "open": {
                                "type": "string",
                                "description": "Opening time in HH:MM format."
                            },
                            "close": {
                                "type": "string",
                                "description": "Closing time in HH:MM format."
                            }
                        },
                        "description": "Operating hours of the restaurant."
                    },
                    "phone": {
                        "type": "string",
                        "description": "Contact phone number."
                    },
                    "restaurant_max_seating_capacity":
                    {
                        "type": "integer",
                        "description": "Maximum seating capacity of the restaurant."
                    },
                    "max_booking_party_size":
                    {
                        "type": "integer",
                        "description": "Maximum allowed party size for a single reservation."
                    },
                    "operating_days": {
                        "type": "string",
                        "description": "Days of the week when the restaurant is open."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_table_booking",
            "description": (
                        '''
                        "Tool to confirm restaurant reservations. Use after naturally collecting all booking details through conversation.

                        Required Information:
                        - restaurant_id: From your restaurant search results
                        - orderer_name: Customer's actual name (collect naturally in conversation)
                        - orderer_contact: Valid phone number
                        - party_size: Number of guests (must fit restaurant's capacity)
                        - reservation_date: Convert any date format user provides to YYYY-MM-DD
                        - reservation_time: Convert user's preferred time to HH:MM (24-hour)

                        Before Confirming:
                        1. Ensure you have all needed details from natural conversation
                        2. Handle all date/time conversions (tomorrow, next week, evening, etc.)
                        3. Verify party size works for the restaurant
                        4. Review complete booking details with customer

                        Response Types:
                        - Successful Booking: Share confirmation details
                        - Capacity Issues: Help find alternatives (different time/restaurant)
                        - Missing Details: Continue conversation to collect information
                        - Invalid Information: Clarify and correct through conversation

                        Important:
                        - Collect information naturally through conversation
                        - Convert dates and times internally without asking user for specific formats
                        - Always confirm complete booking details before finalizing
                        - Never guess or assume any details
                        - Don't proceed if party size exceeds restaurant capacity"
                        '''
            ),
            "parameters": {
                "type": "object",
                "required": [
                    "restaurant_id",
                    "orderer_name",
                    "orderer_contact",
                    "party_size",
                    "reservation_date",
                    "reservation_time"
                ],
                "properties": {
                    "restaurant_id": {
                        "type": "string",
                        "description": "Unique identifier of the restaurant."
                    },
                    "orderer_name": {
                        "type": "string",
                        "description": "Name of the person making the reservation."
                    },
                    "orderer_contact": {
                        "type": "string",
                        "description": "Contact information for the orderer."
                    },
                    "party_size": {
                        "type": "integer",
                        "description": "Number of people for the reservation."
                    },
                    "reservation_date": {
                        "type": "string",
                        "description": "Reservation date in YYYY-MM-DD format. Convert relative dates (tomorrow, next Friday) to this format."
                    },
                    "reservation_time": {
                        "type": "string",
                        "description": "Reservation time in HH:MM format."
                    }
                },
                "description": "A complete JSON object containing all required order information."
            }
        }
    }
]


