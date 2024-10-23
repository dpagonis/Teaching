import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable
from dp_chem import molecule

PT = periodictable.periodictable()

def BondsInCompound():
    compounds = [
            'H2O', 'CO2', 'O2', 'N2', 'H2', 'NH3', 'CH4', 'C2H6', 'C2H4', 'C2H2', 'HCl', 'HF', 'HBr', 'HI', 'NO', 'NO2',
            'N2O', 'SO2', 'SO3', 'CO', 'H2S', 'PH3', 'SiH4', 'Cl2', 'Br2', 'I2', 'F2', 'P4', 'S8', 'O3', 'NaCl', 'KBr',
            'LiF', 'MgO', 'CaCl2', 'NaH', 'KH',
            'Al2O3', 'SiO2', 'P2O5', 'SO3', 'ClO2', 'BrO3', 'IO4', 'C3H8', 'C4H10', 'C5H12',
            'C6H14', 'C7H16', 'N2H4', 
            'SiC', 'BN', 'AlN', 'AlP', 'GaAs', 'InP', 'TiO2', 'ZnO', 'SnO2', 'PbO', 'PbO2', 'Fe2O3', 'Fe3O4', 'CoO', 'NiO',
            'CuO', 'Cu2O', 'Ag2O', 'HgO', 'CdO', 'VO2', 'V2O5', 'CrO3', 'MnO2', 'Tl2O', 'Tl2O3', 'Bi2O3', 'UO2', 'U3O8',
            'BeF2', 'MgF2', 'CaF2', 'SrF2', 'BaF2', 'RaF2', 'Li2S', 'Na2S', 'K2S', 'Rb2S', 'Cs2S',
            'BeCl2', 'MgCl2', 'CaCl2', 'SiF4', 'PF3', 'AsF3', 'SbF3', 'BiF3', 'SeCl4', 'TeCl4', 
            'MnF2', 'TcF6', 'ReF6', 'CrF2', 'MoF5', 'WF6', 'UF4'
        ]

    while True:
        correct_answer = None
        
        C = molecule(random.choice(compounds))
        
        elements = list(C.element_dict.keys()) #get elements
        e1 = elements[0]
        if len(elements) == 2:
            e2 = elements[1]
        else:
            e2 = elements[0]
            

        eneg1=PT.property(e1,'en_pauling') #get electronegativities
        eneg2=PT.property(e2,'en_pauling')

        if eneg1 is not None and eneg2 is not None: #classify
            diff = abs(eneg1-eneg2)
            if diff >= 2:
                correct_answer = "Ionic"
            elif diff >= 0.4:
                correct_answer = "Polar Covalent"
            elif diff >= 0:
                correct_answer = "Nonpolar Covalent"
        
        if correct_answer is not None:
            break
        
    formatted_question = random.choice([
        f'Classify the bonds in {C.simple_html}',
        f'What kinds of bonds join the atoms of {C.simple_html}?',
    ])

    formatted_question += f'<br><br>Electronegativity values:<br>{e1}: {eneg1}'
    if len(elements) > 1:
        formatted_question += f'<br>{e2}: {eneg2}'

    return formatted_question, correct_answer, incorrect_answers(correct_answer)

def BondsBetweenElements():
    correct_answer = None
    while True:
        E1 = PT.random()
        E2 = PT.random()
        eneg1 = E1['en_pauling']
        eneg2 = E2['en_pauling']

        diff = abs(eneg1-eneg2)
        if diff >= 1.9999: #deal with floating point bullshit
            correct_answer = "Ionic"
        elif diff > 0.3999:
            correct_answer = "Polar Covalent"
        elif diff >= 0:
            correct_answer = "Nonpolar Covalent"

        if not pd.isna(eneg1) and not pd.isna(eneg2) and E1['symbol'] != E2['symbol']:
            if correct_answer == 'Polar Covalent':
                if random.choice([True,False]): #toss half the polar covalents...
                    break 
            else:
                break

    formatted_question = random.choice([
        f"What kind of bond do you expect to form between {E1['name']} and {E2['name']}?",
        f"Classify the bonding of {E1['name']} with {E2['name']}.",
        f"What kind of bond do you expect to form between {E1['symbol']} and {E2['symbol']}?",
        f"Classify the bonding of {E1['symbol']} with {E2['symbol']}."
    ])

    formatted_question += f"<br><br>Electronegativity values:<br>{E1['symbol']}: {eneg1}<br>{E2['symbol']}: {eneg2}"

    return formatted_question, correct_answer, incorrect_answers(correct_answer)

def incorrect_answers(correct_answer):
    answers = {'Ionic', 'Polar Covalent', 'Nonpolar Covalent'}
    answers.remove(correct_answer)
    return ';'.join(list(answers))

#-----------------------------------------------------------------

def generate_question():
    question_type = 'multiple_choice'

    #list of strings
    #each string is semicolon-separated: "question text; answers"
    question_options = [
        BondsInCompound,
        BondsBetweenElements
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
