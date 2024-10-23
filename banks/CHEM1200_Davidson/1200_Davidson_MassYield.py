import hashlib
import pandas as pd
import random
import os
from math import gcd

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule
from dp_qti import reaction 

reactions = pd.read_csv('massyieldreactions.csv')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'How many grams of {precipitate_html} can be produced from the reaction of {vol_mL} mL of {conc_M} M {limiting_reactant_html} with excess {excess_reactant} according to the following reaction?<br><br>{reaction_html}<br><br><em>(Use decimal notation and the units of g for your answer)</em>;answers_string'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    row=reactions.sample(1)
    
    rxn = reaction(row['Reaction'].values[0])
    excess_reactant = row['excess_reactant'].values[0]
    precipitate = molecule(row['precipitate'].values[0])
    limiting_reactant = molecule(row['limiting_reactant'].values[0])
    stoichiometry = row['stoichiometry'].values[0]

    if rxn.isbalanced is False:
        raise ValueError("Reaction is not balanced:"+row['Reaction'].values[0])

    vol_mL = sf.random_value((10,50),(2,3))
    conc_M = sf.random_value((1,10),(2,3))

    mol_product = (vol_mL/1000) * conc_M * stoichiometry
    mass_product = mol_product * precipitate.molecular_weight

    answer_list = mass_product.answers(roundoff_tolerance=True).split(';')
    answer_list_with_units = [a + 'g' for a in answer_list]
    answer_list_with_units_space = [a + ' g' for a in answer_list]
    answers_string = ';'.join(answer_list+answer_list_with_units+answer_list_with_units_space)

    precipitate_html = precipitate.simple_html
    limiting_reactant_html = limiting_reactant.simple_html
    reaction_html = rxn.simple_html

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
