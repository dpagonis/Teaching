import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti.units import units


def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        'Convert {area} {u1}<sup>2</sup> to {u2}<sup>2</sup>. There are {conv_factor} {u1} in one {u2}.;answer',
        'Rewrite {area} {u1}<sup>2</sup> in units of {u2}<sup>2</sup>, given that there are {conv_factor} {u1} per {u2}.;answer',
        'A square has an area of {area} {u1}<sup>2</sup>. There are {conv_factor} {u1} in one {u2}. What is the area of the square in {u2}<sup>2</sup>?;answer',
        'Convert the following to {u2}<sup>2</sup>: {area} {u1}<sup>2</sup><br>There are {conv_factor} {u1} in one {u2}.;answer'
    ]

    pairs = [
        ('cm','in'),
        ('m','mi'),
        ('mm','ft')
    ]

    u1,u2 = random.choice(pairs)

    conv_factor = units(u2).to_si_factor / units(u1).to_si_factor

    area_1 = sf.random_value((1e5,1e8),(2,3),True,u1+'2')
    
    if 'e' in str(area_1):
        base, exponent = str(area_1).split('e')
        exponent = exponent.replace('+', '')  # Remove the plus sign if it exists
        area = f'{base}x10<sup>{exponent}</sup>'
    else:
        area = str(area_1)
    area_2=area_1.convert_to(u2+'2')
    answer = f'{area_2};{2*10**area_2.last_decimal_place}'
    
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
