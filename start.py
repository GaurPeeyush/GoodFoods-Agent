"""
GoodFoods Starter

This module launches the GoodFoods reservation system by starting both the 
FastAPI backend server and Streamlit frontend application in the correct sequence.
It starts the API server in a background thread, confirms it's running,
then launches the Streamlit interface as the main process.

Usage:
   python start.py

Dependencies:
   - uvicorn
   - streamlit
   - requests
"""

#Basic imports
import subprocess
import threading
import time
import webbrowser
import os

def start_fastapi_server():
    """Start the FastAPI server in a separate process"""
    try:
        print("Starting FastAPI server...")
        subprocess.Popen(["uvicorn", "data.service_api:app", "--host", "0.0.0.0", "--port", "8000"])
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        return None

def start_streamlit_app():
    """Start the Streamlit app"""
    try:
        print("Starting Streamlit app...")
        subprocess.run(["streamlit", "run", "app_goodfoods.py"])
    except Exception as e:
        print(f"Error starting Streamlit app: {e}")


if __name__ == "__main__":
    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=start_fastapi_server)
    api_thread.daemon = True
    api_thread.start()
    
    # Wait for API server to start
    print("Waiting for API server to start...")
    time.sleep(3)
    
    # Check if API is running by trying to connect
    try:
        import requests
        requests.get("http://localhost:8000/docs")
        print("API server started successfully")
        webbrowser.open("http://localhost:8000/docs")
    except requests.exceptions.ConnectionError:
        print("Warning: API server might not be running correctly")
    
    # Start Streamlit app (blocking call)
    start_streamlit_app()


