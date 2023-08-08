import hashlib
import pandas as pd
import random
import os
from math import gcd

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/ksp.csv')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the solubility of {salt_html} (in M).<br>{pKsp_html};s.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    row=reactions.sample(1)
    
    cation = molecule(row['cation'].values[0])
    anion = molecule(row['anion'].values[0])
    salt = molecule(row['formula'].values[0])
    pKsp = sf(str(row['pKsp'].values[0]))

    Ksp = (-1*pKsp).exponent(10)



    # Assuming cation.charge and anion.charge are integers
    gcd_value = gcd(abs(cation.charge), abs(anion.charge))
    n_cat = abs(anion.charge) // gcd_value
    n_an = abs(cation.charge) // gcd_value

    # K_sp = mult * s^exp...... eg s^2 4s^3 etc
    exp_term = n_cat+n_an
    mult_term = n_cat**n_cat * n_an**n_an 

    s = (Ksp / (mult_term))**(1/exp_term)

    salt_html = create_mattext_element(salt.tex)

    pKsp_html = create_mattext_element(f'pK_{{sp,{salt.formula}}}={pKsp}')

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
