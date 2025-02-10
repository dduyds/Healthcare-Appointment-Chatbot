import sqlite3
conn = sqlite3.connect('clinic_bookings.db')
cursor = conn.cursor()

# Query the database for property recommendations based on user preferences and date range
cursor.execute("""
            SELECT *
            FROM bookings
        """)
results = cursor.fetchall()
print(results)
conn.close()