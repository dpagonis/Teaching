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

# for r in reactions:
#     rxn = reaction(r)
#     if not rxn.isbalanced:
#         print(r)

def incorrect_answers(correct_answer):
    answers = {'Yes','No'}
    answers.remove(correct_answer)
    return ';'.join(list(answers))

def generate_question():
    question_type = 'multiple_choice'

    rxn_original = reaction(random.choice(reactions))
    rxn = reaction(rxn_original.plaintext)
    answer = random.choice(['Yes','No'])

    if answer == 'No':
        
        if random.choice([True,False]):
            species = rxn.reactants
            coefs = []
            for s in species:
                coefs.append(s.coefficient)
            i = random.randint(0,len(coefs)-1)
            coef_original = coefs[i]
            if random.choice([True, False]) and coef_original > 1:
                coef_new = coef_original - 1
            else:
                coef_new = coef_original + 1 

            rxn.reactants[i].coefficient = coef_new
        else:
            species = rxn.products
            coefs = []
            for s in species:
                coefs.append(s.coefficient)
            i = random.randint(0,len(coefs)-1)
            coef_original = coefs[i]
            if random.choice([True, False]) and coef_original > 1:
                coef_new = coef_original - 1
            else:
                coef_new = coef_original + 1 

            rxn.products[i].coefficient = coef_new
        
        rxn._update()

        if rxn.isbalanced:
            raise ValueError("you f'ed up")
    
    rxn_tex = create_mattext_element(rxn.tex)
    formatted_question = f'Is this reaction balanced:<br>{rxn_tex}'

    

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect_answers(answer),
        'question_type': question_type
    }

def generate_questions():
    num_questions = 250
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
