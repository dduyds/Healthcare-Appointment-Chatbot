# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from fuzzywuzzy import process
from typing import Any, Text, Dict, List
from rasa_sdk import Action
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from datetime import datetime
from rasa_sdk.events import SlotSet
import http.client
import re
import sqlite3
import json
import requests
from typing import Optional


# Clinic services mapping with doctors
clinic_services = {
    "General ENT Consultation": ["Dr. Linh Tran", "Dr. An Nguyen", "Dr. Bao Le", "Dr. Minh Vu"],
    "Audiology Services": ["Dr. Bao Le", "Dr. Linh Tran"],
    "Sinus and Nasal Care": ["Dr. Linh Tran", "Dr. Minh Vu"],
    "Throat Care": ["Dr. Linh Tran", "Dr. Minh Vu"],
    "Pediatric ENT Services": ["Dr. An Nguyen"],
    "Surgical Procedures": ["Dr. Linh Tran", "Dr. Minh Vu"],
    "Allergy Testing and Treatment": ["Dr. Minh Vu", "Dr. An Nguyen"],
    "Sleep Apnea Management": ["Dr. Minh Vu", "Dr. Linh Tran"],
}

# Mapping of diseases to their corresponding services
disease_to_service_mapping = {
    "general consultation": "General ENT Consultation",
    "hearing issue": "Audiology Services",
    "sinusitis": "Sinus and Nasal Care",
    "throat pain": "Throat Care",
    "pediatric ENT issue": "Pediatric ENT Services",
    "allergy": "Allergy Testing and Treatment",
    "sleep apnea": "Sleep Apnea Management",
}

"""
Unlock this code to run API
Begin
"""
# Contact me for full code.
"""
End
"""

def is_valid_date_format(date_str: str, date_format: str = "%d:%m:%Y") -> bool:
    """Validate whether the given date string matches the specified format."""
    if date_format == "%d:%m:%Y":
        return bool(re.match(r"^\d{2}:\d{2}:\d{4}$", date_str))
    return False  # Add custom handling for other formats if needed

def is_valid_time_format(time_str: str, time_format: str = "%H:%M") -> bool:
    """Validate whether the given time string matches the specified format."""
    if time_format == "%H:%M":
        return bool(re.match(r"^\d{2}:\d{2}$", time_str))
    return False  # Add custom handling for other formats if needed


class ValidateSimpleHealthcareForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_healthcare_form"

    def validate_type_of_disease(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'type_of_disease' value and suggest the correct disease if necessary."""

        type_of_disease = tracker.get_slot("type_of_disease")

        # List of valid disease types (in lower case)
        valid_diseases = list(disease_to_service_mapping.keys())

        # Find the closest match for the user's input
        closest_match, score = process.extractOne(type_of_disease.lower(), valid_diseases)

        if score < 80:  # If the score is below a certain threshold, suggest a valid disease type
            dispatcher.utter_message(
                text=f"I'm sorry, I couldn't recognize that disease. Here are some valid disease types you might have meant: {', '.join(valid_diseases)}."
            )
            return {"type_of_disease": None}

        # Map disease type to clinic service
        service = disease_to_service_mapping.get(closest_match)

        dispatcher.utter_message(
            text=f"Got it! {closest_match} falls under '{service}'."
        )

        return {"type_of_disease": closest_match}

    def validate_doctor_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'doctor_name' value against the suggested doctors."""
        # Get the current type of disease
        type_of_disease = tracker.get_slot("type_of_disease")
        doctor_name = tracker.get_slot("doctor_name")

        if not doctor_name.lower().startswith("dr."):
            doctor_name = "Dr. " + doctor_name.strip()

        # Map disease type to clinic service
        service = disease_to_service_mapping.get(type_of_disease.lower())
        doctors = clinic_services.get(service, [])

        if doctor_name not in doctors:
            dispatcher.utter_message(
                text=f"{doctor_name} is not a specialist for {type_of_disease}. Please choose from {', '.join(doctors)}."
            )
            return {"doctor_name": None}

        dispatcher.utter_message(text=f"Great! You've chosen {doctor_name} for {type_of_disease}.")
        return {"doctor_name": doctor_name}

    def validate_schedule_date(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'schedule_date' slot."""
        schedule_date = tracker.get_slot("schedule_date")

        if schedule_date and is_valid_date_format(schedule_date, "%d:%m:%Y"):
            # If the date format is valid, return the formatted date
            formatted_date = datetime.strptime(schedule_date, "%d:%m:%Y").strftime("%d:%m:%Y")
            dispatcher.utter_message(
                text=f"Good date, {formatted_date}"
            )
            return {"schedule_date": formatted_date}

        # If the format is invalid, request the user to input the date correctly
        dispatcher.utter_message(
            text="Please provide the schedule date in the format dd:mm:yyyy (e.g., 25:12:2024)."
        )
        return {"schedule_date": None}

    def validate_schedule_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'schedule_time' slot."""
        schedule_time = tracker.get_slot("schedule_time")

        if schedule_time and is_valid_time_format(schedule_time, "%H:%M"):
            # If the time format is valid, return the formatted time
            formatted_time = datetime.strptime(schedule_time, "%H:%M").strftime("%H:%M")
            dispatcher.utter_message(
                text=f"Good time, {formatted_time}"
            )
            return {"schedule_time": formatted_time}

        # If the format is invalid, request the user to input the time correctly
        dispatcher.utter_message(
            text="Please provide the schedule time in the format hh:mm (e.g., 15:30)."
        )
        return {"schedule_time": None}

    def validate_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'phone_number' value."""

        phone_number = tracker.get_slot("phone_number")
        pattern = r"^0\d{9}$"
        if not re.match(pattern, phone_number):
            dispatcher.utter_message(text="Please provide a valid phone number starting with '0' and having 10 digits.")
            return {"phone_number": None}

        dispatcher.utter_message(text=f"Got it! Your phone number is {phone_number}.")
        return {"phone_number": phone_number}


class ValidateSearchAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_appointment_form"

    def validate_search_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'search_phone_number' value."""
        search_phone_number = tracker.get_slot("search_phone_number")
        pattern = r"^0\d{9}$"
        if not re.match(pattern, search_phone_number):
            dispatcher.utter_message(text="Please provide a valid phone number starting with '0' and having 10 digits.")
            return {"search_phone_number": None}

        dispatcher.utter_message(text=f"Got it! Your phone number is {search_phone_number}.")
        return {"search_phone_number": search_phone_number}

class ValidateDeleteAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_delete_appointment_form"

    def validate_deleted_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'deleted_phone_number' value extracted from entity."""
        deleted_phone_number = tracker.get_slot("deleted_phone_number")
        pattern = r"^0\d{9}$"
        if not re.match(pattern, deleted_phone_number):
            dispatcher.utter_message(text="Please provide a valid phone number starting with '0' and having 10 digits.")
            return {"deleted_phone_number": None}

        dispatcher.utter_message(text=f"Got it! Your phone number is {deleted_phone_number}.")
        return {"deleted_phone_number": deleted_phone_number}

    def validate_deleted_type_of_disease(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate 'deleted_type_of_diseases' value extracted from entity."""
        deleted_type_of_disease = tracker.get_slot("deleted_type_of_disease")

        # List of valid disease types (in lower case)
        valid_diseases = list(disease_to_service_mapping.keys())

        # Find the closest match for the user's input
        closest_match, score = process.extractOne(deleted_type_of_disease.lower(), valid_diseases)

        if score < 80:  # If the score is below a certain threshold, suggest a valid disease type
            dispatcher.utter_message(
                text=f"I'm sorry, I couldn't recognize that disease. Here are some valid disease types you might have meant: {', '.join(valid_diseases)}."
            )
            return {"deleted_type_of_disease": None}

        # Map disease type to clinic service
        service = disease_to_service_mapping.get(closest_match)

        dispatcher.utter_message(
            text=f"Got it! {closest_match} falls under '{service}'."
        )

        return {"deleted_type_of_disease": closest_match}


# class ActionIngestBookingData(Action):
#     def name(self) -> Text:
#         return "action_ingest_booking_data"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         # Retrieve slots for booking details
#         type_of_disease = tracker.get_slot("type_of_disease")
#         type_of_service = disease_to_service_mapping.get(type_of_disease)
#         doctor_name = tracker.get_slot("doctor_name")
#         schedule_date = tracker.get_slot("schedule_date")
#         schedule_time = tracker.get_slot("schedule_time")
#         phone_number = tracker.get_slot("phone_number")
#
#         # Get the current datetime
#         current_time = datetime.now()
#
#         # Format for database: hh:mm:dd:mm:yyyy
#         time_for_db = current_time.strftime("%H:%M:%d:%m:%Y")
#
#         # Format for display: hh:mm, dd Month yyyy
#         time_for_display = current_time.strftime("%H:%M, %d %B %Y")
#
#         # Ensure all slots are filled
#         if not (type_of_service and doctor_name and schedule_date and schedule_time and phone_number):
#             dispatcher.utter_message(
#                 text="I'm missing some information. Please make sure to provide the type of service, doctor name, schedule date, schedule time, and phone number."
#             )
#             return []
#
#         try:
#             # Establish a connection to the SQLite database
#             conn = sqlite3.connect('clinic_bookings.db')
#             cursor = conn.cursor()
#
#             # Insert the booking data into the database
#             cursor.execute(
#                 """
#                 INSERT INTO bookings
#                 (type_of_service, doctor_name, schedule_date, schedule_time, phone_number, booking_time)
#                 VALUES (?, ?, ?, ?, ?, ?)
#                 """,
#                 (type_of_service, doctor_name, schedule_date, schedule_time, phone_number, time_for_db)
#             )
#             conn.commit()
#             msg = (
#                 f"Your booking for '{type_of_service}' with {doctor_name} on {schedule_date} at {schedule_time} "
#                 f"has been successfully recorded. We will contact you at {phone_number} if needed."
#             )
#             dispatcher.utter_message(text=msg)
#             conn.close()
#
#         except sqlite3.Error as e:
#             dispatcher.utter_message(text=f"An error occurred while saving your booking: {e}")
#             return []
#
#         # Send SMS notification (modify `send_sms` as per your implementation)
#         target_phone_number = "84" + phone_number[1:]
#         notification_message = (
#             f"You have booked an appointment for '{type_of_service}' with {doctor_name} on {schedule_date} "
#             f"at {schedule_time}. Thank you for choosing our clinic!"
#         )
#         stt = send_sms(notification_message, target_phone_number)
#         dispatcher.utter_message(text=stt)
#
#         return [SlotSet("type_of_disease", None),
#                 SlotSet("doctor_name", None),
#                 SlotSet("schedule_date", None),
#                 SlotSet("schedule_time", None),
#                 SlotSet("phone_number", None),]

class ActionIngestBookingData(Action):
    def name(self) -> Text:
        return "action_ingest_booking_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve slots for booking details
        type_of_disease = tracker.get_slot("type_of_disease")
        type_of_service = disease_to_service_mapping.get(type_of_disease)
        doctor_name = tracker.get_slot("doctor_name")
        phone_number = tracker.get_slot("phone_number")
        schedule_date = tracker.get_slot("schedule_date")
        schedule_time = tracker.get_slot("schedule_time")

        # Get the current datetime
        current_time = datetime.now()

        # Format for database: hh:mm:dd:mm:yyyy
        time_for_db = current_time.strftime("%H:%M:%d:%m:%Y")

        # Ensure all necessary slots are filled
        if not (type_of_disease and type_of_service and doctor_name and schedule_date and schedule_time and phone_number):
            dispatcher.utter_message(
                text="I'm missing some information. Please ensure you provide the type of disease, type of service, doctor name, schedule date, schedule time, and phone number."
            )
            return [SlotSet("type_of_disease", None),
                    SlotSet("doctor_name", None),
                    SlotSet("schedule_date", None),
                    SlotSet("schedule_time", None),
                    SlotSet("phone_number", None)]

        try:
            # Establish a connection to the SQLite database
            conn = sqlite3.connect('clinic_bookings.db')
            cursor = conn.cursor()

            # Insert the booking data into the database
            cursor.execute(
                """
                INSERT INTO bookings 
                (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time, booking_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time, time_for_db)
            )
            conn.commit()

            # Confirm successful booking
            msg = (
                f"Your booking for '{type_of_service}' ({type_of_disease}) with {doctor_name} on {schedule_date} "
                f"at {schedule_time} has been successfully recorded. We will contact you at {phone_number} if needed."
            )
            dispatcher.utter_message(text=msg)
            conn.close()

        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"An error occurred while saving your booking: {e}")
            return [SlotSet("type_of_disease", None),
                    SlotSet("doctor_name", None),
                    SlotSet("schedule_date", None),
                    SlotSet("schedule_time", None),
                    SlotSet("phone_number", None)]

        # Send SMS notification (modify `send_sms` as per your implementation)
        target_phone_number = "84" + phone_number[1:]  # Convert to international format
        notification_message = (
            f"You have booked an appointment for '{type_of_service}' ({type_of_disease}) with {doctor_name} on "
            f"{schedule_date} at {schedule_time}. Thank you for choosing our clinic!"
        )
        stt = send_sms(notification_message, target_phone_number)
        dispatcher.utter_message(text=stt)

        # Reset slots after booking
        return [SlotSet("type_of_disease", None),
                SlotSet("doctor_name", None),
                SlotSet("schedule_date", None),
                SlotSet("schedule_time", None),
                SlotSet("phone_number", None)]


# class ActionSearchAppointments(Action):
#     def name(self) -> Text:
#         return "action_search_appointments"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         # Retrieve the phone number from the slot
#         search_phone_number = tracker.get_slot("search_phone_number")
#
#         try:
#             # Connect to the SQLite database
#             conn = sqlite3.connect('clinic_bookings.db')
#             cursor = conn.cursor()
#
#             # Query the database for all appointments matching the phone number
#             cursor.execute("""
#                 SELECT type_of_service, doctor_name, schedule_date, schedule_time
#                 FROM bookings
#                 WHERE phone_number = ?
#             """, (search_phone_number,))
#
#             appointments = cursor.fetchall()
#
#             if appointments:
#                 # Format and send the appointment details to the user
#                 messages = [f"{idx}. {type_of_service} with {doctor_name} on {schedule_date} at {schedule_time}."
#                             for idx, (type_of_service, doctor_name, schedule_date, schedule_time) in
#                             enumerate(appointments, start=1)]
#                 dispatcher.utter_message(
#                     text=f"Here are your appointments for phone number {search_phone_number}:\n" + "\n".join(messages)
#                 )
#             else:
#                 dispatcher.utter_message(
#                     text=f"Sorry, I couldn't find any appointments for phone number {search_phone_number}.")
#             conn.close()
#         except sqlite3.Error as e:
#             dispatcher.utter_message(text=f"An error occurred while searching the database: {e}")
#
#         return [SlotSet("search_phone_number", None)]

class ActionSearchAppointments(Action):
    def name(self) -> Text:
        return "action_search_appointments"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the phone number from the slot
        search_phone_number = tracker.get_slot("search_phone_number")

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('clinic_bookings.db')
            cursor = conn.cursor()

            # Query the database for all appointments matching the phone number
            cursor.execute("""
                SELECT type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time
                FROM bookings
                WHERE phone_number = ?
            """, (search_phone_number,))

            appointments = cursor.fetchall()

            if appointments:
                # Format and send the appointment details to the user
                messages = [
                    f"{idx}. Service: {type_of_service} ({type_of_disease}), Doctor: {doctor_name}, "
                    f"Phone: {phone_number}, Date: {schedule_date}, Time: {schedule_time}."
                    for idx, (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time) in
                    enumerate(appointments, start=1)
                ]
                dispatcher.utter_message(
                    text=f"Here are your appointments for phone number {search_phone_number}:\n" + "\n".join(messages)
                )
            else:
                dispatcher.utter_message(
                    text=f"Sorry, I couldn't find any appointments for phone number {search_phone_number}."
                )
            conn.close()

        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"An error occurred while searching the database: {e}.")


        # Reset the slot after processing
        return [SlotSet("search_phone_number", None)]


class ActionDeleteAppointment(Action):
    def name(self) -> Text:
        return "action_delete_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        deleted_phone_number = tracker.get_slot("deleted_phone_number")
        deleted_type_of_disease = tracker.get_slot("deleted_type_of_disease")

        try:
            conn = sqlite3.connect('clinic_bookings.db')
            cursor = conn.cursor()

            cursor.execute("""
                 DELETE FROM bookings
                 WHERE phone_number = ? AND type_of_disease = ?
             """, (deleted_phone_number, deleted_type_of_disease))

            conn.commit()

            if cursor.rowcount > 0:
                target_phone_number = "84" + deleted_phone_number[1:]
                notification_message = (
                    f"Your appointment for '{deleted_type_of_disease}' has been successfully canceled. "
                    f"If this was a mistake, please contact our clinic to reschedule."
                )
                stt = send_sms(notification_message, target_phone_number)

                # Notify user
                dispatcher.utter_message(text=f"Appointment deleted successfully. {stt}")
            else:
                dispatcher.utter_message(
                    text=f"No appointment found for phone number {deleted_phone_number} and disease {deleted_type_of_disease}."
                )

            conn.close()

        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"An error occurred while deleting the appointment: {e}")

        return [SlotSet("deleted_phone_number", None),
                SlotSet("deleted_type_of_disease", None)]


class ActionWorkingHourQA(Action):
    def name(self) -> Text:
        return "action_working_hour_qa_harmony_ent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        full_message = tracker.latest_message.get("text")

        if full_message:
            # Get the response from the model using the full message
            answer_with_sources = request_model(full_message)

            if answer_with_sources:  # Check if model returns a response
                dispatcher.utter_message(text=answer_with_sources)
            else:
                dispatcher.utter_message(text="Unable to connect to the model. Please try again later.")
        else:
            dispatcher.utter_message(text="I couldn't retrieve the message from your query.")

        return []


class ActionDoctorInfoQA(Action):
    def name(self) -> Text:
        return "action_doctor_info_qa_harmony_ent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        full_message = tracker.latest_message.get("text")

        if full_message:
            # Get the response from the model using the full message
            answer_with_sources = request_model(full_message)

            if answer_with_sources:  # Check if model returns a response
                dispatcher.utter_message(text=answer_with_sources)
            else:
                dispatcher.utter_message(text="Unable to connect to the model. Please try again later.")
        else:
            dispatcher.utter_message(text="I couldn't retrieve the message from your query.")

        return []


class ActionServiceInfoQA(Action):
    def name(self) -> Text:
        return "action_service_info_qa_harmony_ent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        full_message = tracker.latest_message.get("text")

        if full_message:
            # Get the response from the model using the full message
            answer_with_sources = request_model(full_message)

            if answer_with_sources:  # Check if model returns a response
                dispatcher.utter_message(text=answer_with_sources)
            else:
                dispatcher.utter_message(text="Unable to connect to the model. Please try again later.")
        else:
            dispatcher.utter_message(text="I couldn't retrieve the message from your query.")

        return []


class ActionGeneralInfoQA(Action):
    def name(self) -> Text:
        return "action_general_info_qa_harmony_ent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        full_message = tracker.latest_message.get("text")

        if full_message:
            # Get the response from the model using the full message
            answer_with_sources = request_model(full_message)

            if answer_with_sources:  # Check if model returns a response
                dispatcher.utter_message(text=answer_with_sources)
            else:
                dispatcher.utter_message(text="Unable to connect to the model. Please try again later.")
        else:
            dispatcher.utter_message(text="I couldn't retrieve the message from your query.")

        return []
