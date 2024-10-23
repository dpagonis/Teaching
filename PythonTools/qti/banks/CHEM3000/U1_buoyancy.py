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
        'Calculate the true mass of a sample whose density is {dens} g cm-3 and whose displayed mass is {mass_d} g<br>{dw_html} = 7.99 g cm-3<br>T = {temp} K<br>P = {pres} mbar<br>{da_html} = 0.0011839 g cm-3 at 298 K, 1 bar;mass.answers()'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    i = 0
    
    dens = sf.random_value((0.7,4),(2,4))
    mass_d = sf.random_value((1,5),(5,5))
    dw = sf('7.99')
    da_std = sf('0.0011839')
    temp = sf.random_value((293,300),(3,3))
    pres = sf.random_value((700,1200),(3,4))

    da = da_std * (pres/1000) * (298/temp)

    mass = mass_d * (1-da/dw) / (1-da/dens)

    dw_html = create_mattext_element('d_w')
    da_html = create_mattext_element('d_a')


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
