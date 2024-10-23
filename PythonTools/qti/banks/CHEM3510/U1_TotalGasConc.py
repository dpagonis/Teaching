import hashlib
import pandas as pd
import random

from dp_qti.makeqti import *
from dp_qti import sf

def generate_questions():
    num_questions = 1000
    basename = 'U1_TotalGasConc' #this string is used to name the bank and the hash ID
    
    
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

def PT_to_N():

    temp = sf.random_value((250,310),(2,4))
    pres = sf.random_value((600,1013),(3,5))
    
    N = 6.02214076e23 * (pres*100) * 1e-6 / (8.3145 * temp)

    answers = N.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Calculate the concentration of molecules in air (in molecules cm<sup>-3</sup>) at {temp} K and {pres} mbar.',
        f'Calculate the concentration of molecules in air (in molecules cm<sup>-3</sup>) at {pres} mbar and {temp} K.',
        f'The pressure and temperature of a sample are {pres} mbar and {temp} K. Calculate the concentration of gas in this sample in molecules cm<sup>-3</sup>.',
        f'The pressure and temperature of a sample are {temp} K and {pres} mbar. Calculate the concentration of gas in this sample in molecules cm<sup>-3</sup>.',
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 

def NT_to_P():

    temp = sf.random_value((250,310),(2,4))
    N = sf.random_value((1e19,2.9e19),(3,5))
    
    pres = ((N/6.02214076e23) * 8.3145 * temp / 1e-6)/100

    answers = pres.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Calculate the pressure of a parcel (in mbar) if the total gas concentration is {N} molecules cm<sup>-3</sup> and the temperature is {temp} K',
        f'An airmass at {temp} K has a total gas concentration of {N} molecules cm<sup>-3</sup>. What is the pressure of this airmass in mbar?'
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 

def NP_to_T():

    pres = sf.random_value((600,1013),(3,5))
    N = sf.random_value((1e19,2.9e19),(3,5))

    temp = (pres*100) * 1e-6 / ((N/6.02214076e23) * 8.3145)

    answers = temp.answers(sf_tolerance=1,roundoff_tolerance=True)

    question_options = [
        f'Calculate the temperature of a parcel (in K) if the total gas concentration is {N} molecules cm<sup>-3</sup> and the pressure is {pres} mbar',
        f'An airmass at {pres} mbar has a total gas concentration of {N} molecules cm<sup>-3</sup>. What is the temperature of this airmass in Kelvin?'
    ]

    formatted_question = random.choice(question_options)

    return formatted_question, answers 


def generate_question():
    question_type = 'short_answer'

    question_options = [
        PT_to_N,
        NT_to_P,
        NP_to_T,
    ]

    func = random.choice(question_options)
    formatted_question, answer = func()

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
