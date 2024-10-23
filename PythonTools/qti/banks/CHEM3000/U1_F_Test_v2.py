import hashlib
import pandas as pd
import random
import numpy as np
from scipy.stats import f

from dp_qti.makeqti import *
from dp_chem import uncertainvalue as uv
from dp_chem import sigfig as sf

def generate_questions():
    num_questions = 1000
    basename = 'F_test' #this string is used to name the bank and the hash ID

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
    question_type = 'short_answer_question'

    question_options = [
        'Given the following measurements calculate F:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n};Fcalc.answers(sf_tolerance=1)',
        'Calculate the F statistic for the following measurements:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n};Fcalc.answers(sf_tolerance=1)',
        'Give the tabulated F value (F_table) for the following measurements:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n};Ftable.answers()',
        'Are the following standard deviations significantly different?<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}; yes_no(not Ho)',
        'Do the standard deviations of these measurements agree within experimental error?<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}; yes_no(Ho)'
    ]

    # generating random values for variables & prepping namespace here
    x = uv.random_value(mean_range=(1e-3,1e3),stdev_range=(1e-3,0.5),stdev_relative=True, mean_log=True)
    y = uv.random_value(mean_range=(x.mean * 0.1, x.mean * 10), stdev_range=(1e-3,0.5),stdev_relative=True)
    unit = get_random_unit()
    n1 = x.n if x.stdev.value > y.stdev.value else y.n
    n2 = y.n if x.stdev.value > y.stdev.value else x.n
    
    Fcalc = sf(str((max(x.stdev.value,y.stdev.value)/min(x.stdev.value,y.stdev.value))**2), sig_figs=2)
    Ftable = sf(str(f.ppf(1 - 0.05/2, n1, n2)),last_decimal_place=-2)

    Ho = True if Fcalc.value < Ftable.value else False

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

def get_random_unit():
    units = np.loadtxt('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/units.txt', dtype='str')
    return random.choice(units)

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
