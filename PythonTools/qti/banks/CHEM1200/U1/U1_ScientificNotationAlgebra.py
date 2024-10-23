# still to do:
# 1) limit sigfig of conv_value
# 2) switch to numerical with tolerance


import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sigfig as sf
from dp_chem.units import units


def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        '{question};nt_answer'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here


    operator = random.choice(['mult','div'])
    
    while True:
        if operator == 'mult':
            x = sf.random_value((1e-9,1e9),(2,3),True)
            y = sf.random_value((1e-9,1e9),(2,3),True)
            answer = x*y
            question = f'{x.html} × {y.html} ='
        elif operator == 'div':
            x = sf.random_value((1e-9,1e9),(2,3),True)
            y = sf.random_value((1e-9,1e9),(2,3),True)
            answer = x/y
            question = create_mattext_element('\\frac{'+ x.tex +'}{'+ y.tex +'}=')
        else:
            raise ValueError(f'operator has bad value: {operator}')
            
        nt_answer = f'{answer.value:.5g};{answer.value * 0.005:.5g}'
        if answer.value > 1e-2:
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
