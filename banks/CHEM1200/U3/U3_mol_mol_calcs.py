
import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem.units import units
from dp_chem import molecule


def gC_gE(C):

    gC = sf.random_value((1e-3,1e3),(2,5),True)
    MW_C = C.molecular_weight

    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    MW_E = E.molecular_weight

    molC = gC / (MW_C)
    molE = molC * E_coef
    gE = molE * MW_E 

    formatted_question = random.choice([
        f'How many grams of {E.simple_html} are in {gC.html} g of {C.simple_html}?',
        f'How much {E.simple_html} (in g) could one isolate from {gC.html} g of {C.simple_html}?',
        f'In a {gC.html} g sample of {C.simple_html}, how much {E.simple_html} is present (in g)?'
    ])

    answer = gE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def gC_molE(C):

    gC = sf.random_value((1e-3,1e3),(2,5),True)
    MW_C = C.molecular_weight

    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    MW_E = E.molecular_weight

    molC = gC / (MW_C)
    molE = molC * E_coef

    formatted_question = random.choice([
        f'How many moles of {E.simple_html} are in {gC.html} g of {C.simple_html}?',
        f'How much {E.simple_html} (in mol) could one isolate from {gC.html} g of {C.simple_html}?',
        f'In a {gC.html} g sample of {C.simple_html}, how many moles of {E.simple_html} are present?'
    ])

    answer = molE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def gC_atomE(C):

    gC = sf.random_value((1e-3,1e3),(2,5),True)
    MW_C = C.molecular_weight

    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    MW_E = E.molecular_weight

    molC = gC / (MW_C)
    molE = molC * E_coef
    atomE = molE * 6.02214076e23

    formatted_question = random.choice([
        f'How many atoms of {E.simple_html} are in {gC.html} g of {C.simple_html}?',
        f'How much {E.simple_html} (in atoms) could one isolate from {gC.html} g of {C.simple_html}?',
        f'In a {gC.html} g sample of {C.simple_html}, how many atoms of {E.simple_html} are present?'
    ])

    answer = atomE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def gC_molC(C):

    gC = sf.random_value((1e-3,1e3),(2,5),True)
    MW_C = C.molecular_weight
    molC = gC / (MW_C)

    formatted_question = random.choice([
        f'How many mol of {C.simple_html} are in {gC.html} g of {C.simple_html}?',
        f'How much {C.simple_html} (in mol) could one isolate from {gC.html} g of {C.simple_html}?',
        f'In a {gC.html} g sample of {C.simple_html}, how many moles of {C.simple_html} are present?'
    ])

    answer = molC.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def molC_molE(C):

    molC = sf.random_value((1e-3,1e2),(2,5),True)
    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    molE = molC * E_coef

    formatted_question = random.choice([
        f'How many moles of {E.simple_html} are in {molC.html} mol of {C.simple_html}?',
        f'How much {E.simple_html} (in mol) could one isolate from {molC.html} mol of {C.simple_html}?',
        f'In a {molC.html} mol sample of {C.simple_html}, how many moles of {E.simple_html} are present?'
    ])

    answer = molE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def molC_gE(C):

    molC = sf.random_value((1e-3,1e2),(2,5),True)
    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    MW_E = E.molecular_weight
    molE = molC * E_coef
    gE = molE * MW_E

    formatted_question = random.choice([
        f'How many g of {E.simple_html} are in {molC.html} mol of {C.simple_html}?',
        f'How much {E.simple_html} (in g) could one isolate from {molC.html} mol of {C.simple_html}?',
        f'In a {molC.html} mol sample of {C.simple_html}, how many grams of {E.simple_html} are present?'
    ])

    answer = gE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def molC_atomE(C):

    molC = sf.random_value((1e-3,1e2),(2,5),True)
    e = random.choice(list(C.element_dict.keys()))
    E = molecule(e)
    E_coef = C.element_dict[e]
    MW_E = E.molecular_weight
    molE = molC * E_coef
    atomE = molE * 6.02214076e23

    formatted_question = random.choice([
        f'How many atoms of {E.simple_html} are in {molC.html} mol of {C.simple_html}?',
        f'How much {E.simple_html} (in atoms) could one isolate from {molC.html} mol of {C.simple_html}?',
        f'In a {molC.html} mol sample of {C.simple_html}, how many atoms of {E.simple_html} are present?'
    ])

    answer = atomE.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

def molC_gC(C):

    molC = sf.random_value((1e-3,1e2),(2,5),True)
    MW_C = C.molecular_weight
    gC = molC*MW_C

    formatted_question = random.choice([
        f'How many g of {C.simple_html} are in {molC.html} mol of {C.simple_html}?',
        f'How much {C.simple_html} (in g) could one isolate from {molC.html} mol of {C.simple_html}?',
        f'In a {molC.html} mol sample of {C.simple_html}, how many grams of {C.simple_html} are present?'
    ])

    answer = gC.answers(sf_tolerance=1,roundoff_tolerance=True)
    return formatted_question, answer

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------


def generate_question():
    question_type = 'short_answer'

    question_options = [
        gC_gE,
        gC_molE,
        gC_atomE,
        gC_molC,
        molC_molE,
        molC_gE,
        molC_atomE,
        molC_gC
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

    func = random.choice(question_options)

    formatted_question, answer = func(c)

    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    #question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    #question_text = question_row.split(';')[0]
    #answer_equation = question_row.split(';')[1]

   # Get a dictionary of all local variables
    # namespace = locals()

    # # Replace placeholders in the question with the generated values
    # formatted_question = question_text.format(**namespace)

    # # Calculate the answer using the provided equation
    # answer = eval(answer_equation, globals(), namespace)

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
