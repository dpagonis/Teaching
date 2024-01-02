from flask import Flask, render_template
import pandas as pd
import datetime
import logging
import serial
import serial.tools.list_ports
from threading import Thread

app = Flask(__name__)

roster_file = 'classroster.csv'

# Function to automatically find and connect to the active COM port
def find_active_com_port():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            return ser
        except serial.SerialException:
            pass
    return None

def mark_attendance_and_respond(id_received, roster, serial_port):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if today not in roster.columns:
        roster[today] = False
    
    student_row = roster[roster['id'] == id_received]
    if not student_row.empty:
        student_name = student_row.iloc[0]['name']
        roster.at[student_row.index[0], today] = True
        response = f"ACK,{student_name}"
        serial_port.write(response.encode())  # Send handshake with name
        print(f"Attendance marked for {student_name} (ID: {id_received})")
    else:
        print(f"No record found for ID: {id_received}")
        serial_port.write("NACK".encode())  # Send negative acknowledgment

# Thread function for handling serial communication
def handle_serial_communication():
    serial_port = find_active_com_port()
    if not serial_port:
        print("No active COM port found. Please check the connection.")
        return

    print(f"Connected to {serial_port.port}")
    roster = pd.read_csv(roster_file)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if today not in roster.columns:
        roster[today] = False
    roster['id'] = roster['id'].astype(str)

    try:
        while True:
            if serial_port.in_waiting:
                id_received = serial_port.readline().decode().strip()
                mark_attendance_and_respond(id_received, roster, serial_port)
                roster.to_csv(roster_file, index=False)  # Save after each update
    except KeyboardInterrupt:
        print("Attendance recording stopped.")
    finally:
        serial_port.close()

@app.route('/')
def index():
    roster = pd.read_csv(roster_file)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    present_students = roster[roster[today] == True]['name'].tolist()
    attendance_count = len(present_students)
    recent_students = present_students[-5:]
    return render_template('index.html', count=attendance_count, recent_students=recent_students)

if __name__ == '__main__':
    # Start the serial thread
    serial_thread = Thread(target=handle_serial_communication, daemon=True)
    serial_thread.start()

    # Start the Flask app
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    app.run(debug=True)
