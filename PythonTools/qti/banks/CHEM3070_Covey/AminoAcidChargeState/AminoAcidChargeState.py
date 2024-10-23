import hashlib
import pandas as pd
import random
import os
import re
import numpy as np
import csv

from dp_qti.makeqti import *
from dp_chem import sf
from dp_chem import weakacid

acids = pd.read_csv('aminoacids.csv')
acids['pKa'] = acids['pKa'].apply(lambda x: [float(i) for i in x.split(';')])

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
    question_type = 'multiple_choice'

    question_options = [
        'What is the charge of this amino acid at pH = {pH}?<br>{all_pKa_html}<br>{img_html}'
    ]

    row = acids[acids['pKa'].apply(len)>1].sample(1)
    acid = weakacid(row['formula_neutral'].values[0],row['pKa'].values[0],n_H_neutral=row['N_acidic_proton_neutral'].values[0])


    pKa_types = row['pKa_type'].values[0].split(';')
    pKa_eqn_strings = [f'p_{{Ka,{pKa_type}}}={pKa_value}' for pKa_type, pKa_value in zip(pKa_types,acid.pKa)]
    pKa_html = [create_mattext_element(s) for s in pKa_eqn_strings]
    all_pKa_html = '<br>'.join(pKa_html)

    png_name = row['Abbreviation'].values[0]+'.png'
    img_html = create_img_mattext(png_name)

    while True:
        pH = sf.random_value((0,14),(2,3))
        if np.all(np.abs(np.array(acid.pKa) - pH.value) > 1):
            break

    acid.pH = pH

    # Find the index of the largest alpha value
    largest_alpha_index = np.argmax(acid.alpha)

    # Find the corresponding charge from acid.forms
    answer = str(acid.forms[largest_alpha_index].charge)

    # Find the incorrect charges
    incorrect_charges = [m.charge for i, m in enumerate(acid.forms) if i != largest_alpha_index]

    # Convert the list of incorrect charges to a semi-colon separated string
    incorrect_answers = ";".join(map(str, incorrect_charges))




    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    question_text = question_row.split(';')[0]
    

   # Get a dictionary of all local variables
    namespace = locals()

    # Replace placeholders in the question with the generated values
    formatted_question = question_text.format(**namespace)


    if len(question_row.split(';')) > 1:
        answer_equation = question_row.split(';')[1]
        # Calculate the answer using the provided equation
        answer = eval(answer_equation, globals(), namespace)

    # Check if the image tag exists in the formatted question
    image_tag_search = re.search(r'<img src="\$IMS-CC-FILEBASE\$/Uploaded%20Media/(.*?)"', formatted_question)
    image_file = image_tag_search.group(1) if image_tag_search else None

    return {
        'question': formatted_question,
        'correct_answers': answer,
        'incorrect_answers': incorrect_answers,
        'question_type': question_type,
        'image_file': image_file
    }

def main():
    questions_df, basename, assessment_ident = generate_questions()
    output_zip = f'{basename}.zip'

    # Generate a list of unique image filenames from the DataFrame
    image_files = questions_df['image_file'].dropna().unique().tolist()

    qti_xml = create_qti_xml(questions_df, basename, assessment_ident)
    manifest_xml = create_manifest_xml(assessment_ident, basename, image_files)
    save_xml_to_zip(qti_xml, assessment_ident, manifest_xml, output_zip, image_files)
    output_csv = f'{basename}.csv'
    questions_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    main()
