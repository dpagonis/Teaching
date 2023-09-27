import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the residence time (in s) for a lake whose volume is {V} {unit_vol} and whose input/output flow rate is {Q} {unit_vol}/s;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Calculate the first order rate constant for transport (in 1/s) for a lake whose volume is {V} {unit_vol} and whose input/output flow rate is {Q} {unit_vol}/s;k.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'If a lake has a flow rate of {Q} {unit_vol}/s and a volume of {V} {unit_vol}, calculate the residence time (in s).;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Find the residence time in seconds for a lake with a flow rate of {Q} {unit_vol}/s and a volume of {V} {unit_vol}.;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'What is the first order rate constant for transport (in 1/s) for a lake with a flow rate of {Q} {unit_vol}/s and a volume of {V} {unit_vol}?;k.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Calculate the first order rate constant for transport in 1/s for a lake with a flow rate of {Q} {unit_vol}/s and a volume of {V} {unit_vol}.;k.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Given a flow rate of {Q} {unit_vol}/s and a lake volume of {V} {unit_vol}, determine the first order rate constant for transport (in 1/s).;k.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'For a lake with a flow rate of {Q} {unit_vol}/s and a volume of {V} {unit_vol}, what is the residence time (in s)?;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'If the flow rate of a lake is {Q} {unit_vol}/s and the volume is {V} {unit_vol}, what is the residence time in seconds?;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'If the flow rate of a lake is {Q} {unit_vol}/s and the volume is {V} {unit_vol}, calculate the first order rate constant for transport in 1/s.;t_res.answers(roundoff_tolerance=True, sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    unit_vol = random.choice(['gal', 'm^3', 'L', 'ft^3', 'cubic cm'])

    Q = sf.random_value((1,1000),(2,4),value_log=True)
    V = sf.random_value((1e2,1e6),(2,4),value_log=True)

    k = Q / V
    t_res = V / Q

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

def get_term_list(coeff, rate_eqn_versions):
    """Return all possible terms based on coefficient and rate equation versions."""
    if coeff == 0:
        return []
    elif coeff == 1:
        return rate_eqn_versions
    elif coeff == -1:
        return [f"-{rate_eqn}" for rate_eqn in rate_eqn_versions]
    else:
        return [f"{coeff}{rate_eqn}" for rate_eqn in rate_eqn_versions]

def join_terms(terms):
    """Join terms ensuring subtraction is handled properly."""
    equation = ""
    for t in terms:
        term = t.strip()
        if not equation:  # if equation is still empty
            equation = term
        elif term.startswith('-'):
            term_nominus = term[1:]
            equation += f" - {term_nominus}"  # subtracting, so just add the term as it has '-'
        else:
            equation += f" + {term}"  # adding, so add with '+'
    return equation


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
