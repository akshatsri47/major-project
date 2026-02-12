from langchain.tools import tool
import requests
import json

from config import BACKEND_URL


@tool
def get_billing_summary() -> str:
    """Fetch a summary of all billing records from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/billing/summary")
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except requests.RequestException:
        return "Error fetching billing summary"


@tool
def get_patient_billing_details(patient_id: str) -> str:
    """
    Fetch detailed billing information for a specific patient.

    Args:
        patient_id: The unique identifier of the patient.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/billing/patient/{patient_id}")
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except requests.RequestException:
        return f"Error fetching billing details for patient {patient_id}"

