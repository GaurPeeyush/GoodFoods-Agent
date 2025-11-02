"""
Main logic module for the restaurant booking system.
Handles API calls, response formatting, and tool execution.
"""

#Basic Imports
import json
import re
import requests
from typing import Union

#Third-party Imports
from openai import OpenAI

#Internal Imports
from data.service_api import *

# Setup logging
import logging
logger = logging.getLogger('goodfoods')

#Global Constant
BASE_URL = "http://localhost:8000"
logger.info(f"BASE URL for API calls set as: {BASE_URL}")


#All Functions Available (all the functions in the conversation engine)
# collect_user_console_message()
# generate_chat_completion(api_key, conv_history, tools, model_type, tool_calling_enabled)
# normalize_chat_response(api_response_obj)
# execute_tool_calls(list_of_tool_calls)
# dispatch_backend_tool(function_name, function_args)
# has_function_simulation(response_text)


def collect_user_console_message() -> dict[str, str]:
    """
    Get and format user input for conversation.

    Returns:
        dict: Formatted message with user input
        Format: {"role": "user", "content": str}
    """

    user_input = input("USER>")
    user_message_formatted = {"role": "user", "content": user_input}

    return user_message_formatted


def generate_chat_completion(api_key, conversation_history: list, tools: list, model_type='gpt-4o', tool_calling_enabled: bool=False):
    """
    Make API call to AI model with conversation history.

    Args:
        api_key: API authentication key
        conversation_history: List of conversation messages
        tools: List of available tools
        model_type: AI model identifier
        tool_calling_enabled: Whether to enable tool calls

    Returns:
        object: Raw API response object
    """

    client = OpenAI(api_key=api_key)

    if tool_calling_enabled is True:
        ai_api_response_obj = client.chat.completions.create(
            model=model_type,
            messages=conversation_history,
            tools=tools,
            tool_choice="auto",
        )
    
    else:
        ai_api_response_obj = client.chat.completions.create(
            model=model_type,
            messages=conversation_history
        )
    
    return ai_api_response_obj


def normalize_chat_response(api_response_obj: object) -> Union[list, dict]:
    """
    Format API response and handle tool calls or message content.

    Args:
        api_response_obj: Raw API response object from AI model

    Returns:
        list: List of tool calls if present
        dict: Formatted assistant message if text content present
        Format: {"role": "assistant", "content": str}
    """

    message = api_response_obj.choices[0].message

    if message.tool_calls:
        logger.info("The agent response includes tool calls.")
        list_of_tool_calls = message.tool_calls
        return list_of_tool_calls
    
    elif message.content:
        logger.info("The agent response includes message content.")
        formatted_api_response_content = {"role": "assistant", "content": message.content}
        return formatted_api_response_content
    else:
        
        return {"role": "assistant", "content": ""}
     

def execute_tool_calls(list_of_tool_calls: list) -> list:
    """
    Process and execute list of tool calls from AI response.

    Args:
        list_of_tool_calls: List of tool call objects from AI response

    Returns:
        list: List of formatted tool responses
        Format: [{"role": "tool", "tool_call_id": str, "name": str, "content": str}, ...]
    """

    list_of_tool_call_responses = []
    for tool_call in list_of_tool_calls:
        
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        function_response = dispatch_backend_tool(function_name, function_args)
        
        if isinstance(function_response, (list, dict)):
            function_response = json.dumps(function_response)

        tool_call_response_formatted = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": function_response,
            }
        
        logger.info(tool_call_response_formatted)

        list_of_tool_call_responses.append(tool_call_response_formatted)

    return list_of_tool_call_responses


def dispatch_backend_tool(function_name: str, function_args: dict) -> Union[dict, str]:
    """
    Execute specific tool functions via API endpoints.

    Args:
        function_name (str): Name of the tool function to execute
        function_args (dict): Arguments for the tool function
        BASE_URL (str): Base URL for API endpoints

    Returns:
        dict/str: Function output from API endpoint or error message
    """ 

    if function_name == 'lookup_dining_options':
        logger.info(f"Running Tool Call: {function_name} with arguments {function_args}")
        logger.info(f"Sending API request to {BASE_URL}/restaurants/search with args: {function_args}")
        try:
            response = requests.post(f"{BASE_URL}/restaurants/search", json=function_args)
            function_output = response.json()
        except Exception as e:
            logger.error(f"API call failed for {function_name}: {str(e)}", exc_info=True)
            function_output = {"error": f"Failed to execute {function_name}: {str(e)}"}
        
    elif function_name == 'confirm_table_booking':
        logger.info(f"Running Tool Call: {function_name} with arguments {function_args}")
        logger.info(f"Sending API request to {BASE_URL}/reservations with args: {function_args}")
        capacity_debug = function_args.pop("capacity_debug", False)
        try:
            response = requests.post(f"{BASE_URL}/reservations", json=function_args)
            function_output = response.json()
        except Exception as e:
            logger.error(f"API call failed for {function_name}: {str(e)}", exc_info=True)
            function_output = {"error": f"Failed to execute {function_name}: {str(e)}"}
        
    else:
        function_output = f"No tool found with name {function_name}"

    # Logging a tool_response preview    
    response_preview = str(function_output)[:100] + "..." if len(str(function_output)) > 100 else function_output
    logger.info(f"Got output from tool: {function_name} - {response_preview}")

    return function_output


def has_function_simulation(response_text: str) -> bool:
    """
    Checks if the LLM response contains function simulation patterns.
    
    Parameters:
        response_text (str): The text content from the LLM response
        
    Returns:
        bool: True if function simulation is detected, False otherwise
    """

    patterns = [
        r"<function[^>]*>",
        r"<tool[^>]*>",
        r"function\([^)]*\)",
        r"tool\([^)]*\)",
        r"confirm_table_booking\([^)]*\)",
        r"lookup_dining_options\([^)]*\)"
    ]

    for pattern in patterns:
        if re.search(pattern, response_text, re.IGNORECASE):
            return True
        
    return False


