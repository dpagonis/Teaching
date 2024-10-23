import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable
from dp_chem import molecule
from dp_chem import sf

def E_from_mol():
    
    dHvap = sf.random_value((10,60),(1,3),units_str='kJ mol-1')
    mol = sf.random_value((1e-3,10),(1,3),value_log=True)

    answer_unit = random.choice(['J','kJ','cal','kcal'])

    formatted_question = random.choice([
        f'Calculate the amount of energy (in {answer_unit}) required to vaporize {mol.html} moles of a compound whose enthalpy of vaporization is {dHvap.html} kJ mol<sup>-1</sup>. There are 4.184 J in 1 cal.'
    ])

    answer = mol * dHvap.convert_to(answer_unit+' mol-1')
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)

def mol_from_E():
    
    dHvap = sf.random_value((10,60),(1,3),units_str='kJ mol-1')
    E_unit = random.choice(['J','kJ','cal','kcal'])
    if 'k' in E_unit:
        upper_bound = 600
        lower_bound = 0.1
    else:
        upper_bound = 600000
        lower_bound = 100
    E = sf.random_value((lower_bound,upper_bound),(1,3),value_log=True,units_str=E_unit)

    formatted_question = random.choice([
        f'Calculate the number of moles in a sample that required {E.html} {E_unit} to be vaporized, given that the enthalpy of vaporization is {dHvap} kJ/mol. There are 4.184 J in 1 cal.'
    ])

    answer = E.convert_to('kJ')/dHvap
    return formatted_question, answer.answers(sf_tolerance=1,roundoff_tolerance=True)


#---------------------------------------------------------------------
def generate_question():
    question_type = 'short_answer'

    question_options = [
        E_from_mol,
        mol_from_E
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
