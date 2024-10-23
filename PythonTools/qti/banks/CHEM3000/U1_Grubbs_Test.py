import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf
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
        'Is the measurement {qv} {unit} an outlier in the following dataset?<br>{x} {unit}, n={x.n};yes_no(outlier_bool)',
        'Can you reject the measurement {qv} {unit} as an outlier in the following dataset?<br>{x} {unit}, n={x.n};yes_no(outlier_bool)',
        'What is the calculated G value for the questionable value {qv} {unit} in the following dataset?<br>{x} {unit}, n={x.n};G_calc.answers()',
        'What is the tabulated G value for the following dataset?<br>{x} {unit}, n={x.n};G_table'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here

    unit = random.choice(['bar', 'mbar', 'atm', 'Pa', 'kPa', 'Torr', 'mmHg', 'kg', 'g', 'mol', 'A', 'mA', 'V', 'kV', 'm', 'km', 'nm', 's', 'ms', 'ns', 'yr', 'h', 'L', 'mL', 'M', 'mM', 'K', 'J', 'kJ', 'cal', 'kcal', 'N', 'W', 'Hz'])

    n = random.choice([3,4,5,6,7,8,9,10,11,12,15,20,30,50])

    x = uv.random_value((1e-2,1e4),(0.01,0.5),n_range=(n,n),mean_log=True,stdev_relative=True,no_hidden_digits=True)
    
    df = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/grubbs.txt')
    G_table = df[df['N'] == n]['g_crit'].values[0]
    
    while True:
        qv = sf((x.mean + (random.choice([-1,1]) * random.uniform(0.8,1.2) * (G_table*x.stdev))).scientific_notation())
        if qv.value > 0:
            break

    G_calc = abs(qv.value-x.mean.value)/x.stdev 

    outlier_bool = True if G_calc.value > G_table else False

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

def yes_no(bool):
    if bool:
        return "Yes;yes;Y;y"
    else:
        return "No;no;N;n"

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
