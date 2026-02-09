from langchain.tools import tool
from datetime import date,time
import requests
from config import BACKEND_URL
import json
@tool
def get_availablity()-> str:
    """ This tool fetches the current availablity of the doctors that they are available or not """
    try:
        response=requests.get(f"{BACKEND_URL}/getdoc")
        response.raise_for_status()
        doctors = response.json()
        return json.dumps(doctors)
    except requests.exceptions.RequestException as e:
        return f"Error fetching doctors availabiltiy"

