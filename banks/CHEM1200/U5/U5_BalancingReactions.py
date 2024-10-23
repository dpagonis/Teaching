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


def generate_question(i):
    question_type = 'short_answer'

    rxn_original = reaction(reactions[i])
    rxn = reaction(rxn_original.plaintext)
    
    coefs = []
    for s in rxn.reactants:
        coefs.append(str(s.coefficient))
        s.coefficient = 1
    for s in rxn.products:
        coefs.append(str(s.coefficient))
        s.coefficient = 1
    
    rxn._update()
    rxn_tex = create_mattext_element(rxn.tex)
    formatted_question = f'Balance the following reaction.<br>Enter your answer as a list of coefficients separated by commas.<br>{rxn_tex}'

    answers = []
    answers.append(','.join(coefs))
    answers.append(', '.join(coefs))
    answer_list = ';'.join(answers)

    return {
        'question': formatted_question,
        'correct_answers': answer_list,
        'question_type': question_type
    }

def generate_questions():
    num_questions = len(reactions)
    basename = os.path.basename(__file__).removesuffix('.py')
    
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for i in range(num_questions):
        question = generate_question(i)
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
