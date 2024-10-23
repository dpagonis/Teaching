import hashlib
import pandas as pd
import random
import os

from itertools import product as iter_product
from itertools import permutations

from dp_qti.makeqti import *
from dp_qti import reaction

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/systemsofreactions.txt')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Write the mass balance expression for {target_species} in the following system of reactions.<br>{rxn_html};all_mbal'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    row=reactions.sample(1)
    rs=[reaction(r,reversible=False) for r in row.values[0][0].split(';')]

    # Step 1: Generate the list of all molecules
    all_molecules_set = set()
    for r in rs:
        for reactant in r.reactants:
            all_molecules_set.add(reactant.formula)
        for product in r.products:
            all_molecules_set.add(product.formula)

    # Step 2: Build the dictionary of coefficients for each molecule in each reaction
    system_dict = {mol: [0] * len(rs) for mol in all_molecules_set}
    for i, r in enumerate(rs):
        for reactant in r.reactants:
            system_dict[reactant.formula][i] = -reactant.coefficient  # negative since it's a reactant
        for product in r.products:
            system_dict[product.formula][i] = product.coefficient  # positive since it's a product
    
    target_species = random.choice(list(system_dict.keys()))

    # For the target species, construct the basic mass balance terms
    mass_balance_terms = [] # list of lists...
    for i, coeff in enumerate(system_dict[target_species]):
        rate_eqn_versions = rs[i].rate_eqn_answers.split(';')
        termlist = get_term_list(coeff, rate_eqn_versions)
        mass_balance_terms.append(termlist)

    # Generate all combinations of rate equation forms for the target species
    
    mass_balance_terms = [termlist for termlist in mass_balance_terms if termlist]
    combinations = list(iter_product(*mass_balance_terms))

    # For each combination, get all possible orderings
    all_ordered_combinations = []
    for combination in combinations:
        all_ordered_combinations.extend(permutations(combination))

    # Convert these ordered combinations into equations
    possible_equations = [join_terms(ordered_combination) for ordered_combination in all_ordered_combinations]
    
    if len(possible_equations) == 0:
        raise ValueError("No answers")
    
    all_mbal = ";".join(possible_equations)

    texs = [r.tex for r in rs]
    htmls = [create_mattext_element(tex) for tex in texs]
    rxn_html = "<br>".join(htmls)

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

def get_term_list(coeff, rate_eqn_versions):
    """Return all possible terms based on coefficient and rate equation versions."""
    if coeff == 0:
        return []
    elif coeff == 1:
        return rate_eqn_versions
    elif coeff == -1:
        return [f"-{rate_eqn}" for rate_eqn in rate_eqn_versions]
    else:
        return [f"{coeff}{rate_eqn}" for rate_eqn in rate_eqn_versions]

def join_terms(terms):
    """Join terms ensuring subtraction is handled properly."""
    equation = ""
    for t in terms:
        term = t.strip()
        if not equation:  # if equation is still empty
            equation = term
        elif term.startswith('-'):
            term_nominus = term[1:]
            equation += f" - {term_nominus}"  # subtracting, so just add the term as it has '-'
        else:
            equation += f" + {term}"  # adding, so add with '+'
    return equation


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
