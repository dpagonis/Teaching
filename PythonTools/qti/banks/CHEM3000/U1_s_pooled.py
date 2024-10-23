#sigmas need to be 1 or 2 sig-fig values when passed to uv

from scipy.stats import f
import hashlib
import pandas as pd
import random
import math
import numpy as np
import os

from dp_qti.makeqti import *
from dp_chem import uncertainvalue as uv
from dp_chem import sf


def generate_questions():
    basename = os.path.basename(__file__).rstrip('.py') #this string is used to name the bank and the hash ID
    
    num_questions = 1000    #recommend 1000

    question_type = 'short_answer_question'
        
    float_vars_logdist = 'xbar;ybar;sigma_x'
    ranges = '1,100; 0.11,100;0.12,30'
    float_vars_logdist_ranges = [(float(rng.split(',')[0]), float(rng.split(',')[1])) for rng in ranges.split(';')]

    int_vars = 'nx;ny'
    ranges = '3,20; 3,20'
    int_var_ranges = [(int(rng.split(',')[0]), int(rng.split(',')[1])) for rng in ranges.split(';')]
    
    str_vars = ['unit']

    intermediate_calcs = 'n1;n2;F_table;sigma_y;x;y;s_pooled'
    intermediate_equations = [  
        'nx',
        'ny',
        'f.ppf(1 - 0.05/2, n1, n2)',
        'sigma_x/(F_table/2)**0.5',
        'uv(xbar,sigma_x,nx)',
        'uv(ybar,sigma_y,ny)',
        '((x.stdev**2 *(nx-1)+y.stdev**2 * (ny-1))/(nx+ny-2))**0.5'
    ]
    
    question_data = [
        'Given the following measurements calculate {spool_eqn_html}:<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny};s_pooled.answers(sf_tolerance=1)'
    ]
    
    html_vars=['spool_eqn_html']
    html_strings = [create_mattext_element("s_{pooled}")]

    print(f"generating {num_questions} questions for question bank {basename}")

    questions = []

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    for _ in range(num_questions):
        # Randomly select a question and its corresponding equation
        question_row = random.choice(question_data) if len(question_data) > 1 else question_data[0]
        question_text = question_row.split(';')[0]
        answer_equation = question_row.split(';')[1]

        # Generate random values for variables, prep namespace
        values={}
        current_globals = globals().copy()
        current_globals.pop("__builtins__", None)

        #generate nx, ny
        for var, var_rng in zip(int_vars.split(';'), int_var_ranges):
            values[var] = random.randint(var_rng[0],var_rng[1])

        #generate generate xbar, ybar
        for var, var_rng in zip(float_vars_logdist.split(';'), float_vars_logdist_ranges):
            values[var] = math.e**random.uniform(np.log(var_rng[0]),np.log(var_rng[1]))

        #get units
        for var in str_vars:
            values[var] = get_random_unit()
            
        # Generate values/objects that rely on values created above
        for var, eqn in zip(intermediate_calcs.split(';'), intermediate_equations):
            namespace = {**values}
            values[var] =  eval(eqn.format(**namespace), current_globals, namespace)

        # generate html vars
        for var, string in zip(html_vars,html_strings):
            namespace = {**values}
            values[var] =  string

        # Replace placeholders in the question with the generated values
        namespace = {**values}
        formatted_question = question_text.format(**values)
        
        # Calculate the answer using the provided equation
        answer = eval(answer_equation.format(**namespace), current_globals, namespace)

        questions.append({
            'question': formatted_question,
            'correct_answers': answer,
            'question_type': question_type
        })

    questions_df = pd.DataFrame(questions)
    return questions_df, basename,assessment_ident

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