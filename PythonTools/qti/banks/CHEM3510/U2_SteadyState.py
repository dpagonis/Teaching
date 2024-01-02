import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Compound X is being emitted into a lake at a rate of {E_X} g/hr. Calculate the steady-state concentration of compound X (units: g/L) given that the lake volume is {V} L and its residence time is {tau} h.;c_ss.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Compound X is being emitted into a lake at a rate of {E_X} kg/day. Calculate the steady-state concentration of compound X (units: kg/m3) given that the lake\'s residence time is {tau} days and its volume is {V} cubic meters.;c_ss.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'A lake has a residence time of {tau} h and a volume of {V} L. Compound X is emitted into the lake at a rate of {E_X} g/hr. Calculate the steady-state concentration of X.;c_ss.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'A lake has a volume of {V} L and a residence time of {tau} h. Compound X is emitted into the lake at a rate of {E_X} g/hr. Calculate the steady-state concentration of X.;c_ss.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'A {V} L lake has {E_X} g/hr of pollutant Z being emitted into it from a nearby factory. Calculate the steady-state concentration of Z in the lake (units: g/L) given that its residence time is {tau} hr.;c_ss.answers(roundoff_tolerance=True, sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    
    V = sf.random_value((1e4,1e6),(1,3),value_log=True)
    tau = sf.random_value((100,1000), (2,3))
    E_X = sf.random_value((1,1e3),(1,3),value_log=True)


    c_ss = tau * E_X / V

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
