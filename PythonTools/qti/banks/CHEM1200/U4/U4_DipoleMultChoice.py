import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import molecule

def incorrect_answers(correct_answer):
    answers = {"Need to know molecule's shape", "Non-polar", "Polar"}
    answers.remove(correct_answer)
    return ';'.join(list(answers))

#---------------------------------------------------------------------
def generate_question(row):
    question_type = 'multiple_choice'

    m = molecule(row['formula'])

    formatted_question = f"Select the polarity of {m.simple_html}."

    answer = row['polarity']

    incorrect = incorrect_answers(answer)

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect,
        'question_type': question_type
    }

def generate_questions():
    
    df = pd.read_csv('U4_DipoleMultChoice_Inputs.csv')
    num_questions = len(df)
    basename = os.path.basename(__file__).removesuffix('.py')
    
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for i in range(num_questions):
        question = generate_question(df.iloc[i])
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
