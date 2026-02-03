from abc import ABC, abstractmethod

class Hospitaldata(ABC):

    @abstractmethod
    def get_bills(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_reports(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_doctors_by_specialty(self, specialty: str) -> list[str]:
        pass

    @abstractmethod
    def book_appointment(self, user_id: str, doctor: str, time: str) -> str:
        pass

    @abstractmethod
    def cancel_appointment(self, user_id: str) -> str:
        pass

    @abstractmethod
    def update_appointment(self, user_id: str, doctor: str, time: str) -> str:
        pass