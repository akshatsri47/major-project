from langchain.tools import tool
import requests
import json

from config import BACKEND_URL


@tool
def get_daily_report() -> str:
    """Fetch today's overall report from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/reports/daily")
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except requests.RequestException:
        return "Error fetching daily report"


@tool
def get_monthly_report(month: str, year: str) -> str:
    """
    Fetch a monthly report for a given month and year.

    Args:
        month: Month in MM format (e.g. '01' for January).
        year: Year in YYYY format (e.g. '2026').
    """
    try:
        params = {"month": month, "year": year}
        response = requests.get(f"{BACKEND_URL}/reports/monthly", params=params)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except requests.RequestException:
        return f"Error fetching report for {month}/{year}"

