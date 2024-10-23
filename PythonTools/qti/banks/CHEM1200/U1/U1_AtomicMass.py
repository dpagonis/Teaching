import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sigfig as sf
from dp_chem import periodictable

PT = periodictable()

def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        'An element has the following isotopes at the given abundances. Calculate the atomic mass of the element.<br>{isotope_table};answer'
    ]

    n_isotopes = random.randint(2,3)
    main_isotope = random.randint(10,100)
    
    percent_allocated = 0
    atomic_mass = 0
    isotope_table = 'Isotope mass (u)  :  Abundance (%)'
    for i in range(n_isotopes):
        if i == 0:
            abundance = sf.random_value((10,90),(3,3))
        elif i == n_isotopes-1:
            abundance = 100-percent_allocated
        else:
            max_a = 98-percent_allocated
            abundance = sf.random_value((1,max_a.value),(3,3))
        mass = sf.random_value((main_isotope+i-0.05,main_isotope+i+0.1),(4,4))
        atomic_mass += abundance/100 * mass
        percent_allocated += abundance
        isotope_table += f'<br>{mass}  :  {abundance}%'
    
    answer = f'{atomic_mass.value};{atomic_mass.value * 0.001}'

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
