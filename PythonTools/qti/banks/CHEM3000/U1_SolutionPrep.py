import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf

def generate_questions():
    num_questions = 1000
    basename = os.path.basename(__file__).rstrip('.py') #this string is used to name the bank and the hash ID
    
    
    #####------------Rest of this function stays constant, move to generate_question()--------#####
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for _ in range(num_questions):
        question = generate_question()
        questions.append(question)

    questions_df = pd.DataFrame(questions)
    return questions_df, basename, assessment_ident

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Concentrated {name} has a concentration of {conc_i} M. Calculate the volume of {formula_tex_html} (in mL) needed to prepare a {conc_f} M solution using a {v_flask} L volumetric flask.;v_acid.answers()'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    df = pd.read_csv('U1_SolutionPrep.txt')
    row = df.sample(n=1)

    # Assign the values to your variables
    name = row['name'].values[0]
    conc_i = row['conc_init'].values[0]
    formula_tex = row['formula_tex'].values[0]

    v_flask = sf('1.000')
    conc_f = sf.random_value((0.0011*conc_i,0.1*conc_i),(3,3))
    v_acid = 1000 * conc_f * v_flask / conc_i

    formula_tex_html = create_mattext_element(formula_tex)



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
