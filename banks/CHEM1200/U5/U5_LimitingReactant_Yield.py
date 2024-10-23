import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import molecule
from dp_chem import reaction 

file_path = 'reactions.txt'
reactions = []

with open(file_path, 'r') as file:
    # Read each line in the file
    for line in file:
        reactions.append(line.strip())

for r in reactions:
    rxn = reaction(r)
    if not rxn.isbalanced:
        raise TypeError('input file contained unbalanced reactions')


def quantify_yield():
    while True:
        rxn = reaction(random.choice(reactions))
        if len(rxn.reactants) > 1:
            break
    
    limiting, excess = random.sample(rxn.reactants,2)
    product = random.choice(rxn.products)
    m_lim = sf.random_value((0.1,10),(2,3),True)
    n_lim = m_lim / limiting.molecular_weight
    n_ex_equiv = n_lim * excess.coefficient / limiting.coefficient
    n_ex = sf.random_value((n_ex_equiv.value*1.15,n_ex_equiv.value*2),(2,4))
    m_ex = n_ex * excess.molecular_weight
    n_p = n_lim * product.coefficient/limiting.coefficient
    m_p = n_p * product.molecular_weight
    answers = m_p.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"How much {product.simple_html} (in g) can be produced by reacting {m_lim.html} g of {limiting.simple_html} with {m_ex.html} g of {excess.simple_html}?",
        f"How much {product.simple_html} (in g) can be produced by reacting {m_ex.html} g of {excess.simple_html} with {m_lim.html} g of {limiting.simple_html}?",
        f"How many grams of {product.simple_html} can be produced by reacting {m_lim.html} g of {limiting.simple_html} with {m_ex.html} g of {excess.simple_html}?",
        f"How many grams of {product.simple_html} can be produced by reacting {m_ex.html} g of {excess.simple_html} with {m_lim.html} g of {limiting.simple_html}?"
    ]

    formatted_question = random.choice(question_options)+"<br><br>"+create_mattext_element(rxn.tex)+"<br>"
    for r in rxn.reactants:
        formatted_question += f'<br>{r.simple_html}: {r.molecular_weight} g/mol'
    for p in rxn.products:
        formatted_question += f'<br>{p.simple_html}: {p.molecular_weight} g/mol'
    
    return formatted_question, answers 

def quantify_excess():
    while True:
        rxn = reaction(random.choice(reactions))
        if len(rxn.reactants) > 1:
            break
    
    limiting, excess = random.sample(rxn.reactants,2)
    m_lim = sf.random_value((0.1,10),(2,3),True)
    n_lim = m_lim / limiting.molecular_weight
    n_ex_equiv = n_lim * excess.coefficient / limiting.coefficient
    m_ex_equiv = n_ex_equiv * excess.molecular_weight
    
    m_ex = sf.random_value((m_ex_equiv.value*1.15,m_ex_equiv.value*2),(2,4))

    m_ex_remain = m_ex - m_ex_equiv

    question_options = [
        f"How many grams of excess reactant remain when {m_ex.html} g of {excess.simple_html} react with {m_lim.html} g of {limiting.simple_html}?",
        f"How many grams of excess reactant remain when {m_lim.html} g of {limiting.simple_html} react with {m_ex.html} g of {excess.simple_html}?",
        f"A student reacts {m_ex.html} g of {excess.simple_html} and {m_lim.html} g of {limiting.simple_html} through the following reaction. How much excess reactant (in g) remains at the end of the reaction?",
        f"A student reacts {m_lim.html} g of {limiting.simple_html} and {m_ex.html} g of {excess.simple_html} through the following reaction. How much excess reactant (in g) remains at the end of the reaction?"
    ]
    formatted_question = random.choice(question_options)+"<br><br>"+create_mattext_element(rxn.tex)+"<br>"
    for r in rxn.reactants:
        formatted_question += f'<br>{r.simple_html}: {r.molecular_weight} g/mol'
    for p in rxn.products:
        formatted_question += f'<br>{p.simple_html}: {p.molecular_weight} g/mol'

    answers = m_ex_remain.answers(sf_tolerance=1,roundoff_tolerance=True)

    return formatted_question, answers 

def generate_question():
    question_type = 'short_answer'

    question_options = [
        quantify_yield,
        quantify_excess
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
