from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database setup
DB_FILE = 'hospital.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS patient
                 (Patient_id INTEGER PRIMARY KEY,
                  Patient_name TEXT,
                  Patient_age INTEGER,
                  patient_gender TEXT,
                  Patient_number TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS doctor
                 (doctor_id INTEGER PRIMARY KEY,
                  doctor_name TEXT,
                  doctor_gender TEXT,
                  doctor_speciality TEXT,
                  doctor_number TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointment
                 (appointment_id INTEGER PRIMARY KEY,
                  Patient_id INTEGER,
                  doctor_id INTEGER,
                  appointment_date TEXT,
                  appointment_time TEXT,
                  FOREIGN KEY (Patient_id) REFERENCES patient(Patient_id),
                  FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS medicine
                 (medicine_id INTEGER PRIMARY KEY,
                  medicine_name TEXT,
                  medicine_stock INTEGER CHECK (medicine_stock > 0),
                  manufacture_date TEXT,
                  expiry_date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS prescription
                 (Patient_id INTEGER,
                  doctor_id INTEGER,
                  visit_date TEXT,
                  visit_time TEXT,
                  medicine_id INTEGER,
                  dosage TEXT,
                  duration TEXT,
                  PRIMARY KEY (Patient_id),
                  FOREIGN KEY (Patient_id) REFERENCES patient(Patient_id),
                  FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
                  FOREIGN KEY (medicine_id) REFERENCES medicine(medicine_id))''')

    # Insert sample data
    c.execute("INSERT OR IGNORE INTO patient VALUES (1, 'Rahul Sharma', 21, 'M', '9876543210')")
    c.execute("INSERT OR IGNORE INTO patient VALUES (2, 'Ananya Verma', 19, 'F', '9123456789')")
    c.execute("INSERT OR IGNORE INTO patient VALUES (3, 'Arjun Singh', 25, 'M', '9543217890')")
    c.execute("INSERT OR IGNORE INTO patient VALUES (4, 'Neha Patel', 22, 'F', '9988776655')")
    c.execute("INSERT OR IGNORE INTO patient VALUES (5, 'Vikram Mehta', 23, 'M', '9001122334')")

    c.execute("INSERT OR IGNORE INTO doctor VALUES (101, 'Dr. Ramesh Gupta', 'M', 'General Physician', '8001234567')")
    c.execute("INSERT OR IGNORE INTO doctor VALUES (102, 'Dr. Sneha Kapoor', 'F', 'Dermatologist', '8112233445')")
    c.execute("INSERT OR IGNORE INTO doctor VALUES (103, 'Dr. Mohan Rao', 'M', 'Cardiologist', '8223344556')")
    c.execute("INSERT OR IGNORE INTO doctor VALUES (104, 'Dr. Priya Nair', 'F', 'Pediatrician', '8334455667')")
    c.execute("INSERT OR IGNORE INTO doctor VALUES (105, 'Dr. Arvind Tiwari', 'M', 'Orthopedic', '8445566778')")

    # Insert sample appointments
    c.execute("INSERT OR IGNORE INTO appointment VALUES (1, 1, 101, '2025-04-15', '10:00:00')")
    c.execute("INSERT OR IGNORE INTO appointment VALUES (2, 2, 102, '2025-04-15', '11:00:00')")
    c.execute("INSERT OR IGNORE INTO appointment VALUES (3, 3, 103, '2025-04-16', '14:30:00')")
    c.execute("INSERT OR IGNORE INTO appointment VALUES (4, 4, 104, '2025-04-16', '15:30:00')")
    c.execute("INSERT OR IGNORE INTO appointment VALUES (5, 5, 105, '2025-04-17', '09:30:00')")

    # Insert sample medicines
    c.execute("INSERT OR IGNORE INTO medicine VALUES (1, 'Paracetamol', 100, '2025-01-01', '2026-01-01')")
    c.execute("INSERT OR IGNORE INTO medicine VALUES (2, 'Amoxicillin', 50, '2025-02-01', '2026-02-01')")
    c.execute("INSERT OR IGNORE INTO medicine VALUES (3, 'Omeprazole', 75, '2025-03-01', '2026-03-01')")
    c.execute("INSERT OR IGNORE INTO medicine VALUES (4, 'Metformin', 80, '2025-01-15', '2026-01-15')")
    c.execute("INSERT OR IGNORE INTO medicine VALUES (5, 'Amlodipine', 60, '2025-02-15', '2026-02-15')")

    # Insert sample prescriptions
    c.execute("INSERT OR IGNORE INTO prescription VALUES (1, 101, '2025-04-15', '10:00:00', 1, '500mg', '3 days')")
    c.execute("INSERT OR IGNORE INTO prescription VALUES (2, 102, '2025-04-15', '11:00:00', 2, '250mg', '5 days')")
    c.execute("INSERT OR IGNORE INTO prescription VALUES (3, 103, '2025-04-16', '14:30:00', 3, '20mg', '7 days')")
    c.execute("INSERT OR IGNORE INTO prescription VALUES (4, 104, '2025-04-16', '15:30:00', 4, '500mg', '30 days')")
    c.execute("INSERT OR IGNORE INTO prescription VALUES (5, 105, '2025-04-17', '09:30:00', 5, '5mg', '30 days')")

    conn.commit()
    conn.close()

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as error:
        print(f"Error connecting to SQLite Database: {error}")
        return None

# Route for serving static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

# API Routes
@app.route('/api/patients', methods=['GET'])
def get_patients():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patient")
            patients = [dict(row) for row in cursor.fetchall()]
            return jsonify(patients)
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctor")
            doctors = [dict(row) for row in cursor.fetchall()]
            return jsonify(doctors)
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, p.Patient_name, d.doctor_name 
                FROM appointment a 
                JOIN patient p ON a.Patient_id = p.Patient_id 
                JOIN doctor d ON a.doctor_id = d.doctor_id
            """)
            appointments = [dict(row) for row in cursor.fetchall()]
            return jsonify(appointments)
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicine")
            medicines = [dict(row) for row in cursor.fetchall()]
            return jsonify(medicines)
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, pt.Patient_name, d.doctor_name, m.medicine_name
                FROM prescription p
                JOIN patient pt ON p.Patient_id = pt.Patient_id
                JOIN doctor d ON p.doctor_id = d.doctor_id
                JOIN medicine m ON p.medicine_id = m.medicine_id
            """)
            prescriptions = [dict(row) for row in cursor.fetchall()]
            return jsonify(prescriptions)
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# CRUD operations for each entity
# Patients
@app.route('/api/patients', methods=['POST'])
def add_patient():
    conn = get_db_connection()
    if conn:
        try:
            data = request.json
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patient (Patient_id, Patient_name, Patient_age, patient_gender, Patient_number)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['patient_id'],
                data['patient_name'],
                data['patient_age'],
                data['patient_gender'],
                data['patient_number']
            ))
            conn.commit()
            return jsonify({'message': 'Patient added successfully'}), 201
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# Doctors
@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    conn = get_db_connection()
    if conn:
        try:
            data = request.json
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctor (doctor_id, doctor_name, doctor_gender, doctor_speciality, doctor_number)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['doctor_id'],
                data['doctor_name'],
                data['doctor_gender'],
                data['doctor_speciality'],
                data['doctor_number']
            ))
            conn.commit()
            return jsonify({'message': 'Doctor added successfully'}), 201
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# Appointments
@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    conn = get_db_connection()
    if conn:
        try:
            data = request.json
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointment (appointment_id, Patient_id, doctor_id, appointment_date, appointment_time)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['appointment_id'],
                data['patient_id'],
                data['doctor_id'],
                data['appointment_date'],
                data['appointment_time']
            ))
            conn.commit()
            return jsonify({'message': 'Appointment added successfully'}), 201
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# Medicines
@app.route('/api/medicines', methods=['POST'])
def add_medicine():
    conn = get_db_connection()
    if conn:
        try:
            data = request.json
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medicine (medicine_id, medicine_name, medicine_stock, manufacture_date, expiry_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['medicine_id'],
                data['medicine_name'],
                data['medicine_stock'],
                data['manufacture_date'],
                data['expiry_date']
            ))
            conn.commit()
            return jsonify({'message': 'Medicine added successfully'}), 201
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

# Prescriptions
@app.route('/api/prescriptions', methods=['POST'])
def add_prescription():
    conn = get_db_connection()
    if conn:
        try:
            data = request.json
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prescription (Patient_id, doctor_id, visit_date, visit_time, medicine_id, dosage, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data['patient_id'],
                data['doctor_id'],
                data['visit_date'],
                data['visit_time'],
                data['medicine_id'],
                data['dosage'],
                data['duration']
            ))
            conn.commit()
            return jsonify({'message': 'Prescription added successfully'}), 201
        except sqlite3.Error as error:
            return jsonify({'error': str(error)}), 500
        finally:
            if conn:
                conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8000)
