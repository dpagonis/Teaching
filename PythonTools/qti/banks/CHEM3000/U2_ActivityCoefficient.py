import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule

cations = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/cations.csv')
anions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/anions.csv')

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the activity coefficient for {name} in a solution with an ionic strength of {mu} M. The hydrated radius of {tex_html} is {alpha} pm.;gamma.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    mu = sf.random_value((0.001,0.1),(1,3),value_log=True)

    if random.random() > 0.5: #even odds cation or anion
        row=cations[cations['hydrated_radius_pm']>0].sample(1) #filter out ions with no radius entered
    else:
        row=anions[anions['hydrated_radius_pm']>0].sample(1)
    
    ion = molecule(row['formula'].values[0])
    name = row['Name'].values[0].lower()
    tex_html = create_mattext_element(row['tex'].values[0])

    alpha = row['hydrated_radius_pm'].values[0]
    z = ion.charge

    loggamma = -0.51*z**2 * mu**0.5 / (1+alpha*mu**0.5/305)
    gamma = loggamma.exponent(10)

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
