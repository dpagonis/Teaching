import hashlib
import pandas as pd
import random

from makeqti import *
from sigfig import sigfig as sf

def generate_questions():
    num_questions = 1000
    basename = 'REV_Unit_Conversions_NoPrefixes' #this string is used to name the bank and the hash ID
    
    
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
        'Convert {x} {x_unit} to {y_unit}; x.convert_to(y_unit).answers()'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    
    unit_categories = {
            'distance': ['m', 'ft', 'in', 'mi'],
            'time': ['s', 'min', 'hr', 'day'],
            'mass': ['g', 'lb', 'oz'],
            'amount': ['mol', 'molecules'],
            'volume': ['L', 'gal'],
            'energy': ['J','cal'],
            'pressure': ['Pa','bar','mmHg','Torr','atm','psi'],
            'temperature': ['K', 'C', 'F']
        }
    
    
    # Randomly select a category
    category = random.choice(list(unit_categories.keys())) if random.random() > 0.3 else 'pressure'
    units = unit_categories[category]

    if category == 'temperature':
        x_unit,y_unit = random.sample(units,2)
        if x_unit == 'K':
            temp_range = (250,350)
        elif x_unit == 'C':
            temp_range = (-50,250)
        else:
            temp_range = (-50,300)
        x = sf.random_value(temp_range,(2,5),units_str=x_unit)
    else:
        # Randomly select two different units
        x_unit, y_unit = random.sample(units,2)

        x = sf.random_value((1e-3,1e3),(2,5),value_log=True,units_str=x_unit)
    
    

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
