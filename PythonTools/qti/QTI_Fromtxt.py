# this program is good for numeric questions involving elements [or compounds (not developed yet)]
# use banks/Template_Blank.txt to generate

import hashlib
import pandas as pd
import random
import csv
import tkinter as tk
from tkinter import filedialog

from makeqti import *
from periodictable import periodictable
from uncertainvalue import uncertainvalue as uv
from sigfig import sigfig

def generate_questions(input_csv):
    input_data = parse_input_file(input_csv)
    basename = input_data['basename']
    num_questions = input_data['num_questions']
    question_type = input_data['question_type']
    sigfig_vars = input_data['sigfig_vars']
    sigfig_var_ranges = input_data['sigfig_var_ranges']
    int_vars = input_data['int_vars']
    int_var_ranges = input_data['int_var_ranges']
    sigfig_nsigfig_ranges = input_data['sigfig_nsigfig_ranges']
    periodictable_vars = input_data['periodictable_vars']
    periodictable_weighted = input_data['periodictable_weighted']
    question_data = input_data['question_data']

    print(f"generating {num_questions} questions for question bank {basename}")

    questions = []
    pt = periodictable()
    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for _ in range(num_questions):
        # Randomly select a question and its corresponding equation
        question_row = random.choice(question_data) if len(question_data) > 1 else question_data[0]
        question_text = question_row['question_text']
        answer_equation = question_row['answer_equation']

        # Randomly select an element
        element = pt.random(weighted=periodictable_weighted)
        element_info = {var: element[var] for var in periodictable_vars}

        values={}
        # Generate random values for variables
        for var, var_rng, sf_rng in zip(sigfig_vars, sigfig_var_ranges, sigfig_nsigfig_ranges):
            values[var] = sigfig(sigfig(str(random.uniform(var_rng[0], var_rng[1])), random.randint(sf_rng[0], sf_rng[1])).scientific_notation())
        for var, var_rng in zip(int_vars, int_var_ranges):
            values[var] = random.randint(var_rng[0],var_rng[1])

        # Replace placeholders in the question with the generated values
        formatted_question = question_text.format(**element_info, **values)
        
        # Calculate the answer using the provided equation
        namespace = {**element_info, **values}
        answer = eval(answer_equation.format(**namespace), {'__builtins__': None}, namespace)
        correct_answers = answer.answers()

        questions.append({
            'question': formatted_question,
            'correct_answers': correct_answers,
            'question_type': question_type
        })

    questions_df = pd.DataFrame(questions)
    return questions_df, basename,assessment_ident


def parse_input_file(input_file):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        headers = {}
        question_data = []

        found_header=False
        for row in reader:
            if not row or not row[0].strip():
                # Skip empty lines
                continue

            if not found_header:
                if row[0].startswith("#"):
                    key, value = row[0][1:].strip(), row[1].strip()
                    headers[key] = value
                else:
                    found_header = True
            else:
                question_text, answer_equation = row
                question_data.append({'question_text': question_text, 'answer_equation': answer_equation})

        periodictable_vars = headers.get('periodictable_vars', '').split(';') if 'periodictable_vars' in headers else []
    periodictable_weighted = headers.get('periodictable_weighted', '').split(';') if 'periodictable_weighted' in headers else []
    sigfig_vars = headers.get('sigfig_vars', '').split(';') if 'sigfig_vars' in headers else []
    sigfig_var_ranges = [tuple(map(float, r.split(':'))) for r in headers.get('sigfig_var_ranges', '').split(';')] if 'sigfig_var_ranges' in headers else []
    sigfig_nsigfig_ranges = [tuple(map(int, r.split(':'))) for r in headers.get('sigfig_nsigfig_ranges', '').split(';')] if 'sigfig_nsigfig_ranges' in headers else []
    int_vars = headers.get('int_vars', '').split(';') if 'int_vars' in headers else []
    int_var_ranges = [tuple(r.split(':')) for r in headers.get('int_var_ranges', '').split(';')] if 'int_var_ranges' in headers else []

    input_data = {
        'basename': headers['basename'],
        'num_questions': int(headers['num_questions']),
        'question_type': headers['question_type'],
        'sigfig_vars': sigfig_vars,
        'sigfig_nsigfig_ranges': sigfig_nsigfig_ranges,
        'sigfig_var_ranges':sigfig_var_ranges,
        'int_vars': int_vars,
        'int_var_ranges': int_var_ranges,
        'periodictable_vars': periodictable_vars,
        'periodictable_weighted':periodictable_weighted,
        'question_data': question_data
    }

    return input_data


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Open a file dialog to let the user select the input file
    input_file = filedialog.askopenfilename(title="Select the input txt file", filetypes=[("text files", "*.txt")])

    if not input_file:
        print("No file selected. Exiting.")
        return

    questions_df, basename, assessment_ident = generate_questions(input_file)
    output_zip = f'banks\{basename}.zip'
    qti_xml = create_qti_xml(questions_df, basename, assessment_ident)
    save_to_zip(qti_xml, output_zip)
    return

if __name__ == "__main__":
    main()