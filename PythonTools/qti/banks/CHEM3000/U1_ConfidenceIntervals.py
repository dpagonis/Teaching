import hashlib
import pandas as pd
import random

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import uncertainvalue as uv

def generate_questions():
    num_questions = 1000
    basename = 'U1_ConfidenceIntervals' #this string is used to name the bank and the hash ID
    
    
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
        'Calculate the {conf_level} % confidence interval for the following measurement.<br>{x} {unit}, n = {x.n}<br>Use the ± symbol in your answer.;ci.answers()',
        'Calculate the {conf_level} % confidence interval for the following measurement.<br>{x} {unit}, n = {x.n}<br>Use the ± symbol in your answer.;ci.answers()',
        'Is the value {val} {unit} in the {conf_level} % confidence interval for the following measurement?<br>{x} {unit}, n = {x.n};yes_no(Ho)',
        'Does the following measurement agree with the known value of {val} {unit} at the {conf_level} % confidence level?<br>{x} {unit}, n = {x.n};yes_no(Ho)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    levels = [50,90,95,99,99.9]
    conf_level = random.choice(levels)

    units = ['bar', 'mbar', 'atm', 'Pa', 'kPa', 'Torr', 'mmHg', 'kg', 'g', 'mol', 'A', 'mA', 'V', 'kV', 'm', 'km', 'nm', 's', 'ms', 'ns', 'yr', 'h', 'L', 'mL', 'M', 'mM', 'K', 'J', 'kJ', 'cal', 'kcal', 'N', 'W', 'Hz']
    unit = random.choice(units)

    n = random.choice([3,4,5,6,7,8,9,10,15,20,25,30,40,60,120])

    x = uv.random_value((1e-2,1e4),(0.01,0.5),n_range=(n,n),mean_log=True,stdev_relative=True,no_hidden_digits=True)
    ci = uv(x.mean,x.ci(confidence_level=conf_level),x.n)
    
    val = sf((x.mean + (random.choice([-1,1]) * random.uniform(0.5,1.5) *x.ci(confidence_level=conf_level))).scientific_notation())

    Ho = True if val.value < ci.mean.value+ci.stdev.value and val.value > ci.mean.value-ci.stdev.value else False

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
