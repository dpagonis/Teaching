import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import molecule


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the ionic strength of a {F} M solution of {tex_html};mu.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    F = sf.random_value((0.05,0.2),(1,3))

    cation = molecule(random.choice(['Na+','K+','Mg++']))
    anion = molecule(random.choice(['Cl-','NO3-','SO4--','PO4---']))

    if cation.charge == -1*anion.charge:
        salt = molecule(cation.formula+anion.formula)
        coef_anion = 1
        coef_cation = 1
        salttex = salt.tex
    else:
        coef_anion = cation.charge
        coef_cation = abs(anion.charge)
        cation_nocharge=molecule(cation.formula) #formula is elements only
        anion_nocharge=molecule(anion.formula)
        salttex = f'({cation_nocharge.tex})_{coef_cation}' if coef_cation > 1 else cation_nocharge.tex
        salttex += f'({anion_nocharge.tex})_{coef_anion}' if coef_anion > 1 else anion_nocharge.tex

    mu = 0.5*(F*coef_cation*cation.charge**2+F*coef_anion*anion.charge**2)
    tex_html = create_mattext_element(salttex)

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
