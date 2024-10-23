import hashlib
import pandas as pd
import random

from makeqti import *
from sigfig import sigfig as sf

def generate_questions():
    num_questions = 1000
    basename = 'REV_SI_Prefix_Conversions' #this string is used to name the bank and the hash ID
    
    
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
            'distance': ['m', 'ft', 'mi'],
            'time': ['s', 'min', 'h', 'hr', 'day', 'hour'],
            'mass': ['g', 'lb', 'oz'],
            'amount': ['mol', 'molecules'],
            'volume': ['L', 'gal'],
            'energy': ['J','cal'],
            'frequency': ['Hz'],
            'pressure': ['Pa','bar','mmHg','Torr','atm','psi']
        }
    
    si_prefixes = {
            'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3,
            'h': 1e2, 'd': 1e-1, 'c': 1e-2,
            'm': 1e-3, 'µ': 1e-6, 'n': 1e-9, 'p': 1e-12,
            'f': 1e-15, 'a': 1e-18
        }
    
    # Randomly select a category
    category = random.choice(list(unit_categories.keys()))
    units = unit_categories[category]

    # Randomly select base unit
    unit_base  = random.choice(units)
    
    # Randomly select a prefix about 50% of the time
    if random.random() < 0.5:
        x_prefix = random.choice(list(si_prefixes.keys()))
        # Make sure the same prefix isn't used for both units
    else:
        x_prefix = ''
    
    
    if len(x_prefix) == 0 or random.random() < 0.7: 
        y_prefix = x_prefix
        while y_prefix == x_prefix:
            y_prefix = random.choice(list(si_prefixes.keys()))
    else:
        y_prefix = ''
    
    x_unit = x_prefix + unit_base
    y_unit = y_prefix + unit_base

    x = sf.random_value((1,9.999),(2,5),value_log=True,units_str=x_unit)

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
