import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_qti import sf

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Compound X has a diffusion coefficient of {D_cm2s} {html_cm2s}. Calculate the mean displacement (in cm) of a molecule after {time_s} seconds.;x_from_tD.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Compound X has a diffusion coefficient of {D_cm2s} {html_cm2s}. How long (in seconds) will it take a molecule to acheive a displacement of {x_cm} cm?;t_from_xD.answers(roundoff_tolerance=True, sf_tolerance=1)',
        'Calculate the diffusion coefficient (in {html_cm2s}) for a molecule that is diplaced by {x_cm} cm after {time_s} seconds.;D_from_xt.answers(roundoff_tolerance=True,sf_tolerance=1)'
    ]

    html_cm2s = 'cm<sup>2</sup> s<sup>-1</sup>'

    # generating random values for variables, doing calculations, & prepping namespace here
    
    D_cm2s = sf.random_value((0.001,0.1),(2,3))
    time_s = sf.random_value()
    x_cm = sf.random_value((0.1,1000),(2,4),value_log=True)

    x_from_tD = (2 * time_s * D_cm2s)**0.5
    t_from_xD = x_cm **2 / (2* D_cm2s)
    D_from_xt = x_cm**2/(2 * time_s)

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
