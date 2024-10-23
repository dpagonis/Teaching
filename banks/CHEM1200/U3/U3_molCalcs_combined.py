
import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem.units import units


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Convert {v1.html} {v1_tex} to {v2_tex}. {conversion_html};answers',
    ]


    mass_units = ['kg', 'g', 'mg', 'lb', 'oz']
    volume_units = ['cm3','m3','L','gal']
    energy_units = ['cal','kcal','J','kJ']
    amount_units = ['mol','molecule']

    numerator_units = random.choice([mass_units,volume_units,energy_units])

    numerator_unit = random.choice(numerator_units)
    new_num_unit = None
    amount_unit = random.choice(amount_units)
    first_unit = f'{numerator_unit} {amount_unit}-1'

    if random.choice([True,False]):
        new_num_unit = random.choice([u for u in numerator_units if u != numerator_unit])
        second_unit = f'{new_num_unit} {amount_unit}-1'
    else:
        new_amount_unit = random.choice([u for u in amount_units if u != amount_unit])
        second_unit = f'{numerator_unit} {new_amount_unit}-1'

    if(amount_unit == 'molecule'):
        v1 = sf.random_value((1e-27,1e-24),(2,4),True,units_str=first_unit)
    else:
        v1 = sf.random_value((0.05,20),(2,4),True,units_str=first_unit)
    
    v2_calc = v1.convert_to(second_unit)
    v2 = sf(v2_calc.scientific_notation(),sig_figs=v1.sig_figs,units_str=second_unit)
    

    if new_num_unit:
        u1 = numerator_unit
        u2 = new_num_unit
        conv_factor = units(u1).to_si_factor / units(u2).to_si_factor
        if conv_factor > 1:
            usmall = u2
            ularge = u1
        else:
            usmall = u1
            ularge = u2
            conv_factor = 1/conv_factor
        conv_factor = sf(f'{conv_factor:.5g}',sig_figs=5)
        conversion_html = f'There are {conv_factor.html} {usmall} in one {ularge}.'
    else:
        conversion_html=''
    
    v1_tex = create_mattext_element(v1.units.tex)
    v2_tex = create_mattext_element(v2.units.tex)

    answers = v2.answers(sf_tolerance=1,roundoff_tolerance=True)



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
