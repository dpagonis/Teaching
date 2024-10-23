import hashlib
import pandas as pd
import random
from scipy.stats import t
import os
import re
from itertools import permutations

from dp_qti.makeqti import *

cations = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/cations.csv')
anions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/anions.csv')

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Write the charge balance for a solution containing the following ions:<br>{ionlist_html};all_cbal_str'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    n_cation = random.randint(0,2)
    n_anion = random.randint(0,2)

    # Exclude 'H_3O^{+}'
    cation_sample = cations[cations['Molecular Formula'] != 'H_3O^{+}'].sample(n_cation)
    cation_list = cation_sample['Molecular Formula'].tolist()
    cation_charges = [abs(getcharge(ion)) for ion in cation_list]

    anion_sample = anions.sample(n_anion)
    anion_list = anion_sample['Molecular Formula'].tolist()
    anion_charges = [abs(getcharge(ion)) for ion in anion_list]

    # Ensure 'OH^{-}' and 'H^{+}' are always present
    if 'OH^{-}' not in anion_list:
        anion_list.append('OH^{-}')
        anion_charges.append(1)
    if 'H^{+}' not in cation_list:
        cation_list.append('H^{+}')
        cation_charges.append(1)
    
    # Create the comma-separated ion list
    ionlist_html = ', '.join(create_mattext_element(ion) for ion in sorted(cation_list + anion_list))

    # Create the charge balance equation
    cation_terms = [f'{charge if charge != 1 else ""}[{re.sub("[_^{}]", "", ion)}]' for ion, charge in zip(cation_list, cation_charges)]
    anion_terms = [f'{charge if charge != 1 else ""}[{re.sub("[_^{}]", "", ion)}]' for ion, charge in zip(anion_list, anion_charges)]

    # Get all possible permutations of the cation and anion terms separately
    cation_perm = list(permutations(cation_terms))
    anion_perm = list(permutations(anion_terms))
    
    # Create all combinations of cation and anion permutations
    all_combinations = [(c, a) for c in cation_perm for a in anion_perm]

    # Convert each combination into a string equation and add to a list
    all_cbal = [f'{"+".join(c)}={"+".join(a)}' for c, a in all_combinations]
    all_cbal_str = '; '.join(all_cbal)


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

def getcharge(tex):
    # Search for ^{...} in the LaTeX string
    match = re.search(r'\^\{(.*?)\}', tex)
    if match:  # If found...
        charge_str = match.group(1)  # Extract the contents
        # First, check if the string starts with a digit
        if charge_str[0].isdigit():
            # If it does, extract the number part
            charge_num = int(''.join(filter(str.isdigit, charge_str)))
            # Now check for the sign
            if charge_str.endswith('+'):  # If it ends with a plus sign...
                return charge_num  # Return the number as positive
            elif charge_str.endswith('-'):  # If it ends with a minus sign...
                return -charge_num  # Return the number as negative
        # If the string does not start with a digit, assume a charge of 1
        else:
            if charge_str.endswith('+'):  # If it ends with a plus sign...
                return 1  # Return 1 as positive
            elif charge_str.endswith('-'):  # If it ends with a minus sign...
                return -1  # Return 1 as negative
    # If ^{...} is not found or if its contents are not recognized, return None
    return None

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
