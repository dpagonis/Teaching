import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import uncertainvalue as uv

def generate_questions():
    num_questions = 1000
    basename = os.path.basename(__file__).rstrip('.py') #this string is used to name the bank and the hash ID
    
    
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
        '{x} + {y} = ?<br>Use the ± symbol in your answer.;sum.answers()',
        '{x} - {y} = ?<br>Use the ± symbol in your answer.;difference.answers()',
        '{x} × {y} = ?<br>Use the ± symbol in your answer.;product.answers()',
        '{x} ÷ {y} = ?<br>Use the ± symbol in your answer.;division.answers()'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    x = uv.random_value((1e-2,1e4),(0.01,0.5),mean_log=True,stdev_relative=True,no_hidden_digits=True)
    y = uv.random_value((x.mean.value*0.1,x.mean.value*10),(0.01,0.5),mean_log=True,stdev_relative=True,no_hidden_digits=True)

    sum = x + y
    difference = x - y
    product = x*y
    division = x / y

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
