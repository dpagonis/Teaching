import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule



def generate_question():
    question_type = 'short_answer'

    question_options = [
    'To find the {cation_element} content of a solid, {mass_sample} g of sample were dissolved and treated with excess {halogen} to precipitate {salt_html}. The precipitate was collected, washed, dried, and weighed, giving a mass of {mass_salt} g. What was the mass fraction of {ion_html} in the original solid?<br>Formula mass {salt_html} = {mw_salt} g mol-1<br>Formula mass {cation_element} = {mw_cation} g mol-1;mass_frac.answers()']

    # generating random values for variables, doing calculations, & prepping namespace here
    ksp_table = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/ksp.csv')
    row = ksp_table.sample(n=1)

    cation_element = row['cation_element'].values[0]
    halogen = row['anion_name'].values[0]
    salt_html = create_mattext_element(row['tex'].values[0])
    ion_html = create_mattext_element(row['cation_tex'].values[0])

    mass_salt=sf(str(random.uniform(0.5,3)),last_decimal_place=-4)                      
    
    mw_salt = molecule(row['formula'].values[0]).molecular_weight
    mw_cation = molecule(row['cation_element'].values[0]).molecular_weight

    mass_cation = mass_salt/mw_salt * mw_cation

    mass_sample = sf(str(mass_cation/random.uniform(0.1,0.7)),last_decimal_place=-4)

    mass_frac = mass_cation/mass_sample

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
