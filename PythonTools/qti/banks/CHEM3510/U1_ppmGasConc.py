import hashlib
import pandas as pd
import random

from dp_qti.makeqti import *
from dp_qti import sf

molecs = pd.read_csv('U1_ppmGasConc_molecules.txt')

def generate_questions():
    num_questions = 1000
    basename = 'U1_ppmGasConc' #this string is used to name the bank and the hash ID
    
    
    #####------------Rest of this function stays constant, move to generate_question()--------#####
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for _ in range(num_questions):
        question = generate_question()
        questions.append(question)

    questions_df = pd.DataFrame(questions)
    return questions_df, basename, assessment_ident

def ppm_to_n():

    molecule = random.choice(['ozone', 'NO', 'NO<sub>2</sub>', 'HNO<sub>3</sub>', 'CH<sub>4</sub>', 'methane', 'carbon monoxide'])

    ppm = sf.random_value((0.1,10),(2,4),True)
    temp = sf.random_value((250,310),(2,4))
    pres = sf.random_value((700,1013),(3,5))
    
    N = 6.02214076e23 * (pres*100) * 1e-6 / (8.3145 * temp)
    n = N * ppm * 1e-6
    answers = n.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Assume {molecule} has a concentration of {ppm} ppm at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in molecules cm<sup>-3</sup>.',
        f'Assume {molecule} has a concentration of {ppm} ppm at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in molecules cm<sup>-3</sup>.',
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 


def ppb_to_n():

    molecule = random.choice(['ozone', 'NO', 'NO<sub>2</sub>', 'HNO<sub>3</sub>', 'CH<sub>4</sub>', 'methane', 'carbon monoxide'])

    ppb = sf.random_value((1,100),(2,4),True)
    temp = sf.random_value((250,310),(2,4))
    pres = sf.random_value((700,1013),(3,5))
    
    N = 6.02214076e23 * (pres*100) * 1e-6 / (8.3145 * temp)
    n = N * ppb * 1e-9
    answers = n.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Assume {molecule} has a concentration of {ppb} ppb at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in molecules cm<sup>-3</sup>.',
        f'Assume {molecule} has a concentration of {ppb} ppb at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in molecules cm<sup>-3</sup>.',
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 

def n_to_ppm():

    molecule = random.choice(['ozone', 'NO', 'NO<sub>2</sub>', 'HNO<sub>3</sub>', 'CH<sub>4</sub>', 'methane', 'carbon monoxide'])

    n = sf.random_value((1e12,1e15),(2,4),True)
    temp = sf.random_value((250,310),(2,4))
    pres = sf.random_value((700,1013),(3,5))
    
    N = 6.02214076e23 * (pres*100) * 1e-6 / (8.3145 * temp)
    ppm = 1e6 * n / N
    
    answers = ppm.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in parts per million.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in ppm.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in parts per million.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in ppm.',
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 

def n_to_ppb():

    molecule = random.choice(['ozone', 'NO', 'NO<sub>2</sub>', 'HNO<sub>3</sub>', 'CH<sub>4</sub>', 'methane', 'carbon monoxide'])

    n = sf.random_value((1e19,1e13),(2,4),True)
    temp = sf.random_value((250,310),(2,4))
    pres = sf.random_value((700,1013),(3,5))
    
    N = 6.02214076e23 * (pres*100) * 1e-6 / (8.3145 * temp)
    ppb = 1e9 * n / N
    
    answers = ppb.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in parts per billion.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {temp} K and {pres} mbar. Calculate the concentration of {molecule} in this sample in ppb.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in parts per billion.',
        f'Assume {molecule} has a concentration of {n.html} molecules cm<sup>-3</sup> at {pres} mbar and {temp} K. Calculate the concentration of {molecule} in this sample in ppb.',
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 

def generate_question():
    question_type = 'short_answer'

    question_options = [
        n_to_ppm,
        n_to_ppb,
        ppm_to_n,
        ppb_to_n
    ]

    func = random.choice(question_options)
    formatted_question, answer = func()

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'question_type': question_type
    }

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'The concentration of {gas} in an air sample is {conc} molecules cm-3 at {temp} K and {pres} mbar. Calculate the mixing ratio in ppm.;ppm.answers(sf_tolerance=1)',
        'The concentration of {gas} in an air sample is {conc_ppb} molecules cm-3 at {temp} K and {pres} mbar. Calculate the mixing ratio in ppb.;ppm.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    R = 8.3145
    NA = 6.0221408e+23
    i = 0

    gasrow = molecs.sample(1)
    gas = gasrow['name'].values[0]
    
    while True:
        temp = sf.random_value((250,310),(3,4),units_str='K')
        pres = sf.random_value((400,1200),(3,4))
        v=1e-6 #1 cm3
        ppm = sf.random_value((0.1,1200),(2,4))
        c_tot = (pres*100) * v / (R * temp) * NA
        conc = (ppm * 1e-6) * c_tot
        conc_ppb = conc/1000

        ppm_check = 1e6 * conc / c_tot

        ppm_from_conc = True if ppm_check.scientific_notation() == ppm.scientific_notation() else False
        
        if all([ppm_from_conc]): #if all values are self-consistent
            if(i > 100):
                print(i,'iterations to get self-consistent values') # catch inefficient but not terrible code
            break

        if i > 1e6: #catch terrible code
            raise RuntimeError("The loop has gone too far without acheiving self-consistent values!")
    
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
