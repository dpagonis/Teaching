import hashlib
import pandas as pd
import random

from makeqti import *
from sigfig import sigfig as sf

def generate_questions():
    num_questions = 1000
    basename = 'REV_SigFigs' #this string is used to name the bank and the hash ID
    
    
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
        '{x} + {y} = ?; (x+y).answers()',
        '{x} - {y} = ?; (x-y).answers()',
        '{x} x {y} = ?; (x*y).answers()',
        '{x} ÷ {y} = ?; (x/y).answers()',
        'ln({w}) = ?; w.ln().answers()',
        'e^{z} = ?; z.exponent().answers()'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    x = sf.random_value((1e-3,1e3),(2,5),value_log=True)
    y = sf.random_value((x.value*0.2,x.value*5),(2,5))
    z = sf.random_value((1e-4,3),(3,5),value_log=True)
    w = sf.random_value((1e-2,100),(2,5),value_log=True)

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
