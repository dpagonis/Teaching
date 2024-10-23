import hashlib
import pandas as pd
import random
import numpy as np
from scipy.stats import f
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import uncertainvalue as uv
from dp_chem import sf

def generate_questions():
    num_questions = 1000
    basename = os.path.basename(__file__).rstrip('.py') #this string is used to name the bank and the hash ID

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
        'Given the following measurements calculate t:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n},<br>Use 95% confidence level;t_calc.answers(sf_tolerance=1)',
        'Calculate the t statistic for the following measurements:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}<br>Use 95% confidence level;t_calc.answers(sf_tolerance=1)',
        'Give the tabulated t value (t_table) for the following measurements:<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}<br>Use 95% confidence level;t_table.answers()',
        'Are the following measurements significantly different?<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}<br>Use 95% confidence level; yes_no(not Ho)',
        'Do these measurements agree within experimental error?<br>{x} {unit}, n={x.n}<br>{y} {unit}, n={y.n}<br>Use 95% confidence level; yes_no(Ho)'
    ]

    # generating random values for variables & prepping namespace here
    x = uv.random_value(mean_range=(1e-3,1e3),stdev_range=(1e-3,0.5),n_range=(3,6),stdev_relative=True, mean_log=True)
    y = uv.random_value(mean_range=(x.mean.value/2, x.mean.value*2), stdev_range=(1e-3,0.5),n_range=(3,6),stdev_relative=True)
    
    unit = random.choice(['bar', 'mbar', 'atm', 'Pa', 'kPa', 'Torr', 'mmHg', 'kg', 'g', 'mol', 'A', 'mA', 'V', 'kV', 'm', 'km', 'nm', 's', 'ms', 'ns', 'yr', 'h', 'L', 'mL', 'M', 'mM', 'K', 'J', 'kJ', 'cal', 'kcal', 'N', 'W', 'Hz'])
    
    n1 = x.n if x.stdev.value > y.stdev.value else y.n
    n2 = y.n if x.stdev.value > y.stdev.value else x.n
    
    Fcalc = sf(str((max(x.stdev.value,y.stdev.value)/min(x.stdev.value,y.stdev.value))**2), sig_figs=2)
    Ftable = sf(str(f.ppf(1 - 0.05/2, n1, n2)),last_decimal_place=-2)

    F_Ho = True if Fcalc.value < Ftable.value else False

    if F_Ho: #pool the stdevs
        s_pooled = ((x.stdev**2 *(x.n-1)+y.stdev**2 * (y.n-1))/(x.n+y.n-2))**0.5
        t_calc = abs(x.mean.value-y.mean.value)*(n1*n2/(n1+n2))**0.5/s_pooled
        degrees_of_freedom = n1 + n2 - 2
    
    else: #don't pool them
        ux = x.stdev/(x.n**0.5)
        uy = y.stdev/(y.n**0.5)
        t_calc = abs(x.mean.value-y.mean.value)/(ux**2+uy**2)**0.5
        dof_calc = (ux**2+uy**2)**2/((ux**4/(x.n-1))+(uy**4/(y.n-1)))
        degrees_of_freedom = sf(str(dof_calc),last_decimal_place=0).value
    
    t_table = sf(str(t.ppf(1 - 0.05/2, degrees_of_freedom)),last_decimal_place=-3)
    Ho = True if t_calc.value < t_table.value else False


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
