import hashlib
import pandas as pd
import random
import os
import re 
from itertools import permutations


from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/equilibriumrxns.csv')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Write the expression for the reaction quotient Q for the following reaction.<br>{rxn_html};Q_list'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    row=reactions.sample(1)

    reactants, reactants_coef = handle(row['reactants'].values[0])
    products, products_coef = handle(row['products'].values[0])
    

    reactants_std, reactants_std_phase, reactants_std_coefs = handle_std(row['reactants_std'].values[0])
    products_std, products_std_phase,products_std_coefs = handle_std(row['products_std'].values[0])


    reactant_strings = [f'{coef}{m.tex}' if coef > 1 else m.tex for m, coef in zip(reactants, reactants_coef)]
    reactant_strings += [f'{coef}{m.tex}{phase}' if coef > 1 else f'{m.tex}{phase}' for m, coef, phase in zip(reactants_std, reactants_std_coefs, reactants_std_phase)]

    product_strings = [f'{coef}{m.tex}' if coef > 1 else m.tex for m, coef in zip(products, products_coef)]
    product_strings += [f'{coef}{m.tex}{phase}' if coef > 1 else f'{m.tex}{phase}' for m, coef, phase in zip(products_std, products_std_coefs, products_std_phase)]


    # Join the 'tex' strings with "+", and place "\leftrightarrow" between reactants and products
    tex_string = f"{'+'.join(reactant_strings)}\\leftrightarrow{{}}{'+'.join(product_strings)}"
    rxn_html = create_mattext_element(tex_string)

    reactant_terms = [f'[{m}]^{coef}' if coef > 1 else f'[{m}]' for m,coef in zip(reactants,reactants_coef)]
    product_terms = [f'[{m}]^{coef}' if coef > 1 else f'[{m}]' for m,coef in zip(products,products_coef)]
    
    reactant_perm = list(permutations(reactant_terms))
    product_perm = list(permutations(product_terms))

    all_combinations = [(r, p) for r in reactant_perm for p in product_perm]
    all_Q = [f'{"".join(p)}'+('/' if len(r)>0 and len(p)>0 else '')+f'{"".join(r)}' for r,p in all_combinations]
    Q_list=';'.join(all_Q)

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

def handle_std(std):
    """
    This function will use regular expression to extract formula, phase, and coefficient.
    """
    p = re.compile(r'(\d+)?([A-Za-z\(\)\d\+\-]+)\s*\(([A-Za-z\s]*)\)$')
    
    formulas = []
    phases = []
    coefs = []
    
    if isinstance(std,float):
        return formulas, phases, coefs
    
    stds = std.split(';')

    for std in stds:
        m = p.match(std)
        coef = m.group(1) if m.group(1) else 1
        formula = m.group(2)
        phase = f"({m.group(3)})"
        formulas.append(molecule(formula))
        phases.append(phase)
        coefs.append(int(coef))

    return formulas, phases, coefs

def handle(s):
    """
    This function will use regular expression to extract formula and coefficient.
    """
    p = re.compile(r'(\d+)?([A-Za-z\(\)\d\+\-]+)')
    
    formulas = []
    coefs = []
    if isinstance(s,float):
        return formulas, coefs

    compounds = s.split(';')
    for c in compounds:
        m = p.match(c.strip())
        if m:
            coef = m.group(1) if m.group(1) else 1
            formula = m.group(2)
            formulas.append(molecule(formula))
            coefs.append(int(coef))

    return formulas, coefs


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
