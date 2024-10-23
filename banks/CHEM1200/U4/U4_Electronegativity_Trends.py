import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable
from dp_chem import molecule

PT = periodictable.periodictable()

def getLowerElectronegativityElement(E1):
    while True:
        E2 = PT.random(weighted=True)
        en2 = E2['en_pauling']
        g2 = E2['group']
        if E1['symbol']==E2['symbol'] or pd.isna(en2) or pd.isna(g2): #must be different element, have electroneg value, and not in f block
            continue

        if E1['en_pauling']>en2 and E1['group']>=g2 and E1['period']<=E2['period']:
            break
    return E2


def TwoElements_High():
    correct_answer = None
    while True:
        E1 = PT.random(weighted=True)

        if pd.isna(E1['en_pauling']) or pd.isna(E1['group']):
            continue

        if E1['en_pauling'] >=1:
            break 

    E2 = getLowerElectronegativityElement(E1)

    formatted_question = random.choice([
        'Which element is more electronegative?',
        'Select the higher electronegativity element',
        'Select the element with the higher electronegativity value'
    ])

    return formatted_question, E1["name"], E2["name"]

def TwoElements_Low():
    correct_answer = None
    while True:
        E1 = PT.random(weighted=True)

        if pd.isna(E1['en_pauling']) or pd.isna(E1['group']):
            continue

        if E1['en_pauling'] >=1:
            break 

    E2 = getLowerElectronegativityElement(E1)

    formatted_question = random.choice([
        'Which element is less electronegative?',
        'Select the lower electronegativity element',
        'Select the element with the lower electronegativity value'
    ])

    return formatted_question, E2["name"], E1["name"]

def ThreeElements_High():
    correct_answer = None
    while True:
        E1 = PT.random(weighted=True)
        if pd.isna(E1['en_pauling']) or pd.isna(E1['group']):
            continue
        if E1['en_pauling'] >=1.5:
            break 

    while True:
        E2 = getLowerElectronegativityElement(E1)
        E3 = getLowerElectronegativityElement(E1)

        if E2['symbol'] != E3['symbol']:
            break

    formatted_question = random.choice([
        'Which element is the most electronegative?',
        'Select the highest electronegativity element',
        'Select the element with the highest electronegativity value'
    ])

    incorrect_answers = ';'.join([E2["name"],E3["name"]])
    return formatted_question, E1["name"], incorrect_answers

def ThreeElements_Low():
    correct_answer = None
    while True:
        E1 = PT.random(weighted=True)
        if pd.isna(E1['en_pauling']) or pd.isna(E1['group']):
            continue
        if E1['en_pauling'] >=1.5:
            break 

    while True:
        E2 = getLowerElectronegativityElement(E1)
        E3 = getLowerElectronegativityElement(E1)

        if E3['en_pauling'] < E2['en_pauling'] and E2['symbol'] != E3['symbol']:
            break

    formatted_question = random.choice([
        'Which element is the least electronegative?',
        'Select the lowest electronegativity element',
        'Select the element with the lowest electronegativity value'
    ])
    incorrect_answers = ';'.join([E1["name"],E2["name"]])
    return formatted_question, E3["name"], incorrect_answers

#---------------------------------------------------------------------
def generate_question():
    question_type = 'multiple_choice'

    question_options = [
        TwoElements_High,
        TwoElements_Low,
        ThreeElements_High,
        ThreeElements_Low
    ]

    func = random.choice(question_options)
    formatted_question, answer, incorrect_answers = func()

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect_answers,
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
