import sqlite3
from datetime import datetime

try:
    # Establish connection to the SQLite database
    conn = sqlite3.connect('clinic_bookings.db')
    cursor = conn.cursor()

    # Create or update the table structure with `phone_number` next to `doctor_name`
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            type_of_service TEXT NOT NULL,
            type_of_disease TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,  -- Placed next to doctor_name
            schedule_date TEXT NOT NULL,
            schedule_time TEXT NOT NULL,
            booking_time TEXT NOT NULL
        )
    """)

    # Sample booking data
    booking_data = [
        {"type_of_service": "General ENT Consultation", "type_of_disease": "general consultation", "doctor_name": "Dr. Linh Tran", "phone_number": "0123456789", "schedule_date": "25:12:2024", "schedule_time": "10:30"},
        {"type_of_service": "Audiology Services", "type_of_disease": "hearing issue", "doctor_name": "Dr. Bao Le", "phone_number": "0987654321", "schedule_date": "26:12:2024", "schedule_time": "14:00"},
        {"type_of_service": "Sinus and Nasal Care", "type_of_disease": "sinusitis", "doctor_name": "Dr. Minh Vu", "phone_number": "0912345678", "schedule_date": "27:12:2024", "schedule_time": "16:45"},
        {"type_of_service": "Throat Care", "type_of_disease": "throat pain", "doctor_name": "Dr. Linh Tran", "phone_number": "0923456789", "schedule_date": "28:12:2024", "schedule_time": "09:15"},
        {"type_of_service": "Pediatric ENT Services", "type_of_disease": "pediatric ENT issue", "doctor_name": "Dr. An Nguyen", "phone_number": "0934567890", "schedule_date": "29:12:2024", "schedule_time": "11:00"},
        {"type_of_service": "Allergy Care", "type_of_disease": "allergy", "doctor_name": "Dr. Linh Tran", "phone_number": "0956781234", "schedule_date": "30:12:2024", "schedule_time": "10:00"},
        {"type_of_service": "Sleep Apnea Treatment", "type_of_disease": "sleep apnea", "doctor_name": "Dr. Bao Le", "phone_number": "0976543210", "schedule_date": "31:12:2024", "schedule_time": "15:30"}
    ]

    # Insert the booking data into the database
    for booking in booking_data:
        type_of_service = booking['type_of_service']
        type_of_disease = booking['type_of_disease']
        doctor_name = booking['doctor_name']
        phone_number = booking['phone_number']
        schedule_date = booking['schedule_date']
        schedule_time = booking['schedule_time']
        booking_time = datetime.now().strftime("%H:%M:%d:%m:%Y")  # Format: hh:mm:dd:mm:yy

        cursor.execute("""
            INSERT INTO bookings 
            (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time, booking_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (type_of_service, type_of_disease, doctor_name, phone_number, schedule_date, schedule_time, booking_time))

    # Commit the changes
    conn.commit()

    print("Database updated and data insertion successful!")
    conn.close()

except sqlite3.Error as e:
    print("SQLite error:", e)

