import sqlite3

# phone_number = "0868538364"
# search_phone_number = "0956781234"
search_phone_number = "0868538364"

import sqlite3

# phone_number = "0868538364"
#
# try:
#     conn = sqlite3.connect('clinic_bookings.db')
#     cursor = conn.cursor()
#
#     # Query the database for all appointments matching the phone number
#     cursor.execute("""
#         SELECT type_of_service, doctor_name, schedule_date, schedule_time
#         FROM bookings
#         WHERE phone_number = ?
#     """, (phone_number,))
#
#     appointments = cursor.fetchall()
#
#     if appointments:
#         print(f"Appointments for phone number {phone_number}:")
#         for idx, appointment in enumerate(appointments, start=1):
#             type_of_service, doctor_name, schedule_date, schedule_time = appointment
#             print(f"{idx}. {type_of_service} with {doctor_name} on {schedule_date} at {schedule_time}.")
#     else:
#         print("Sorry, no appointments found for this phone number.")
# except sqlite3.Error as e:
#     print(f"An error occurred while searching the database: {e}")
# finally:
#     if conn:
#         conn.close()

# try:
#     # Connect to the SQLite database
#     conn = sqlite3.connect('clinic_bookings.db')
#     cursor = conn.cursor()
#
#     # Query the database for all appointments matching the phone number
#     cursor.execute("""
#         SELECT type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time
#         FROM bookings
#         WHERE phone_number = ?
#     """, (search_phone_number,))
#
#     appointments = cursor.fetchall()
#     if appointments:
#         # Format and send the appointment details to the user
#         messages = [
#             f"{idx}. Service: {type_of_service} ({type_of_disease}), Doctor: {doctor_name}, "
#             f"Phone: {phone_number}, Date: {schedule_date}, Time: {schedule_time}."
#             for idx, (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time) in
#             enumerate(appointments, start=1)
#         ]
#         print(f"Here are your appointments for phone number {search_phone_number}:\n" + "\n".join(messages))
#     else:
#         print(f"Sorry, I couldn't find any appointments for phone number {search_phone_number}.")
#     conn.close()
#
# except sqlite3.Error as e:
#     print(f"An error occurred while searching the database: {e}")


