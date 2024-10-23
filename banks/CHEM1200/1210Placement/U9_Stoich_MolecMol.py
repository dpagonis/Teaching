import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti.periodictable import periodictable

PT = periodictable()

def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        'How many moles are in {N_fmt} atoms of {name}?;answer_n',
        'A sample of {name} has {N_fmt} atoms. How many moles of {name} are in the sample?;answer_n',
        'How many atoms are in {n_fmt} moles of {name}?;answer_N',
        'A sample containes {n_fmt} moles of a compound. How many atoms are present in the sample?;answer_N'
    ]

    while True:
        element = PT.random(weighted=True)
        name = element['name']
        if not (element['atomic_number'] in [1,7,8,9,17,35,53,85,117]): # no diatomics to avoid confusion
            break
    
    N = sf.random_value((1e20,1e26),(2,4),True,'molecules')
    n = N.convert_to('mol')

    N_fmt = str(N)
    if 'e' in str(N):
        base, exponent = N_fmt.split('e')
        exponent = exponent.replace('+', '')  # Remove the plus sign if it exists
        N_fmt = f'{base}x10<sup>{exponent}</sup>'

    n_fmt = str(n)
    if 'e' in str(n):
        base, exponent = n_fmt.split('e')
        exponent = exponent.replace('+', '')  # Remove the plus sign if it exists
        n_fmt = f'{base}x10<sup>{exponent}</sup>'
        
    tol_n = 2*10**(n.last_decimal_place)
    answer_n = f'{n};{tol_n}'
    tol_N = 2*10**(N.last_decimal_place)
    answer_N = f'{N};{tol_N}'

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
