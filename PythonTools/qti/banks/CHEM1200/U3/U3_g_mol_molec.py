
import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem.units import units
from dp_chem import molecule



def generate_question():
    question_type = 'short_answer'

    question_options = [
        'How many moles are in a {mass.html} g sample of {c.simple_html}?;mol_answers',
        'What is the number of moles in a {mass.html} g sample of {c.simple_html}?;mol_answers',
        'How many molecules are in a {mass.html} g sample of {c.simple_html}?;mQ_answers',
        'What is the mass in g of {mol.html} moles of {c.simple_html}?;mass_answers',
        'How many molecules are in a {mol.html} mol sample of {c.simple_html}?;mQ_answers',
        'How much does {mol.html} mol of {c.simple_html} weigh (in g)?;mass_answers',
        'What is the mass of {mQ.html} molecules of {c.simple_html} in g?;mass_answers'
    ]

    compounds = [
        'H2O', 'CO2', 'O2', 'N2', 'H2', 'NH3', 'CH4', 'C2H6', 'C2H4', 'C2H2', 'HCl', 'HF', 'HBr', 'HI', 'NO', 'NO2',
        'N2O', 'SO2', 'SO3', 'CO', 'H2S', 'PH3', 'SiH4', 'Cl2', 'Br2', 'I2', 'F2', 'P4', 'S8', 'O3', 'NaCl', 'KBr',
        'LiF', 'MgO', 'CaCl2', 'NaH', 'KH', 'H2SO4', 'HNO3', 'HCN', 'H2CO3', 'H3PO4', 'NaOH', 'KOH', 'LiOH', 
         'NH4Cl', 'Na2CO3', 'K2CO3', 'Li2CO3', 'MgCO3', 'CaCO3', 'NH4NO3', 'NaNO3', 'KNO3', 'AgNO3', 'CuSO4',
        'FeSO4', 'ZnSO4', 'MgSO4', 'Al2O3', 'SiO2', 'P2O5', 'SO3', 'ClO2', 'BrO3', 'IO4', 'C3H8', 'C4H10', 'C5H12',
        'C6H14', 'C7H16', 'C8H18', 'C2H6O', 'C6H6', 'C6H12', 'C6H6O', 'C2H4O2', 'CH2O2', 'N2H4', 'CH5N', 'C2H7N',
        'SiC', 'BN', 'AlN', 'AlP', 'GaAs', 'InP', 'TiO2', 'ZnO', 'SnO2', 'PbO', 'PbO2', 'Fe2O3', 'Fe3O4', 'CoO', 'NiO',
        'CuO', 'Cu2O', 'Ag2O', 'HgO', 'CdO', 'VO2', 'V2O5', 'CrO3', 'MnO2', 'Tl2O', 'Tl2O3', 'Bi2O3', 'UO2', 'U3O8',
        'SF6', 'CF4', 'CCl4', 'CBr4', 'CI4', 'SiCl4', 'SiBr4', 'SiI4', 'PCl3', 'PBr3', 'PI3', 'S2Cl2', 'SCl2', 'ClF3',
        'BrF5', 'IF7', 'KrF2', 'XeF2', 'XeF4', 'XeF6', 'RnF2', 'NF3', 'PF5', 'AsF5', 'SF4', 'SeF6', 'TeF6', 'MoF6',
        'WF6', 'UF6', 'OF2', 'BeF2', 'MgF2', 'CaF2', 'SrF2', 'BaF2', 'RaF2', 'Li2S', 'Na2S', 'K2S', 'Rb2S', 'Cs2S',
        'BeCl2', 'MgCl2', 'CaCl2', 'SrCl2', 'BaCl2', 'TiCl4', 'ZrCl4', 'HfCl4', 'TcCl4', 'ReCl4', 'FeCl3',
        'RuCl3', 'OsCl3', 'RhCl3', 'IrCl3', 'NiCl2', 'PdCl2', 'PtCl2', 'CuCl2', 'AgCl', 'AuCl3', 'ZnCl2', 'CdCl2',
        'HgCl2', 'AlCl3', 'GaCl3', 'InCl3', 'TlCl3', 'SiF4', 'PF3', 'AsF3', 'SbF3', 'BiF3', 'SeCl4', 'TeCl4', 
        'MnF2', 'TcF6', 'ReF6', 'CrF2', 'MoF5', 'WF6', 'UF4'
    ]

    c = molecule(random.choice(compounds))

    while True:
        mol = sf.random_value((0.01,50),(1,4),True)
        mass = mol * c.molecular_weight
        mQ = mol * 6.02214076e23

        mol_from_mass = sf(mass.scientific_notation(),sig_figs=mass.sig_figs) / c.molecular_weight
        mol_from_mass_check = mol_from_mass.scientific_notation() == mol.scientific_notation()

        mol_from_mQ = sf(mQ.scientific_notation(),sig_figs=mQ.sig_figs)/6.02214076e23
        mol_from_mQ_check = mol_from_mQ.scientific_notation() == mol.scientific_notation()

        if mol_from_mass_check and mol_from_mQ_check:
            break

    mass_answers = mass.answers(sf_tolerance=1,roundoff_tolerance=True)
    mQ_answers = mQ.answers(sf_tolerance=1,roundoff_tolerance=True)
    mol_answers = mol.answers(sf_tolerance=1,roundoff_tolerance=True)

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
