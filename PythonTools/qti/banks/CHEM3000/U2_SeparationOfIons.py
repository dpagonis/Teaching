import hashlib
import pandas as pd
import random
import os
from math import gcd

from dp_qti.makeqti import *
from dp_qti import sf
from dp_qti import molecule

reactions = pd.read_csv('C:/Users/demetriospagonis/Box/github/Teaching/PythonTools/tables/ksp.csv')


def generate_question():
    question_type = 'short_answer'

    question_options = [
        'A solution contains {conc0} M {cation0_html} and {conc1} M {cation1_html}. Which ion will precipitate first when {anion_html} is added to the solution?<br>{pKsp0_html}<br>{pKsp1_html};first_ion_out',
        'A solution contains {conc0} M {cation0_html} and {conc1} M {cation1_html}. What fraction of {first_ion_out} will remain in solution when these ions are separated by adding {anion_html} to the solution?<br>{pKsp0_html}<br>{pKsp1_html};resid_frac.answers(sf_tolerance=1)'
    ]

    # generating random values for variables, doing calculations, & prepping namespace here
    # Group the dataframe by 'anion'
    conc0 = sf.random_value((0.01,0.1),(2,3))
    conc1 = sf.random_value((0.01,0.1),(2,3))
    
    grouped = reactions.groupby('anion')

    # Select a group randomly, but only consider groups with at least two members
    valid_groups = [name for name, group in grouped if len(group) >= 2]
    random_group_name = random.choice(valid_groups)

    # Get two random samples from the chosen group
    rows = grouped.get_group(random_group_name).sample(2)

    
    cation0, cation1 = [molecule(cation) for cation in rows['cation'].values]
    anion0, anion1 = [molecule(anion) for anion in rows['anion'].values]
    salt0, salt1 = [molecule(salt) for salt in rows['formula'].values]
    pKsp0, pKsp1 = [sf(str(pKsp)) for pKsp in rows['pKsp'].values]

    Ksp0 = (-1*pKsp0).exponent(10)
    Ksp1 = (-1*pKsp1).exponent(10)


    #calculate critical anion concentrations
    gcd_value0 = gcd(abs(cation0.charge), abs(anion0.charge))
    n_cat0 = abs(anion0.charge) // gcd_value0
    n_an0 = abs(cation0.charge) // gcd_value0
    
    conc_crit0 = (Ksp0/(conc0**n_cat0))**(1/n_an0)

    gcd_value1 = gcd(abs(cation1.charge), abs(anion1.charge))
    n_cat1 = abs(anion1.charge) // gcd_value1
    n_an1 = abs(cation1.charge) // gcd_value1
    
    conc_crit1 = (Ksp1/(conc1**n_cat1))**(1/n_an1)

    first_ion_out = cation0 if conc_crit0.value < conc_crit1.value else cation1
    ci_firstion = conc0 if conc_crit0.value < conc_crit1.value else conc1
    Ksp_firstion = Ksp0 if conc_crit0.value < conc_crit1.value else Ksp1
    n_an_firstion = n_an0 if conc_crit0.value < conc_crit1.value else n_an1
    n_cat_firstion = n_cat0 if conc_crit0.value < conc_crit1.value else n_cat1
    conc_crit = max(conc_crit0.value,conc_crit1.value)
    
    conc_firstion_atcrit = (Ksp_firstion/(conc_crit**n_an_firstion))**(1/n_cat_firstion)

    resid_frac = conc_firstion_atcrit / ci_firstion

    cation0_html = create_mattext_element(cation0.tex)
    cation1_html = create_mattext_element(cation1.tex)
    anion_html = create_mattext_element(anion0.tex)
    pKsp0_html = create_mattext_element(f'pK_{{sp,{salt0.formula}}}={pKsp0}')
    pKsp1_html = create_mattext_element(f'pK_{{sp,{salt1.formula}}}={pKsp1}')
    

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
