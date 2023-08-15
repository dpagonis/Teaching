import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the free energy (in kJ mol-1) for the following galvanic cell.<br>Eo = {Eo} V<br>n = {n_E}<br>T = {T_K} K;dG_kJmol.answers(sf_tolerance=1)',
        'Calculate the equilibrium constant for the following galvanic cell.<br>Eo = {Eo} V<br>n = {n_E}<br>T = {T_K} K;K.answers(sf_tolerance=1)',
        'Calculate the reaction potential (in V) for the following galvanic cell.<br>dG = {dG_kJmol} kJ mol-1<br>n = {n_E}<br>T = {T_K} K;Eo.answers(sf_tolerance=1)',
        'Calculate the reaction potential (in V) for the following galvanic cell.<br>K = {K}<br>n = {n_E}<br>T = {T_K} K;Eo.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    F = 96486
    R = 8.3145

    while True:
        Eo = sf.random_value((-1,3),(2,4))
        n_E = random.randint(1,3)
        T_K = sf.random_value((280,305),(3,4))
        
        dG_Jmol = -1*n_E*F*Eo
        dG_kJmol = dG_Jmol/1000

        K = (-1*dG_Jmol/(R*T_K)).exponent()

        E_from_G = sf(str((dG_kJmol*1000)/(-1*n_E*F)))
        E_from_K = sf(str(R*T_K*K.ln()/(n_E*F)))

        if (E_from_G.scientific_notation() == Eo.scientific_notation()) and (E_from_K.scientific_notation() == Eo.scientific_notation() ):
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
