import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf

molecules = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/organics.csv')

def generate_question():
    question_type = 'short_answer'

    question_options = [
        '{name} has an octanol-water partitioning coefficient of {Kow}. What percentage of {name} will be found in the aqueous phase if {grams} g of {name} partitions between {V_aq} L of water and {V_oct} L of octanol?;pct_aq.answers(sf_tolerance=1,roundoff_tolerance=True)' 
    ]

    while True:
        row=molecules.sample(1)
        name = (row['Molecule Name'].values[0]).lower()
        Kow = row['K_ow'].values[0]
        # Check if Kow is not NaN
        
        if not pd.isna(Kow):
            break
    
    grams = sf.random_value(value_log=True)
    V_aq = sf.random_value((1,1000),(2,3),value_log=True)
    V_oct = sf.random_value((V_aq.value/100,V_aq.value*100),(2,3),value_log=True)
    
    mass_aq = grams / (1+(V_oct*Kow/V_aq))
    pct_aq = 100 * mass_aq/grams


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
