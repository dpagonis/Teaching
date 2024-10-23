# still to do:
# 1) limit sigfig of conv_value
# 2) switch to numerical with tolerance


import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem.units import units


def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        'Convert {v1_str} {u1} to {u2}. There are {conv_factor} {usmall} in one {ularge}.;answer',
    ]


    unit_categories = {
            'distance': ['m', 'ft',  'mi'],
            'time': ['s', 'min', 'hr', 'day'],
            'mass': ['g', 'lb', 'oz'],
            'volume': ['L', 'gal'],
            'energy': ['J','cal'],
            'pressure': ['Pa','bar','mmHg','Torr','atm','psi'],
        }
    
    
    
    while True: #numerical value questions can't handle answers below 1e-4
        category = random.choice(list(unit_categories.keys()))

        u1,u2 = random.sample(unit_categories[category],2)
        v1 = sf.random_value((1e-3,1e3),(3,5),value_log=True,units_str=u1)
        v2 = v1.convert_to(u2)

        if 'e' in str(v1):
            base, exp = v1.scientific_notation().split('e')
            v1_str = f'{base} x 10<sup>{exp}</sup>'
        else:
            v1_str = str(v1)
        
        conv_factor = units(u1).to_si_factor / units(u2).to_si_factor
        if conv_factor > 1:
            usmall = u2
            ularge = u1
        else:
            usmall = u1
            ularge = u2
            conv_factor = 1/conv_factor
        conv_factor = sf(f'{conv_factor:.5g}')
        
        answer = f'{v2.value:.5g};{v2.value * 0.005:.5g}'
        if v2.value > 1e-2:
            break

    
    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    question_text = question_row.split(';')[0]
    answer_equation = question_row.split(';')[1]

   # Get a dictionary of all local variables
    namespace = locals()

    # Replace placeholders in the question with the generated values
    formatted_question = question_text.format(**namespace)

    # Calculate the answer using the provided equation
    answer = eval(answer_equation, globals(), namespace)

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'question_type': question_type
    }

def generate_questions():
    num_questions = 1000
    basename = os.path.basename(__file__).removesuffix('.py')
    
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for _ in range(num_questions):
        question = generate_question()
        questions.append(question)

    questions_df = pd.DataFrame(questions)
    return questions_df, basename, assessment_ident

def yes_no(bool):
    if bool:
        return "Yes;yes;Y;y"
    else:
        return "No;no;N;n"

def main():
    questions_df, basename, assessment_ident = generate_questions()
    output_zip = f'{basename}.zip'
    qti_xml = create_qti_xml(questions_df, basename, assessment_ident)
    manifest_xml = create_manifest_xml(assessment_ident,basename)
    save_xml_to_zip(qti_xml,assessment_ident,manifest_xml, output_zip)
    output_csv = f'{basename}.csv'
    questions_df.to_csv(output_csv, index=False)
    return

if __name__ == "__main__":
    main()
