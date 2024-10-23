import hashlib
import pandas as pd
import random

from makeqti import *
from sigfig import sigfig as sf

def generate_questions():
    num_questions = 1000
    basename = 'U1_Classify_Light_Wavelength_MultChoice' #this string is used to name the bank and the hash ID
    
    
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
    question_type = 'multiple_choice'

    question_options = [
        'What type of electromagnetic radiation is a photon with a wavelength of {lamda_nm} nm?',
        'What type of electromagnetic radiation is a photon with a frequency of {nu_Hz} Hz?',
        'What type of electromagnetic radiation is a photon with an energy of {E_kJmol} kJ/mol?'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    h = 6.62607015e-34
    c = 299792458
    NA = 6.0221408e+23
    i = 0
    
    while True:
        rand = 3*random.random()
        if rand < 1: #UV
            lamda_nm = sf.random_value((50,350),(3,3))
            answer = 'Ultraviolet'
            incorrect_answers = "Visible;Infrared"    
        elif rand < 2: #vis
            lamda_nm = sf.random_value((380,800),(3,3))
            answer = "Visible"
            incorrect_answers = "Ultraviolet;Infrared" 
        else:
            lamda_nm = sf.random_value((850,1200),(3,3))
            answer = "Infrared"
            incorrect_answers = "Ultraviolet;Visible" 
        
        E_kJmol = h * c * NA / (lamda_nm * 1e-9) / 1000
        nu_Hz = c / (lamda_nm * 1e-9)
        
        l1 = 1e9 * c / sf(nu_Hz.scientific_notation())
        lamda_from_nu = True if l1.scientific_notation() == lamda_nm.scientific_notation() else False
        
        E1 = h * sf(nu_Hz.scientific_notation())*NA/1000
        E_from_nu = True if E1.scientific_notation() == E_kJmol.scientific_notation() else False

        l2 = 1e9 * h * c /  (sf(E_kJmol.scientific_notation())*1000/NA)
        lamda_from_E  = True if l2.scientific_notation() == lamda_nm.scientific_notation() else False
        
        nu1 = sf(E_kJmol.scientific_notation()) * 1000/NA/ h
        nu_from_E = True if nu1.scientific_notation() == nu_Hz.scientific_notation() else False

        if all([lamda_from_nu, E_from_nu, lamda_from_E, nu_from_E]): #if all values are self-consistent
            if(i > 100):
                print(i,'iterations to get self-consistent values') # catch inefficient but not terrible code
            break

        if i > 1e6: #catch terrible code
            raise RuntimeError("The loop has gone too far without acheiving self-consistent values!")
    
    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    question_text = question_row.split(';')[0]
    #answer_equation = question_row.split(';')[1]

   # Get a dictionary of all local variables
    namespace = locals()

    # Replace placeholders in the question with the generated values
    formatted_question = question_text.format(**namespace)

    # Calculate the answer using the provided equation
    #answer = eval(answer_equation, globals(), namespace)

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect_answers,
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
