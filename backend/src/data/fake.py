from .base import Hospitaldata

class FakeHospitalDB(Hospitaldata):
    """A fake in-memory hospital database for testing and demos"""

    def __init__(self):
        self.users = {"123": "Akshat", "456": "Riya"}

        self.bills = {
            "123": "₹2300 due for blood tests",
            "456": "No pending bills"
        }

        self.reports = {
            "123": "Blood test: Normal | X-Ray: Pending",
            "456": "MRI: Mild disc bulge"
        }

        self.doctors = {
            "general": ["Dr. Sharma"],
            "cardiology": ["Dr. Rao"],
            "orthopedics": ["Dr. Kapoor"],
            "neurology": ["Dr. Sen"]
        }

        self.appointments = {}

    def get_bills(self, user_id: str) -> str:
        return self.bills.get(user_id, "User not found")

    def get_reports(self, user_id: str) -> str:
        return self.reports.get(user_id, "No reports found")

    def get_doctors_by_specialty(self, specialty: str) -> list[str]:
        return self.doctors.get(specialty, [])

    def book_appointment(self, user_id: str, doctor: str, time: str) -> str:
        self.appointments[user_id] = {
            "doctor": doctor,
            "time": time
        }
        return f"Booked {doctor} at {time}"

    def cancel_appointment(self, user_id: str) -> str:
        if user_id in self.appointments:
            del self.appointments[user_id]
            return "Appointment cancelled"
        return "No appointment found"

    def update_appointment(self, user_id: str, doctor: str, time: str) -> str:
        if user_id in self.appointments:
            self.appointments[user_id] = {
                "doctor": doctor,
                "time": time
            }
            return f"Updated to {doctor} at {time}"
        return "No appointment found to update"