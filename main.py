from flask import Flask, jsonify, render_template

# Initialize the Flask application
app = Flask(__name__)

# --- MOCK DATA ---
# This data is now managed by the backend.
# In a real application, this would come from a database.
PATIENTS_DATA = [
    { 'id': 'P12345', 'name': 'Alex Johnson', 'medication': 'Metformin', 'condition': 'Diabetes', 'dueDate': '2025-07-25', 'lastRefill': '2025-06-25', 'doctor': 'Dr. Carter', 'lastContact': '2025-07-26', 'contactLog': 'SMS (Final Reminder)', 'adherence': 'Missed', 'opsIssue': 'Manual Call Required', 'insurance': 'Aetna - Verified', 'contact': '555-0101' },
    { 'id': 'P67890', 'name': 'Maria Garcia', 'medication': 'Atorvastatin', 'condition': 'Hyperlipidemia', 'dueDate': '2025-08-01', 'lastRefill': '2025-07-02', 'doctor': 'Dr. Lee', 'lastContact': '2025-07-25', 'contactLog': 'Email (Initial)', 'adherence': 'At Risk', 'opsIssue': 'None', 'insurance': 'Cigna - Verified', 'contact': '555-0102' },
    { 'id': 'P55432', 'name': 'David Chen', 'medication': 'Ozempic', 'condition': 'Diabetes', 'dueDate': '2025-08-05', 'lastRefill': '2025-07-06', 'doctor': 'Dr. Patel', 'lastContact': 'N/A', 'contactLog': 'None', 'adherence': 'Good', 'opsIssue': 'Insurance Mismatch', 'insurance': 'BCBS - Pending', 'contact': '555-0103' },
    { 'id': 'P87654', 'name': 'Sarah Miller', 'medication': 'Levothyroxine', 'condition': 'Hypothyroidism', 'dueDate': '2025-08-10', 'lastRefill': '2025-07-11', 'doctor': 'Dr. Carter', 'lastContact': 'N/A', 'contactLog': 'None', 'adherence': 'Good', 'opsIssue': 'Out of Stock', 'insurance': 'United - Verified', 'contact': '555-0104' },
    { 'id': 'P99876', 'name': 'James Brown', 'medication': 'Lisinopril', 'condition': 'Hypertension', 'dueDate': '2025-08-22', 'lastRefill': '2025-07-23', 'doctor': 'Dr. Lee', 'lastContact': 'N/A', 'contactLog': 'None', 'adherence': 'Good', 'opsIssue': 'None', 'insurance': 'Humana - Verified', 'contact': '555-0105' },
    { 'id': 'P11223', 'name': 'Emily White', 'medication': 'Amlodipine', 'condition': 'Hypertension', 'dueDate': '2025-08-02', 'lastRefill': '2025-07-03', 'doctor': 'Dr. Patel', 'lastContact': '2025-07-26', 'contactLog': 'SMS (Initial)', 'adherence': 'At Risk', 'opsIssue': 'None', 'insurance': 'Aetna - Verified', 'contact': '555-0106' },
    { 'id': 'P22334', 'name': 'Michael Clark', 'medication': 'Metformin', 'condition': 'Diabetes', 'dueDate': '2025-08-15', 'lastRefill': '2025-07-16', 'doctor': 'Dr. Carter', 'lastContact': 'N/A', 'contactLog': 'None', 'adherence': 'Good', 'opsIssue': 'None', 'insurance': 'Cigna - Verified', 'contact': '555-0107' },
]

@app.route('/')
def index():
    """
    Serve the main HTML file that contains the dashboard application.
    Flask will look for 'index.html' in a 'templates' folder.
    """
    return render_template('index.html')

@app.route('/api/patients')
def get_patients():
    """
    API endpoint to provide the patient data in JSON format.
    The frontend will fetch data from this endpoint.
    """
    return jsonify(PATIENTS_DATA)

if __name__ == '__main__':
    """
    Run the Flask development server.
    'debug=True' allows for automatic reloading when code changes.
    """
    app.run(debug=True)
