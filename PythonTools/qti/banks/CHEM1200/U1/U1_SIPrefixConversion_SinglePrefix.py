import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf

from random import randint


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Convert {v1_str} {unit} to {prefix}{unit};v2.answers()',
        'Convert {v2_str} {prefix}{unit} to {unit};v1.answers()'
    ]


    prefix_pool = ['c','m','µ','n','k','M','G']
    units_pool = ['m', 'ft', 'mi', 's', 'min', 'h', 'day','g', 'lb', 'oz', 'L', 'gal', 'J','cal','Pa','bar']


    unit = random.choice(units_pool)
    prefix = random.choice(prefix_pool)

    power = random.randint(-3,3)

    v1 = sf(f'1e{power}',sig_figs=1,units_str=unit)
    v2 = v1.convert_to((prefix+unit))
    v2 = sf(v2.scientific_notation(),sig_figs=1)

    v1_str = str(v1)
    if 'e' in str(v1):
        base, exp = v1.scientific_notation().split('e')
        v1_str = f'{base} x 10<sup>{exp}</sup>'

    if 'e' in str(v2):
        base, exp = v2.scientific_notation().split('e')
        v2_str = f'{base} x 10<sup>{exp}</sup>'
    else:
        v2_str = str(v2)


    

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
