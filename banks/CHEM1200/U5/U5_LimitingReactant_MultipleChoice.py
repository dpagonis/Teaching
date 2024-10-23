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



def generate_question():
    question_type = 'multiple_choice'

    while True:
        rxn = reaction(random.choice(reactions))
        if len(rxn.reactants) > 1:
            break

    limiting, excess = random.sample(rxn.reactants,2)
    m_lim = sf.random_value((0.1,10),(2,4),True)
    n_lim = m_lim / limiting.molecular_weight
    n_ex_equiv = n_lim * excess.coefficient / limiting.coefficient
    n_ex = sf.random_value((n_ex_equiv.value*1.15,n_ex_equiv.value*2),(2,4))
    m_ex = n_ex * excess.molecular_weight

    question_options = [
        f"Which reactant is limiting when {m_ex.html} g of {excess.simple_html} react with {m_lim.html} g of {limiting.simple_html}?",
        f"Which reactant is limiting when {m_lim.html} g of {limiting.simple_html} react with {m_ex.html} g of {excess.simple_html}?",
        f"Which reactant is limiting when {n_lim.html} mol of {limiting.simple_html} react with {m_ex.html} g of {excess.simple_html}?",
        f"Which reactant is limiting when {n_ex.html} mol of {excess.simple_html} react with {m_lim.html} g of {limiting.simple_html}?",
        f"Which reactant is limiting when {n_lim.html} mol of {limiting.simple_html} react with {n_ex.html} mol of {excess.simple_html}?",
        f"Which reactant is limiting when {n_ex.html} mol of {excess.simple_html} react with {n_lim.html} mol of {limiting.simple_html}?",
        f"Which reactant is in excess when {m_ex.html} g of {excess.simple_html} react with {m_lim.html} g of {limiting.simple_html}?",
        f"Which reactant is in excess when {m_lim.html} g of {limiting.simple_html} react with {m_ex.html} g of {excess.simple_html}?",
        f"Which reactant is in excess when {n_lim.html} mol of {limiting.simple_html} react with {m_ex.html} g of {excess.simple_html}?",
        f"Which reactant is in excess when {n_ex.html} mol of {excess.simple_html} react with {m_lim.html} g of {limiting.simple_html}?",
        f"Which reactant is in excess when {n_lim.html} mol of {limiting.simple_html} react with {n_ex.html} mol of {excess.simple_html}?",
        f"Which reactant is in excess when {n_ex.html} mol of {excess.simple_html} react with {n_lim.html} mol of {limiting.simple_html}?"
    ]
    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    if 'in excess' in formatted_question:
        answer =excess.formula
        incorrect = limiting.formula
    else:
        answer =limiting.formula
        incorrect = excess.formula

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect, #semicolon sep
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
