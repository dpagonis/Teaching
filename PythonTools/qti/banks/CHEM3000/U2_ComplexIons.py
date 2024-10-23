import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import molecule

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/formationconstants.csv')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the concentration of {complex_html} (in M) in a saturated solution of {salt_html} given:<br>pH = {pH}<br>{beta_html}<br>{Ksp_html};c_complex.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    pH = sf.random_value((7,12),(2,3))

    row=reactions[(reactions['ligand']=='OH-') & (reactions['pKsp']>0)].sample(1) #OH- reactions with a pKsp listed
    metal = molecule(row['metal'].values[0])
    n_ligand = row['n_ligand'].values[0]
    log_b = sf(str(row['log_b'].values[0]))
    pKsp = sf(str(row['pKsp'].values[0]))

    c_OH = (-1*(14-pH)).exponent(10)
    
    Ksp = (-1*pKsp).exponent(10)
    c_metal = Ksp/(c_OH**metal.charge)

    beta=log_b.exponent(10)

    c_complex = beta * c_metal * c_OH**n_ligand
    
    salt=molecule(metal.formula+'(OH)'+str(metal.charge),charge=0)
    salt_html = create_mattext_element(salt.tex)

    complex = molecule(metal.formula+('OH' if n_ligand == 1 else '(OH)'+str(n_ligand)),charge=metal.charge-n_ligand)
    complex_html = create_mattext_element(complex.tex)

    beta_html = create_mattext_element(f'log(\\beta_{n_ligand})={log_b}')
    Ksp_html = create_mattext_element(f'pK_{{sp,{salt.formula}}}={pKsp}')

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
