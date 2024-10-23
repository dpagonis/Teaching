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
    
    m = sf.random_value((1,10),(1,4))
    V = sf.random_value((0.1,1),(1,4),value_log=True, units_str='L')

    c=molecule(random.choice(COMPOUNDS))

    n = m/c.molecular_weight
    M = n/V

    formatted_question = random.choice([
        f'Calculate the concentration (in M) of a solution prepared by dissolving {m.html} g of {c.simple_html} in {V.html} L of water.',
        f'Calculate the concentration (in M) of a solution prepared by dissolving {m.html} g of {c.simple_html} in {V.convert_to("mL").html} mL of water.',
        f'A student dissolves {m.html} g of {c.simple_html} in {V.html} L of water. What is the molarity of this solution?',
        f'A student dissolves {m.html} g of {c.simple_html} in {V.convert_to("mL").html} mL of water. What is the molarity of this solution?',
        f'A student prepares a {V.html} L solution by dissolving {m.html} g of {c.simple_html} in water. What is the molarity of this solution?',
        f'A student prepares a {V.convert_to("mL").html} mL solution by dissolving {m.html} g of {c.simple_html} in water. What is the molarity of this solution?'
    ])
    
    answer = M
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_m():
    
    M = sf.random_value((1e-3,1),(1,4),value_log=True)
    V = sf.random_value((0.1,1),(1,4),value_log=True, units_str='L')

    c=molecule(random.choice(COMPOUNDS))

    n = M*V
    m = n*c.molecular_weight

    formatted_question = random.choice([
        f'Calculate the mass of {c.simple_html} (in g) needed to prepare a {V.html} L solution with a concentration of {M.html} M.',
        f'Calculate the mass of {c.simple_html} (in g) needed to prepare a {V.convert_to("mL").html} mL solution with a concentration of {M.html} M.',
        f'Calculate the mass of {c.simple_html} (in g) needed to prepare a {M.html} M solution with a volume of {V.html} L.',
        f'Calculate the mass of {c.simple_html} (in g) needed to prepare a {M.html} M solution with a volume of {V.convert_to("mL").html} mL.',
        f'A student prepares a {V.html} L, {M.html} M solution of {c.simple_html} in water. How many grams of {c.simple_html} did they dissolve?',
        f'A student prepares a {V.convert_to("mL").html} mL, {M.html} M solution of {c.simple_html} in water. How many grams of {c.simple_html} did they dissolve?',
        f'A student prepares a {M.html} M, {V.html} L solution of {c.simple_html} in water. How many grams of {c.simple_html} did they dissolve?',
        f'A student prepares a {M.html} M, {V.convert_to("mL").html} mL solution of {c.simple_html} in water. How many grams of {c.simple_html} did they dissolve?'
    ])
    
    answer = m
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)




#---------------------------------------------------------------------
def generate_question():
    question_type = 'short_answer'

    question_options = [
        calc_M,
        calc_m
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
