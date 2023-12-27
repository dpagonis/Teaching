import csv

# Read the course ID from the configuration file
with open("COURSE_ID.txt", "r") as file:
    COURSE_ID = file.readline().strip()

# Input and Output Filenames
INPUT_FILENAME = "C:/Users/demetriospagonis/Downloads/2023-10-11T1438_Grades-CHEM_3000_WSU_Fall_2023_22673.csv"
STUDENTS_FILENAME = f"course_{COURSE_ID}_students.csv"
ASSIGNMENTS_FILENAME = f"course_{COURSE_ID}_assignments.csv"


def extract_data_from_gradebook(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # For storing student and assignment data
        students = set()
        assignments = set()

        # Extract headers
        headers = reader.fieldnames

        # Extract student names and IDs
        for row in reader:
            if row["ID"] and row["Student"] != "Student, Test":  # Check if the ID exists and exclude "Student, Test"
                last, first = row["Student"].split(", ")
                formatted_name = f"{first} {last}"
                students.add((formatted_name, row["ID"]))


        # Extract assignment names and IDs
        for header in headers:
            if "(" in header and ")" in header:
                name, id = header.rsplit(" (", 1)
                id = id.rstrip(")")
                assignments.add((name, id))
        
        return students, assignments

def write_to_csv(filename, data, headers):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    students, assignments = extract_data_from_gradebook(INPUT_FILENAME)
    write_to_csv(STUDENTS_FILENAME, students, ["Student", "ID"])
    write_to_csv(ASSIGNMENTS_FILENAME, assignments, ["Assignment", "ID"])
