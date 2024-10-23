import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import periodictable
from dp_chem import molecule

PT = periodictable.periodictable()

ELEMENTS = [i for i in range(1,31)]
ELEMENTS.extend([35, 36, 53, 54, 80, 86])

def incorrect_answers(correct_answer):
    answers = {'Solid', 'Liquid', 'Gas'}
    answers.remove(correct_answer)
    return ';'.join(list(answers))

#---------------------------------------------------------------------
def generate_question(atomic_number):
    question_type = 'multiple_choice'

    e = PT.element(atomic_number)
        
    formatted_question = f"What phase is {e['name']} at room temperature?"

    if atomic_number in {1,2,7,8,9,10,17,18,36,54,86}:
        answer = "Gas"
    elif atomic_number in {35, 80}:
        answer = "Liquid"
    else:
        answer = "Solid"

    incorrect = incorrect_answers(answer)

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect,
        'question_type': question_type
    }

def generate_questions():
    num_questions = len(ELEMENTS)
    basename = os.path.basename(__file__).removesuffix('.py')
    
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for i in range(num_questions):
        question = generate_question(ELEMENTS[i])
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
