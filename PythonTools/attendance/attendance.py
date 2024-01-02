import serial
import serial.tools.list_ports
import pandas as pd
import datetime

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


# Load the class roster
roster_file = 'classroster.csv'
roster = pd.read_csv(roster_file)

# Ensure 'id' column is string for comparison
roster['id'] = roster['id'].astype(str)

# Find and connect to the active COM port
serial_port = find_active_com_port()
if not serial_port:
    print("No active COM port found. Please check the connection.")
else:
    print(f"Connected to {serial_port.port}")

    try:
        while True:
            if serial_port.in_waiting:
                id_received = serial_port.readline().decode().strip()
                mark_attendance_and_respond(id_received, roster, serial_port)
                roster.to_csv(roster_file, index=False)  # Save after each update
    except KeyboardInterrupt:
        roster.to_csv(roster_file, index=False)  # Save after each update
        print("Attendance recording stopped.")

    serial_port.close()
