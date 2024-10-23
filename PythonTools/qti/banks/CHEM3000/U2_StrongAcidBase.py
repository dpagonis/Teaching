import hashlib
import pandas as pd
import random
import os

from dp_qti.makeqti import *
from dp_chem import sf

strongacids = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/strongacids.csv')
strongbases = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/strongbases.csv')

def generate_question():
    question_type = 'short_answer'

    question_options = [
        'Calculate the pH of a {conc} M solution of {acid}.;pH_acid.answers(sf_tolerance=1)',
        'Calculate the pH of a {conc} M solution of {base}.;pH_base.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    
    conc = sf.random_value((1e-8,1e-4),(2,3),value_log=True)
    Kw = 1e-14
    strongacid = strongacids[strongacids['name'] != 'sulfuric acid'].sample(1)
    acid = strongacid['name'].values[0]
    c_H = quadratic_positiveroot(1,-1*conc,-Kw)
    pH_acid = -1*c_H.log()

    strongbase = strongbases.sample(1)
    base = strongbase['name'].values[0]
    n_OH = strongbase['n_OH'].values[0]
    c_H = quadratic_positiveroot(1,n_OH*conc,-Kw)
    pH_base = -1*c_H.log()
    

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

def yes_no(bool):
    if bool:
        return "Yes;yes;Y;y"
    else:
        return "No;no;N;n"
    
def quadratic_positiveroot(a,b,c):
    a = sf(str(a),sig_figs=99)
    c = sf(str(c),sig_figs=99)
    
    root1=(-1*b+(b**2-4*a*c)**0.5)/(2*a)
    root2=(-1*b-(b**2-4*a*c)**0.5)/(2*a)
    if root1.value > 0 and root2.value > 0:
        print(a,b,c)
        raise ValueError("both roots in quadratic_positiveroot() are positive")
    elif root1.value < 0 and root2.value < 0:
        raise ValueError("both roots in quadratic_positiveroot() are negative")
    
    pos_root = root1 if root1.value > 0 else root2
    
    if pos_root.sig_figs <= 0:
        pos_root.sig_figs = b.sig_figs

    return pos_root

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
