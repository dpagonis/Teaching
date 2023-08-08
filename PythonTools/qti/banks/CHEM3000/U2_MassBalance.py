import hashlib
import pandas as pd
import random
import os
from itertools import permutations

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import weakacid

weakacids = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/weakacidbases.csv')
weakacids['pKa'] = weakacids['pKa'].apply(lambda x: [i for i in x.split(';')])

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Write the mass balance for a {F} M solution of {name}<br>{rxn_html};all_mbal_str'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    F = sf.random_value((0.001,0.1),(1,3),value_log=True)
    
    row=weakacids.sample(1)
    name = row['name'].values[0]
    acid = weakacid(row['formula_neutral'].values[0],row['pKa'].values[0],n_H_neutral=row['N_acidic_proton_neutral'].values[0])
    forms = acid.forms
    rxn_tex = "\leftrightarrow{}".join(str(form.tex) for form in forms)
    rxn_html=create_mattext_element(rxn_tex)


    forms_perm = list(permutations(list('['+str(f)+']' for f in forms)))
    all_mbal = [f"{F}={'+'.join(perm)}" for perm in forms_perm]
    all_mbal_str = ';'.join(all_mbal)

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
