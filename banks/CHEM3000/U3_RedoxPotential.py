import hashlib
import pandas as pd
import random
import os

import math
import re
from itertools import permutations

from dp_qti.makeqti import *
from dp_chem import molecule
from dp_chem import reaction
from dp_chem import sf

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/redoxpairs.csv')

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Given the half-reactions below calculate the net potential of this galvanic cell (in V):<br>{r1_html}<br>{E1_html}<br><br>{r2_html}<br>{E2_html};E_net.answers(sf_tolerance=1)',
        'The two half-reactions of a galvanic cell are listed below. Which element is oxidized?<br>{r1_html}<br>{E1_html}<br><br>{r2_html}<br>{E2_html};oxidized',
        'The two half-reactions of a galvanic cell are listed below. Which element is reduced?<br>{r1_html}<br>{E1_html}<br><br>{r2_html}<br>{E2_html};reduced'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    
    rows = reactions.sample(2)

    r1 = parse_redox_half_rxn(rows.iloc[0])
    r2 = parse_redox_half_rxn(rows.iloc[1])

    r1_html = create_mattext_element(r1.tex)
    r2_html = create_mattext_element(r2.tex)

    E1 = sf(str(rows.iloc[0]['Eo']))
    E2 = sf(str(rows.iloc[1]['Eo']))

    E1_tex = f'E^o={E1}V'
    E2_tex = f'E^o={E2}V'

    E1_html = create_mattext_element(E1_tex)
    E2_html = create_mattext_element(E2_tex)

    E_net = E1-E2 if E1.value > E2.value else E2-E1

    oxidized = rows.iloc[1]['redox_element'] if E1.value > E2.value else rows.iloc[0]['redox_element']
    reduced = rows.iloc[0]['redox_element'] if E1.value > E2.value else rows.iloc[1]['redox_element']

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

def get_rxn_term(m):
    coef_str = f'{m.coefficient}' if m.coefficient > 1 else ''
    phase_str = f'({m.phase})' if m.phase is not None else ''
    return coef_str+str(m)+phase_str


def parse_redox_half_rxn(row):
    n_e=row['n_e']
    pH_str = row['pH']
    ox_form = parse(row['oxidized'])
    red_form = parse(row['reduced'])
    redox_element = row['redox_element']

    reactants = []
    products = []

    reactants += [molecule('e-',coefficient=n_e)]

    ox_count = ox_form.element_dict.get(redox_element, 0)
    red_count = red_form.element_dict.get(redox_element, 0)
    lcm = ox_count * red_count // math.gcd(ox_count, red_count)
    ox_coefficient = lcm // ox_count
    red_coefficient = lcm // red_count

    ox_form.coefficient = ox_coefficient
    red_form.coefficient = red_coefficient

    reactants += [ox_form]
    products += [red_form]

    charge_reactants = sum([m.coefficient * m.charge for m in reactants])
    charge_products = sum([m.coefficient * m.charge for m in products])

    if charge_reactants != charge_products:
        if charge_products > charge_reactants:
            if pH_str == 'basic':
                OH = molecule('OH-',coefficient=charge_products-charge_reactants)
                products += [OH]
            else:
                H = molecule('H+',coefficient=charge_products-charge_reactants)
                reactants += [H]
        else:
            if pH_str == 'basic':
                OH = molecule('OH-',coefficient=charge_reactants-charge_products)
                reactants += [OH]
            else:
                H = molecule('H+',coefficient=charge_reactants-charge_products)
                products += [H]

    
    delta_n_O = sum([m.element_dict.get('O', 0)* m.coefficient for m in reactants])-sum([m.element_dict.get('O', 0)* m.coefficient for m in products])

    if delta_n_O != 0:
        if delta_n_O > 0:
            products += [molecule('H2O',coefficient=delta_n_O)]
        else:
            reactants += [molecule('H2O',coefficient=abs(delta_n_O))]

    delta_n_H = sum([m.element_dict.get('H', 0) * m.coefficient for m in reactants])-sum([m.element_dict.get('H', 0)* m.coefficient for m in products])
    if delta_n_H == 0:
        return (reaction(reactants,products)) 
    else:
        print("reactants:",reactants)
        print("products:",products)
        raise ValueError("parse_redox_half_rxn failed to balance the equation")

def parse(s):
    """
    This function will use regular expression to extract molecule and phase from a given string.
    """
    p = re.compile(r'([A-Za-z\(\)\d\+\-]+)\s*\(([a-z\s]*)\)$')

    m = p.match(s.strip())
    if m:
        formula = m.group(1)
        phase = m.group(2)
        m = molecule(formula,phase=phase)
    else:
        m = molecule(s)

    return m

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

def parse(s):
    """
    This function will use regular expression to extract molecule and phase from a given string.
    """
    p = re.compile(r'([A-Za-z\(\)\d\+\-]+)\s*\(([a-z\s]*)\)$')

    m = p.match(s.strip())
    if m:
        formula = m.group(1)
        phase = m.group(2)
        m = molecule(formula,phase=phase)
    else:
        m = molecule(s)

    return m


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
