import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem.units import units
from dp_chem import molecule


AVOCADO = 6.02214076e23

def kjmol_jbond():

    kjmol = sf.random_value((200,700),(1,4))
    

    formatted_question = random.choice([
        f'A covalent bond has an energy of {kjmol.html} kJ/mol. Calculate the energy of a single bond in J.',
        f'Convert {kjmol.html} kJ/mol to J/bond.',
        f'A covalent bond has an energy of {kjmol.html} kJ mol<sup>-1</sup>. Calculate the energy of a single bond in J.',
        f'Convert {kjmol.html} kJ mol<sup>-1</sup> to J bond<sup>-1</sup>.'
    ])
    
    jbond = kjmol * 1000 / AVOCADO

    answer = jbond.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def jbond_kjmol():

    jbond = sf.random_value((3e-19,1e-18),(1,4))
    

    formatted_question = random.choice([
        f'A single covalent bond has an energy of {jbond.html} J. Calculate this bond energy in kJ/mol.',
        f'Convert {jbond.html} J/bond to kJ/mol.',
        f'A single covalent bond has an energy of {jbond.html} J. Calculate this bond energy in kJ mol<sup>-1</sup>.',
        f'Convert {jbond.html} J bond<sup>-1</sup> to kJ mol<sup>-1</sup>.'
    ])
    
    kjmol = jbond * AVOCADO / 1000

    answer = kjmol.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def jbond_calbond():
    jbond = sf.random_value((3e-19,1e-18),(1,3))

    formatted_question = random.choice([
        f'A single covalent bond has an energy of {jbond.html} J. Calculate this bond energy in cal.',
        f'Convert {jbond.html} J/bond to cal/bond.'
    ])
    formatted_question += "<br>There are 4.184 J in one cal."

    calbond = jbond/4.184
    answer = calbond.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def calbond_jbond():
    calbond = sf.random_value((1e-19,1e-18),(1,3))

    formatted_question = random.choice([
        f'A single covalent bond has an energy of {calbond.html} cal. Calculate this bond energy in J.',
        f'Convert {calbond.html} cal/bond to J/bond.'
    ])
    formatted_question += "<br>There are 4.184 J in one cal."

    jbond = calbond*4.184
    answer = jbond.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def kcalmol_kjmol():
    kcalmol = sf.random_value((200,700),(1,4))

    formatted_question = random.choice([
        f'A covalent bond has an energy of {kcalmol.html} kcal/mol. Calculate this bond energy in kJ/mol.',
        f'Convert {kcalmol.html} kcal/mol to kJ/mol.',
    ])
    formatted_question += "<br>There are 4.184 J in one cal."

    kjmol = kcalmol*4.184
    answer = kjmol.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def kjmol_kcalmol():
    kjmol = sf.random_value((200,700),(1,4))

    formatted_question = random.choice([
        f'A covalent bond has an energy of {kjmol.html} kJ/mol. Calculate this bond energy in kcal/mol.',
        f'Convert {kjmol.html} kJ/mol to kcal/mol.',
    ])
    formatted_question += "<br>There are 4.184 J in one cal."

    kcalmol = kjmol/4.184
    answer = kcalmol.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------


def generate_question():
    question_type = 'short_answer'

    question_options = [
        kjmol_jbond,
        jbond_kjmol,
        jbond_calbond,
        calbond_jbond,
        kcalmol_kjmol,
        kjmol_kcalmol
    ]

    func = random.choice(question_options)

    formatted_question, answer = func()

    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    #question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    #question_text = question_row.split(';')[0]
    #answer_equation = question_row.split(';')[1]

   # Get a dictionary of all local variables
    # namespace = locals()

    # # Replace placeholders in the question with the generated values
    # formatted_question = question_text.format(**namespace)

    # # Calculate the answer using the provided equation
    # answer = eval(answer_equation, globals(), namespace)

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
