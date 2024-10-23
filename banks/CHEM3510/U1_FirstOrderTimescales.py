import hashlib
import pandas as pd
import random

from dp_qti.makeqti import *
from dp_qti import sf

def generate_questions():
    num_questions = 1000
    basename = 'U1_FirstOrderTimescales' #this string is used to name the bank and the hash ID
    
    
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

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'The rate constant of a first-order reaction is {k} s-1. Calculate the timescale of this reaction in s;tau.answers(sf_tolerance=1)',
        'The rate constant of a first-order reaction is {k} s-1. Calculate the timescale of this reaction in s;tau.answers(sf_tolerance=1)',
        'A first-order reaction has a timescale of {tau} s. Calculate the rate constant in units of s-1;k.answers(sf_tolerance=1)',
        'A first-order reaction has a timescale of {tau_min} min. Calculate the rate constant in units of s-1;k.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    i = 0
    
    while True:
        tau = sf.random_value((1e-6,1e5),(1,4),units_str='s',value_log=True)
        k= 1/tau
        tau_min = tau.convert_to('min')

        tau_check = 1 / sf(str(k))
        k_check = (1/(60*sf(str(tau_min))))
        
        tau_from_k = True if tau_check.scientific_notation() == tau.scientific_notation() else False
        k_from_taumin = True if k_check.scientific_notation() == k.scientific_notation() else False 

        if all([tau_from_k, k_from_taumin]): #if all values are self-consistent
            if(i > 100):
                print(i,'iterations to get self-consistent values') # catch inefficient but not terrible code
            break

        if i > 1e6: #catch terrible code
            raise RuntimeError("The loop has gone too far without acheiving self-consistent values!")
        
        i += 1
    
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
