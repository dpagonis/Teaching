
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
        'Calculate the density of a material (in {mass_unit}/{volume_unit}) given the following data:<br>Mass = {massA.html} {mass_unit}<br>Volume = {volumeA.html} {volume_unit};A_list',
        'Calculate the density of a material (in {mass_unit}/{volume_unit}) given the following data:<br>Volume = {volumeA.html} {volume_unit}<br>Mass = {massA.html} {mass_unit};A_list',
        'What is the mass of a sample (in {mass_unit}) whose density is {densityB.html} {mass_unit}/{volume_unit} and whose volume is {volumeB.html} {volume_unit}.;B_list',
        'What is the mass of a sample (in {mass_unit}) whose volume is {volumeB.html} {volume_unit} and whose density is {densityB.html} {mass_unit}/{volume_unit}.;B_list',
        'A sample has a density of {densityC.html} {mass_unit}/{volume_unit} and a mass of {massC.html} {mass_unit}. Calculate the volume of the sample in {volume_unit};C_list',
        'A sample has a mass of {massC.html} {mass_unit} and a density of {densityC.html} {mass_unit}/{volume_unit}. Calculate the volume of the sample in {volume_unit};C_list'
    ]


    unit_pairs = [
        ('g','cm<sup>3</sup>'),
        ('g','mL'),
        ('kg','m<sup>3</sup>')
    ]

    mass_unit, volume_unit = random.choice(unit_pairs)


    # case A: calculating density from mass and volume
    if mass_unit == 'g':
        massA = sf.random_value((1e-2,1e4),(2,4),value_log=True)
        volume_range = (massA.value/20,2*massA.value)
    else:
        massA = sf.random_value((1e2,1e5),(2,4),value_log=True)
        volume_range = (massA.value/20_000,massA.value/500) 
    volumeA = sf.random_value(volume_range,(2,4))
    densityA = massA/volumeA
    A_list = densityA.answers(sf_tolerance=1,roundoff_tolerance=True)

    #case B: calculate mass from density and volume
    if mass_unit == 'g':
        densityB = sf.random_value((0.5,20),(2,4),value_log=True)
    else:
        densityB = sf.random_value((500,20_000),(2,4),value_log=True)

    volumeB = sf.random_value((1e-1,1e3),(2,4),value_log=True)
    
    massB = densityB*volumeB
    B_list = massB.answers(sf_tolerance=1,roundoff_tolerance=True)

    #case C: calculate volume from density and mass
    if mass_unit == 'g':
        densityC = sf.random_value((0.5,20),(2,4),value_log=True)
    else:
        densityC = sf.random_value((500,20_000),(2,4),value_log=True)
    
    massC = sf.random_value((10,1e5),(2,4),value_log=True)
    volumeC = massC/densityC
    C_list = volumeC.answers(sf_tolerance=1,roundoff_tolerance=True)


    
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
