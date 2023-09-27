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

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the concentration of molecules in air at {temp} K and {pres} mbar.;conc.answers(sf_tolerance=1)',
        'The concentration of molecules in an air sample is {conc} molecules cm-3 at {temp} K. Calculate the pressure of this sample in mbar.;pres.answers(sf_tolerance=1)',
        'The pressure and temperature of a sample are {pres} mbar and {temp_C} C. Calculate the concentration of gas in this sample in molecules cm-3.;conc.answers(sf_tolerance=1)',
        'The concentration of molecules in an air sample is {conc} molecules cm-3 at {pres} mbar. Calculate the temperature of this sample in K.;temp.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    R = 8.3145
    NA = 6.0221408e+23
    i = 0
    
    while True:
        temp = sf.random_value((250,310),(3,4),units_str='K')
        temp_C = temp.convert_to('C')
        pres = sf.random_value((400,1200),(3,4))
        v=1e-6 #1 cm3
        conc = (pres*100) * v / (R * temp) * NA

        T_check = (pres*100) * v / (R * conc) * NA
        P_check = (conc * R * temp) / (v * NA) / 100
        conc_degC_check = (pres*100) * v / (R * (temp_C+273.15)) * NA

        temp_from_conc = True if T_check.scientific_notation() == temp.scientific_notation() else False
        pres_from_conc = True if P_check.scientific_notation() == pres.scientific_notation() else False
        conc_from_C = True if conc_degC_check.scientific_notation() == conc.scientific_notation() else False

        if all([temp_from_conc, pres_from_conc, conc_from_C]): #if all values are self-consistent
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
