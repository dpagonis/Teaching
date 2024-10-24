import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable

from random import randint

PT = periodictable.periodictable()

def generate_question():
    question_type = 'short_answer'

    #list of strings
    #each string is semicolon-separated: "question text; answers"
    question_options = [
        'What is the charge of {a_an} {element_name} atom with {n_e} electrons?;charge_answers',
        'How many electrons does {a_an} {element_name} atom have if its charge is {sign}{abs_charge}?;n_e',
        'How many electrons are in {a_an} {ion_symbol} atom?;n_e',
        'How many protons are in {a_an} {ion_symbol} atom?;atomic_number',
        '{a_an_upper} {element_name} atom has a charge of {sign}{abs_charge}. How many electrons are in the atom?;n_e',
        'An atom of {element_name} has {n_e} electrons. What is its charge?;charge_answers'
    ]


    e = PT.random(weighted=True)

    
    element_name = e['name']
    a_an = 'an' if element_name[0].lower() in 'aeiou' else 'a'
    a_an_upper = a_an[0].upper() + a_an[1:]

    atomic_number = e['atomic_number']
    
    min_e = atomic_number-3
    if min_e < 0:
        min_e = 0
    max_e = atomic_number + 3

    n_e = randint(min_e,max_e)
    charge = int(atomic_number - n_e)

    symbol = e['symbol']
    

    # Generate the charge_answers string
    abs_charge = abs(charge)
    if charge == 0:
        sign = ''
        charge_answers = '0'
    elif charge > 0:
        sign = '+'    
        charge_answers = f"{sign}{abs_charge};{sign} {abs_charge};{abs_charge}{sign};{abs_charge} {sign};{abs_charge}"
    else:
        sign = '-'
        charge_answers = f"{sign}{abs_charge};{sign} {abs_charge};{abs_charge}{sign};{abs_charge} {sign}"
    
    ion_symbol = f'{symbol}<sup>{abs_charge}{sign}</sup>'

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
