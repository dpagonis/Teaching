
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
        'Calculate the density of a material (in {density_unit_html}) given the following data:<br>Mass = {mass.html} {mass_unit}<br>Volume = {volume.html} {volume_unit_html}<br>{conversion_html};density_answer_list',
        'Calculate the density of a material (in {density_unit_html}) given the following data:<br>Volume = {volume.html} {volume_unit_html}<br>Mass = {mass.html} {mass_unit}<br>{conversion_html};density_answer_list',
        'What is the mass of a sample (in {mass_unit}) whose density is {density.html} {density_unit_html} and whose volume is {volume.html} {volume_unit_html}.<br>{conversion_html};mass_answer_list',
        'What is the mass of a sample (in {mass_unit}) whose volume is {volume.html} {volume_unit_html} and whose density is {density.html} {density_unit_html}.<br>{conversion_html};mass_answer_list',
        'A sample has a density of {density.html} {density_unit_html} and a mass of {mass.html} {mass_unit}. Calculate the volume of the sample in {volume_unit_html}<br>{conversion_html};volume_answer_list',
        'A sample has a mass of {mass.html} {mass_unit} and a density of {density.html} {density_unit_html}. Calculate the volume of the sample in {volume_unit_html}<br>{conversion_html};volume_answer_list'
    ]


    mass_units = ['kg', 'g', 'mg', 'lb', 'oz']
    volume_units = ['cm3','m3','L','gal']

    mass_unit = random.choice(mass_units)
    volume_unit = random.choice(volume_units)
    new_vol_unit = None 
    new_mass_unit = None

    if random.choice([True,False]):
        new_vol_unit = random.choice([u for u in volume_units if u != volume_unit])
        density_unit = f'{mass_unit} {new_vol_unit}-1'
    else:
        new_mass_unit = random.choice([u for u in mass_units if u != mass_unit])
        density_unit = f'{new_mass_unit} {volume_unit}-1'

    density_unit = density_unit.replace("3-1","-3")


    volume_unit_html = volume_unit.replace("3","<sup>3</sup>")


    if "-3" in density_unit:
        density_unit_html = density_unit.replace("-3","<sup>-3</sup>")
    elif "-1" in density_unit:
        density_unit_html = density_unit.replace("-1","<sup>-1</sup>")


    #make the numbers, check for self consistency
    while True:
        density_gcm3 = sf.random_value((0.5,20),(2,4),units_str="g cm-3")
        density = density_gcm3.convert_to(density_unit)

        mass = sf.random_value((1,3000),(2,4),True,units_str=mass_unit)
        mass_g = mass.convert_to('g')
        
        v_cm3 = mass_g/density_gcm3
        volume_cm3 = sf(str(v_cm3.value),sig_figs=v_cm3.sig_figs, units_str='cm3')
        volume = volume_cm3.convert_to(volume_unit)


        displayed_volume = sf(volume.scientific_notation(), units_str=volume_unit)


        mass_calc_vol_unit = (volume_unit+'-1').replace('3-1','-3')
        mass_calc = density.convert_to(f'{mass_unit} {mass_calc_vol_unit}') * displayed_volume
        mass_check = sf(str(mass.value),sig_figs=mass_calc.sig_figs).scientific_notation() == mass_calc.scientific_notation()
        
        if new_vol_unit:
            density_calc = mass / displayed_volume.convert_to(new_vol_unit)
            density_check = sf(str(density.value),sig_figs=density_calc.sig_figs).scientific_notation() == density_calc.scientific_notation()
        else:
            density_calc = mass.convert_to(new_mass_unit) / displayed_volume
            density_check = sf(str(density.value),sig_figs=density_calc.sig_figs).scientific_notation() == density_calc.scientific_notation()

        if mass_check and density_check:
            break

    if new_vol_unit:
        u1 = volume_unit
        u2 = new_vol_unit
    else:
        u1 = mass_unit
        u2 = new_mass_unit
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


    mass_answer_list = mass_calc.answers(sf_tolerance=1,roundoff_tolerance=True)
    volume_answer_list = volume.answers(sf_tolerance=1,roundoff_tolerance=True)
    density_answer_list = density_calc.answers(sf_tolerance=1,roundoff_tolerance=True)



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
