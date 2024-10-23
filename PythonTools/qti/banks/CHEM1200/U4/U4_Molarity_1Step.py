import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable
from dp_chem import molecule
from dp_chem import sf

COMPOUNDS = [
    'NaCl', 'KNO3', 'NH4Br', 'NaNO3', 'KCl', 'Na2SO4', 'NH4Cl', 'Mg(NO3)2', 'CaCl2',
    'Na3PO4', 'K2CO3', 'Na2CO3', 'NaClO4', 'KClO4', 'Fe(NO3)2', 'Fe(NO3)3', 'AgNO3',
    'Pb(NO3)2', 'Co(NO3)2', 'Ba(NO3)2'
    ]

def calc_M():
    
    n = sf.random_value((1e-3,1),(1,3),value_log=True)
    V = sf.random_value((n.value/5,n.value/1e-3),(1,3),value_log=True, units_str='L')

    c=molecule(random.choice(COMPOUNDS))

    formatted_question = random.choice([
        f'Calculate the concentration of a solution (in M) prepared by dissolving {n.html} moles of {c.simple_html} in {V.convert_to("mL").html} mL of water',
        f'Calculate the concentration of a solution (in M) prepared by dissolving {n.html} moles of {c.simple_html} in {V.html} L of water',
        f'Calculate the molarity of a solution prepared from {n.html} moles of {c.simple_html} and {V.convert_to("mL").html} mL of water',
        f'Calculate the molarity of a solution prepared from {n.html} moles of {c.simple_html} and {V.html} L of water',
        f'Calculate the molarity of a solution prepared from {V.convert_to("mL").html} mL of water and {n.html} moles of {c.simple_html}',
        f'Calculate the concentration of a solution (in M) prepared from {V.html} L of water and {n.html} moles of {c.simple_html}',
        f'Calculate the molarity of a solution prepared from {n.html} moles of solute and {V.html} L of water',
        f'Calculate the molarity of a solution prepared from {V.convert_to("mL").html} mL of water and {n.html} moles of solute'
    ])
    
    answer = n/V
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_V():
    
    n = sf.random_value((1e-3,1),(1,3),value_log=True)
    M = sf.random_value((1e-3,5),(1,3),value_log=True)

    c=molecule(random.choice(COMPOUNDS))

    answer_unit = random.choice(['L','mL'])

    formatted_question = random.choice([
        f'What is the volume of a solution (in {answer_unit}) if it contains {n.html} moles of {c.simple_html} and has a concentration of {M.html} M',
        f'What is the volume of a solution (in {answer_unit}) if it contains {n.html} moles of {c.simple_html} and has a concentration of {M.html} mol L<sup>-1</sup>',
        f'A {M.html} M solution of {c.simple_html} contains {n.html} moles of {c.simple_html}. What is the solution volume, in {answer_unit}?',
        f'A {M.html} mol/L solution of {c.simple_html} contains {n.html} moles of {c.simple_html}. What is the solution volume, in {answer_unit}?',
        f'What is the volume (in {answer_unit}) of a {M.html} M solution of {c.simple_html} if it contains {n.html} moles of solute?'
    ])
    
    V = n/M
    V_L = sf(str(V.value),sig_figs=V.sig_figs,units_str='L')

    answer = V_L.convert_to(answer_unit)
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_n():
    
    V = sf.random_value((0.01,1),(1,3),units_str='L')
    M = sf.random_value((1e-3,5),(1,3),value_log=True)

    c=molecule(random.choice(COMPOUNDS))

    formatted_question = random.choice([
        f'How many moles of solute are in a {V.html} L of a {M.html} M solution of {c.simple_html}?',
        f'How many moles of solute are in a {V.convert_to("mL").html} mL of a {M.html} M solution of {c.simple_html}?',
        f'A {M}.html M solution of {c.simple_html} has a volume of {V.html} L. How many moles of solute are in the solution?',
        f'A {M.html} M solution of {c.simple_html} has a volume of {V.convert_to("mL").html} mL. How many moles of solute are in the solution?',
    ])
    
    answer = M * V
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)


#---------------------------------------------------------------------
def generate_question():
    question_type = 'short_answer'

    question_options = [
        calc_M,
        calc_V,
        calc_n
    ]

    func = random.choice(question_options)
    formatted_question, answer = func()

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
