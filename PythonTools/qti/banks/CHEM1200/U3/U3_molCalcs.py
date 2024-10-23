
import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import molecule
from dp_chem import periodictable

PT = periodictable.periodictable()


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Convert {N.html} {type} {molec.simple_html} to mol {molec.simple_html}.;n_answer_list',
        'Convert {n} mol {molec.simple_html} to {type} {molec.simple_html}.;N_answer_list'
    ]

    ions = ['CO3--','SO4--','Na+','Cl-','Li+','K+','F-','Br-','NO3-','ClO4-','PO4---','NH4+']
    molecules = ['CO2','H2O','O2','N2','Cl2','H2','NO','NO2','O3','HNO3','HCl','N2O','NH3']

    type = random.choice(['ions','molecules','atoms'])

    if type == 'atoms':
        molec = molecule(PT.random(weighted=True)['symbol'])
    elif type == 'ions':
        molec = molecule(random.choice(ions))
    elif type == 'molecules':
        molec = molecule(random.choice(molecules))
    while True:
        n = sf.random_value((1e-3,100),(1,4),True,units_str='mol')
        N = sf(str(n.convert_to('molec')),sig_figs=n.sig_figs)
        n_calc = (sf(N.scientific_notation(),units_str='molec')).convert_to('mol')
        n_check = n_calc.scientific_notation() == n.scientific_notation()
        if n_check:
            break

    n_answer_list = n.answers(sf_tolerance=1,roundoff_tolerance=True)
    N_answer_list = N.answers(sf_tolerance=1,roundoff_tolerance=True)

    
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
