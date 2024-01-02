import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import periodictable

PT = periodictable.periodictable()

def generate_question():
    question_type = 'short_answer'

    #list of strings
    #each string is semicolon-separated: "question text; answers"
    question_options = [
        'What is the atomic number of {element_name}?;atomic_number',
        'What element has {atomic_number} protons in its nucleus?;name_symbol_answers',
        'What is the name of the element with symbol {symbol}?;name_answers'
    ]


    element_dict = PT.random(weighted=True)
    #this is a dictionary
    
    element_name = element_dict['name']
    atomic_number = element_dict['atomic_number']
    symbol = element_dict['symbol']

    name_upper = element_name.capitalize()
    name_lower = element_name.lower()
    name_answers = f"{name_upper};{name_lower}"

    name_symbol_answers = name_answers+";"+symbol

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
