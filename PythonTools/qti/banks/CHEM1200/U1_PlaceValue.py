import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf



def generate_question():
    question_type = 'short_answer'

    question_options = [
        'What digit is in the {pv} place of the following number: {num};digit'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    n = sf.random_value((10_000,99_999),(8,8))
    num = n.as_num()

    pvs = {
        'ones': 0,
        'tens': 1,
        'hundreds': 2,
        'thousands': 3,
        'ten thousands': 4,
        'tenths': -1,
        'hundredths': -2,
        'thousandths': -3
    }

    pv = random.choice(list(pvs.keys()))

    decimal_index = num.find('.') if '.' in num else len(num)

    if pvs[pv] >=0:
        target_index = decimal_index - pvs[pv] -1
    else:
        target_index = decimal_index - pvs[pv]

    # Handle cases where the target index is out of bounds
    if target_index < 0 or target_index >= len(num) or num[target_index] == '.':
        print('index out of bounds', num, pv, decimal_index, target_index)
    
    digit = num[target_index] 

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
