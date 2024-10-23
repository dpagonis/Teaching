#sigmas need to be 1 or 2 sig-fig values when passed to uv

from scipy.stats import f
import hashlib
import pandas as pd
import random
import math
import numpy as np

from dp_qti.makeqti import *
from dp_chem import  uncertainvalue as uv
from dp_chem import sf

def generate_questions():
    basename = 'U1_F_test' #this string is used to name the bank and the hash ID
    
    num_questions = 1000    #recommend 1000

    question_type = 'short_answer'
    
    float_vars = 'sigma_x;sigma_y'
    ranges = '0.1,0.7; 0.1,0.99'
    float_vars_ranges = [(float(rng.split(',')[0]), float(rng.split(',')[1])) for rng in ranges.split(';')]
    
    float_vars_logdist = 'xbar;ybar'
    ranges = '1,100; 0.11,100'
    float_vars_logdist_ranges = [(float(rng.split(',')[0]), float(rng.split(',')[1])) for rng in ranges.split(';')]

    int_vars = 'nx;ny'
    ranges = '3,20; 3,20'
    int_var_ranges = [(int(rng.split(',')[0]), int(rng.split(',')[1])) for rng in ranges.split(';')]
    
    str_vars = ['unit']

    intermediate_calcs = 'x;y;Fcalc;n1;n2;Ftable;Ho'
    intermediate_equations = [
        'uv(xbar,sigma_x,nx)',
        'uv(ybar,sigma_y,ny)',
        'sf(str((max(x.stdev.value,y.stdev.value)/min(x.stdev.value,y.stdev.value))**2), sig_figs=2)',
        'nx if x.stdev.value > y.stdev.value else ny',
        'ny if x.stdev.value > y.stdev.value else nx',
        'sf(str(f.ppf(1 - 0.05/2, n1, n2)),last_decimal_place=-2)',
        'True if Fcalc.value<float(Ftable.scientific_notation()) else False'
    ]
    
    question_data = [
        'Given the following measurements calculate F:<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny};Fcalc.answers(sf_tolerance=1)',
        'Calculate the F statistic for the following measurements:<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny};Fcalc.answers(sf_tolerance=1)',
        'Give the tabulated F value (F_table) for the following measurements:<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny};Ftable.answers()',
        'Are the following standard deviations significantly different?<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny}; yes_no(not Ho)',
        'Do the standard deviations of these measurements agree within experimental error?<br>{x} {unit}, n={nx}<br>{y} {unit}, n={ny}; yes_no(Ho)'
    ]

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

        #generate sigma_x, sigma_y
        for var, var_rng, in zip(float_vars.split(';'), float_vars_ranges):
            values[var] = float(uv(0,random.uniform(var_rng[0],var_rng[1])).stdev.scientific_notation())

        #get units
        for var in str_vars:
            values[var] = get_random_unit()
            
        # Generate values/objects that rely on values created above
        for var, eqn in zip(intermediate_calcs.split(';'), intermediate_equations):
            namespace = {**values}
            values[var] =  eval(eqn.format(**namespace), current_globals, namespace)

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