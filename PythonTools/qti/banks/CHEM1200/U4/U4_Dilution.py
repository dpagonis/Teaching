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

def calc_M2():
    
    M1 = sf.random_value((1,10),(1,4))
    V1 = sf.random_value((0.001,0.1),(2,4),value_log=True, units_str='L')
    V2 = sf.random_value((V1.value*2,V1.value*1000),(2,4),value_log=True, units_str='L')
    c=molecule(random.choice(COMPOUNDS))

    M2 = M1 * V1 / V2

    formatted_question = random.choice([
        f'Calculate the molarity of a solution prepared by diluting {V1.html} L of {M1.html} M stock solution to {V2.html} L.',
        f'Calculate the molarity of a solution prepared by diluting {V1.convert_to("mL").html} mL of {M1.html} M stock solution to {V2.html} L.',
        f'Calculate the concentration (in mol/L) of a solution prepared by diluting {V1.html} L of {M1.html} M stock solution to {V2.convert_to("mL").html} mL.',
        f'Calculate the concentration (in mol/L) of a solution prepared by diluting {V1.convert_to("mL").html} mL of {M1.html} M stock solution to {V2.convert_to("mL").html} mL.',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s concentration (in mol/L) when {V1.html} L of stock are diluted to {V2.html} L.',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s concentration (in mol/L) when {V1.html} L of stock are diluted to {V2.convert_to("mL").html} mL.',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s molarity when {V1.convert_to("mL").html} mL of stock are diluted to {V2.html} L.',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s molarity when {V1.convert_to("mL").html} mL of stock are diluted to {V2.convert_to("mL").html} mL.'
    ])
    
    answer = M2
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_M1():
    
    M2 = sf.random_value((1e-3,0.1),(1,4))
    V1 = sf.random_value((0.001,0.1),(2,4),value_log=True, units_str='L')
    V2 = sf.random_value((V1.value*2,V1.value*1000),(2,4),value_log=True, units_str='L')
    c=molecule(random.choice(COMPOUNDS))

    M1 = M2 * V2 / V1

    formatted_question = random.choice([
        f'What is the molarity of a stock solution of {c.simple_html} if diluting {V1.html} L of stock to {V2.html} L gives a solution with a concentration of {M2.html} M?',
        f'What is the molarity of a stock solution of {c.simple_html} if diluting {V1.convert_to("mL").html} mL of stock to {V2.html} L gives a solution with a concentration of {M2.html} M?',
        f'What is the molarity of a stock solution of {c.simple_html} if diluting {V1.html} L of stock to {V2.convert_to("mL").html} mL gives a solution with a concentration of {M2.html} M?',
        f'What is the molarity of a stock solution of {c.simple_html} if diluting {V1.convert_to("mL").html} mL of stock to {V2.convert_to("mL").html} mL gives a solution with a concentration of {M2.html} M?',
        f'A new solution is prepared by diluting {V1.html} L of stock to {V2.convert_to("mL")} mL. What is the molarity of the stock solution if the new solution has a concentration of {M2.html} M?',
        f'A new solution is prepared by diluting {V1.convert_to("mL").html} mL of stock to {V2.html} L. What is the molarity of the stock solution if the new solution has a concentration of {M2.html} M?',
        f'A new solution is prepared by diluting {V1.convert_to("mL").html} mL of stock to {V2.convert_to("mL").html} mL. What is the molarity of the stock solution if the new solution has a concentration of {M2.html} M?',
        f'A new solution is prepared by diluting {V1.html} L of stock to {V2.html} L. What is the molarity of the stock solution if the new solution has a concentration of {M2.html} M?'
    ])
    
    answer = M1
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_V1():
    
    M2 = sf.random_value((1e-3,0.1),(1,4))
    V2 = sf.random_value((0.1,1),(2,4),value_log=True, units_str='L')
    M1 = sf.random_value((M2.value*2,M2.value*100),(2,4),value_log=True)
    c=molecule(random.choice(COMPOUNDS))
    answer_unit = random.choice(['L','mL'])
    V1 = M2 * V2 / M1

    formatted_question = random.choice([
        f'A {M2.html} M solution of {c.simple_html} is prepared by diluting a {M1.html} M stock solution to {V2.convert_to("mL").html} mL. What was the volume (in {answer_unit}) of the aliquot of stock used to prepare the new solution?',
        f'A {M2.html} M solution of {c.simple_html} is prepared by diluting a {M1.html} M stock solution to {V2.html} L. What was the volume (in {answer_unit}) of the aliquot of stock used to prepare the new solution?',
        f'Calculate the volume (in {answer_unit}) of a {M1.html} M stock solution of {c.simple_html} that should be diluted to make {V2.html} L of {M2.html} M {c.simple_html}.',
        f'Calculate the volume (in {answer_unit}) of a {M1.html} M stock solution of {c.simple_html} that should be diluted to make {V2.convert_to("mL").html} mL of {M2.html} M {c.simple_html}.'
    ])
    
    answer = sf(str(V1.value),sig_figs=V1.sig_figs,units_str='L').convert_to(answer_unit)
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def calc_V2():
    
    M1 = sf.random_value((0.01,5),(1,4))
    V1 = sf.random_value((0.1,1),(2,4),value_log=True, units_str='L')
    M2 = sf.random_value((M1.value/100,M1.value/2),(2,4),value_log=True)
    c=molecule(random.choice(COMPOUNDS))
    answer_unit = random.choice(['L','mL'])
    V2 = M1 * V1 / M2

    formatted_question = random.choice([
        f'A {M2.html} M solution of {c.simple_html} is prepared by diluting {V1.convert_to("mL").html} mL of a {M1.html} M stock solution. What is the volume (in {answer_unit}) of the new solution?',
        f'A {M2.html} M solution of {c.simple_html} is prepared by diluting {V1.html} L of a {M1.html} M stock solution. What is the volume (in {answer_unit}) of the new solution?',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s volume in {answer_unit} if diluting {V1.html} L of stock gives a solution with a concentration of {M2.html} M.',
        f'A new solution is prepared from a {M1.html} M stock solution. Calculate the new solution\'s volume in {answer_unit} if diluting {V1.convert_to("mL").html} mL of stock gives a solution with a concentration of {M2.html} M.'
    ])
    
    answer = sf(str(V2.value),sig_figs=V2.sig_figs,units_str='L').convert_to(answer_unit)
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)


#---------------------------------------------------------------------
def generate_question():
    question_type = 'short_answer'

    question_options = [
        calc_M1,
        calc_M2,
        calc_V1,
        calc_V2
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
