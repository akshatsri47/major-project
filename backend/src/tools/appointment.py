"""Appointment tools: get doctors (all or by specialty) and book via backend API."""
from typing import Any, Optional

import aiohttp
from langchain_core.tools import tool

from config import BACKEND_URL


async def _fetch_doctors(specialty: Optional[str] = None) -> list[dict[str, Any]]:
    """Fetch doctors from backend API. If specialty is None, returns all doctors."""
    base = BACKEND_URL.rstrip("/")
    url = f"{base}/getdoc/{specialty}" if specialty else f"{base}/getdoc"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
    return data.get("doctors", [])


def _format_doctors(doctors: list[dict[str, Any]]) -> str:
    """Format doctor list with names, emails, specialty, and available slots."""
    if not doctors:
        return "No doctors found."
    lines = []
    for i, d in enumerate(doctors, 1):
        name = d.get("name", "?")
        email = d.get("email", "?")
        spec = d.get("specialty", "?")
        slots = d.get("available_slots", [])
        slot_parts = []
        for s in slots[:10]:
            dte = s.get("date", "?")
            times_list = s.get("times", [])
            if times_list:
                slot_parts.append(f"{dte}: {', '.join(str(t) for t in times_list[:8])}")
        slot_str = "\n    ".join(slot_parts) if slot_parts else "No slots"
        lines.append(f"{i}. {name} | {email} | {spec}\n    Slots:\n    {slot_str}")
    return "\n\n".join(lines)


@tool
async def get_doctors(specialty: Optional[str] = None) -> str:
    """Get all doctors, or filter by medical specialty.
    Call with no argument to get all doctors. Or pass a specialty like: general, cardiology, orthopedics, neurology, dermatology, psychiatry.
    Returns each doctor's name, email, specialty, and available date/time slots."""
    doctors = await _fetch_doctors(specialty)
    if specialty:
        return _format_doctors(doctors) if doctors else f"No doctors found for specialty: {specialty}."
    return _format_doctors(doctors) if doctors else "No doctors in the system."


@tool
async def book_appointment(
    doctor_email: str,
    patient_name: str,
    patient_email: str,
    patient_id: str,
    appointment_date: str,
    appointment_time: str,
) -> str:
    """Book an appointment with a doctor.
    doctor_email must match a doctor from get_doctors. appointment_date format: YYYY-MM-DD. appointment_time format: HH:MM or HH:MM:SS."""
    url = f"{BACKEND_URL.rstrip('/')}/book"
    payload = {
        "doctor_email": doctor_email,
        "patient_name": patient_name,
        "patient_email": patient_email,
        "patient_id": patient_id,
        "date": appointment_date,
        "time": appointment_time,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return (
                    f"Booked. Confirmation: appointment_id={data.get('appointment_id')}, "
                    f"doctor={data.get('doctor')}, date={data.get('date')}, time={data.get('time')}."
                )
            try:
                err = await resp.json()
                detail = err.get("detail", str(err))
            except Exception:
                detail = await resp.text()
            return f"Booking failed: {detail}"
