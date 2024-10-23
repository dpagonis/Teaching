import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti.periodictable import periodictable

PT = periodictable()

def generate_question():
    question_type = 'numerical_tolerance'

    question_options = [
        'What is the concentration (in mol/L) of a solution prepared by dissolving {mol} mol of {solute} in {vol_mL} mL of water?;conc_answer',
        'A solution of {solute} has a concentration of {conc} mol/L. How many moles of {solute} are present in {vol_mL} mL of this solution?;mol_answer',
        'A solution of {solute} has a concentration of {conc} mol/L. What volume of solution (in mL) containes {mol} mol of {solute}?;vol_answer'
    ]

    solutes = [
        "NaCl",               # Sodium chloride
        "sulfuric acid",      # H2SO4
        "glucose",            # C6H12O6
        "KBr",                # Potassium bromide
        "acetic acid",        # CH3COOH
        "calcium chloride",   # CaCl2
        "ethanol",            # C2H5OH
        "sodium bicarbonate", # NaHCO3
        "magnesium sulfate",  # MgSO4
        "potassium iodide",   # KI
        "hydrochloric acid",  # HCl
        "ammonium nitrate",   # NH4NO3
        "sodium hydroxide",   # NaOH
        "nitric acid",        # HNO3
        "potassium nitrate",  # KNO3
        "sodium sulfate",     # Na2SO4
        "magnesium chloride", # MgCl2
        "copper (II) sulfate", # CuSO4
        "ammonia"             # NH3
    ]
    solute = random.choice(solutes)

    vol_mL = sf.random_value((10,100),(2,3),units_str='mL')
    conc = sf.random_value((0.01,1),(2,3),True)
    mol = conc * vol_mL.convert_to('L')

    vol_answer= f'{vol_mL};{2*10**vol_mL.last_decimal_place}'
    mol_answer= f'{mol};{2*10**mol.last_decimal_place}'
    conc_answer= f'{conc};{2*10**conc.last_decimal_place}'

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
