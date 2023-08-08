import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import uv

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
        'Given the following measurements calculate t:<br>{dbar_html} = {d.mean} {unit}<br>{sd_html} = {d.stdev} {unit}<br>n = {d.n}<br>Use 95% confidence level;t_calc.answers(sf_tolerance=1)',
        'Two techniques give the following data. Do the two techniques give significantly different results?<br>{dbar_html} = {d.mean} {unit}<br>{sd_html} = {d.stdev} {unit}<br>n = {d.n}<br>Use 95% confidence level;yes_no(not Ho)',
        'Two techniques give the following data. Do the two techniques agree within experimental error?<br>{dbar_html} = {d.mean} {unit}<br>{sd_html} = {d.stdev} {unit}<br>n = {d.n}<br>Use 95% confidence level;yes_no(Ho)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here

    unit = random.choice(['bar', 'mbar', 'atm', 'Pa', 'kPa', 'Torr', 'mmHg', 'kg', 'g', 'mol', 'A', 'mA', 'V', 'kV', 'm', 'km', 'nm', 's', 'ms', 'ns', 'yr', 'h', 'L', 'mL', 'M', 'mM', 'K', 'J', 'kJ', 'cal', 'kcal', 'N', 'W', 'Hz'])

    n = random.choice([3,4,5,6,7,8,9,10])

    d = uv.random_value((-10,10),(0.1,5),n_range=(n,n),no_hidden_digits=True)
    
    t_calc = abs(d.mean.value)*n**0.5/d.stdev
    t_table = sf(str(t.ppf(1 - 0.05/2, n-1)),last_decimal_place=-3)
    Ho = True if t_calc.value < t_table.value else False

    dbar_html = create_mattext_element('\overline{d}')
    sd_html = create_mattext_element('s_d')

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
