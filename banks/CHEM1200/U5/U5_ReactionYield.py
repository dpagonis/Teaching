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

def mol_to_mol():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    n_r = sf.random_value((0.01,10),(2,4),True)
    n_p = n_r * product.coefficient / reactant.coefficient
    answers = n_p.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"Calculate the amount of {product.simple_html} (in mol) that can be produced from {n_r.html} moles of {reactant.simple_html} by the following reaction:",
        f"How many moles of {product.simple_html} can be produced from {n_r.html} moles of {reactant.simple_html} by the reaction below?",
        f"A student reacts {n_r.html} moles of {reactant.simple_html} according to the reaction below. How many moles of {product.simple_html} will be produced?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def product_mol_to_mol():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    n_p = sf.random_value((0.01,10),(2,4),True)
    n_r = n_p * reactant.coefficient / product.coefficient
    answers = n_r.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"A student forms {n_p.html} moles of {product.simple_html} according to the reaction below. How many moles of {reactant.simple_html} were consumed?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def mass_to_mol():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    m_r = sf.random_value((1,100),(2,4),True,units_str='g')
    n_r = m_r/reactant.molecular_weight
    n_p = n_r * product.coefficient / reactant.coefficient
    answers = n_p.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"Calculate the amount of {product.simple_html} (in mol) that can be produced from {m_r.html} g of {reactant.simple_html} by the following reaction:",
        f"How many moles of {product.simple_html} can be produced from {m_r.html} grams of {reactant.simple_html} by the reaction below?",
        f"A student reacts {m_r.html} g of {reactant.simple_html} according to the reaction below. How many moles of {product.simple_html} will be produced?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def product_mass_to_mol():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    m_p = sf.random_value((1,100),(2,4),True,units_str='g')
    n_p = m_p/product.molecular_weight
    n_r = n_p * reactant.coefficient / product.coefficient
    answers = n_r.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"Calculate the amount of {reactant.simple_html} (in mol) that is needed to produce {m_p.html} g of {product.simple_html} by the following reaction:"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def mol_to_mass():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    n_r = sf.random_value((0.01,10),(2,4),True)
    n_p = n_r * product.coefficient / reactant.coefficient
    m_p = n_p * product.molecular_weight
    answers = m_p.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"Calculate the amount of {product.simple_html} (in g) that can be produced from {n_r.html} moles of {reactant.simple_html} by the following reaction:",
        f"How many grams of {product.simple_html} can be produced from {n_r.html} moles of {reactant.simple_html} by the reaction below?",
        f"A student reacts {n_r.html} moles of {reactant.simple_html} according to the reaction below. How many grams of {product.simple_html} will be produced?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def product_mol_to_mass():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    n_p = sf.random_value((0.01,10),(2,4),True)
    n_r = n_p * reactant.coefficient / product.coefficient
    m_r = n_r * reactant.molecular_weight
    answers = m_r.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"How many grams of {reactant.simple_html} are needed to produce {n_p.html} moles of {product.simple_html} through the reaction below?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def mass_to_mass():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    m_r = sf.random_value((1,100),(2,4),True,units_str='g')
    n_r = m_r/reactant.molecular_weight
    n_p = n_r * product.coefficient / reactant.coefficient
    m_p = n_p * product.molecular_weight
    answers = m_p.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"Calculate the amount of {product.simple_html} (in g) that can be produced from {m_r.html} g of {reactant.simple_html} by the following reaction:",
        f"How many grams of {product.simple_html} can be produced from {m_r.html} grams of {reactant.simple_html} by the reaction below?",
        f"A student reacts {m_r.html} g of {reactant.simple_html} according to the reaction below. How many grams of {product.simple_html} will be produced?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def product_mass_to_mass():
    rxn = reaction(random.choice(reactions))
    reactant = random.choice(rxn.reactants)
    product = random.choice(rxn.products)
    m_p = sf.random_value((1,100),(2,4),True,units_str='g')
    n_p = m_p/product.molecular_weight
    n_r = n_p * reactant.coefficient / product.coefficient
    m_r = n_r * reactant.molecular_weight
    answers = m_r.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f"A student produces {m_p.html} g of {product.simple_html} through the reaction below. How many grams of {reactant.simple_html} were needed for this reaction?"
    ]

    formatted_question = random.choice(question_options)+"<br>"+create_mattext_element(rxn.tex)

    return formatted_question, answers 

def generate_question():
    question_type = 'short_answer'

    question_options = [
        mol_to_mol,
        mass_to_mol,
        mol_to_mass,
        mass_to_mass,
        product_mol_to_mol,
        product_mass_to_mol,
        product_mol_to_mass,
        product_mass_to_mass
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
