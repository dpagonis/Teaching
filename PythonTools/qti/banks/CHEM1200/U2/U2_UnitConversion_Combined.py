
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
        'Convert {v1.html} {tex1} to {tex2}. There are {conv_factor.html} {usmall} in one {ularge}.;a_list',
    ]


    distance_units = ['m', 'km', 'ft', 'mi']
    time_units = ['s', 'hr', 'min']
    mass_units = ['kg', 'g', 'mg', 'lb', 'oz']
    volume_units = ['cm3']
    energy_units = ['J','cal','kJ','kcal']
    
    cases = ['speed', 'density', 'mass_rate','energy_rate','mileage']
    case = random.choice(cases)

    if case == 'speed':
        if random.choice([True,False]):
            u1,u2 = random.sample(distance_units,2)
            u3 = random.choice(time_units)
            cu1 = f'{u1} {u3}-1'
            cu2 = f'{u2} {u3}-1'
        else:
            u1,u2 = random.sample(time_units,2)
            u3 = random.choice(distance_units)
            cu1 = f'{u3} {u1}-1'
            cu2 = f'{u3} {u2}-1'
    elif case == 'density':
        u1,u2 = random.sample(mass_units,2)
        u3 = 'cm-3'
        cu1 = f'{u1} {u3}'
        cu2 = f'{u2} {u3}'
    elif case == 'mass_rate':
        if random.choice([True,False]):
            u1,u2 = random.sample(mass_units,2)
            u3 = random.choice(time_units)
            cu1 = f'{u1} {u3}-1'
            cu2 = f'{u2} {u3}-1'
        else:
            u1,u2 = random.sample(time_units,2)
            u3 = random.choice(mass_units)
            cu1 = f'{u3} {u1}-1'
            cu2 = f'{u3} {u2}-1'
    elif case == 'energy_rate':
        if random.choice([True,False]):
            u1,u2 = random.sample(energy_units,2)
            u3 = random.choice(time_units)
            cu1 = f'{u1} {u3}-1'
            cu2 = f'{u2} {u3}-1'
        else:
            u1,u2 = random.sample(time_units,2)
            u3 = random.choice(energy_units)
            cu1 = f'{u3} {u1}-1'
            cu2 = f'{u3} {u2}-1'
    elif case == 'mileage':
        u1,u2 = random.sample(distance_units,2)
        u3 = 'gal'
        cu1 = f'{u1} {u3}-1'
        cu2 = f'{u2} {u3}-1'

    
    v1 = sf.random_value((1e-3,1e3),(2,5),value_log=True,units_str=cu1)
    v2 = v1.convert_to(cu2)
    conv_factor = units(u1).to_si_factor / units(u2).to_si_factor
    if conv_factor > 1:
        usmall = u2
        ularge = u1
    else:
        usmall = u1
        ularge = u2
        conv_factor = 1/conv_factor
    conv_factor = sf(f'{conv_factor:.5g}',sig_figs=5)
    
    tex1 = create_mattext_element(units(cu1).tex)
    tex2 = create_mattext_element(units(cu2).tex)

    a_list = v2.answers(sf_tolerance=1,roundoff_tolerance=True)
    
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
