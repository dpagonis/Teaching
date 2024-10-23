
import hashlib
import pandas as pd
import random
from scipy.stats import t
import os

from dp_qti.makeqti import *
from dp_chem import sigfig as sf
from dp_chem.units import units


def generate_question(i, np, nn, ne, synonyms_dict):
    question_type = 'multi_select'
    

    # Calculate indices
    index_np = i % len(np)
    index_nn = (i // len(np)) % len(nn)
    index_ne = i // (len(np) * len(nn))

    # Retrieve items
    item_np = np[index_np]
    item_nn = nn[index_nn]
    item_ne = ne[index_ne]

    np_answers = [i for i in np if (len(i)>0 and i != item_np)]
    nn_answers = [i for i in nn if (len(i)>0 and i != item_nn)]
    ne_answers = [i for i in nn if (len(i)>0 and i != item_ne)]

    item_list = [i for i in [item_np,item_nn,item_ne] if len(i) > 0]
    random.shuffle(item_list)
    param_str = '<br>'.join(item_list)

    question_options = [
        'You know the following information about an atom. Which of the following properties of the atom can you determine? Select all that are correct.<br>{param_str};answers;distractors',
    ]

    correct_answer_list = []
    incorrect_answer_list = []

    for i in item_list:
        correct_answer_list.extend(synonyms_dict[i])

    if len(item_np) > 0:
        correct_answer_list.extend([i for i in np_answers if i not in correct_answer_list])
    else: 
        incorrect_answer_list.extend(np_answers)

    if len(item_np) > 0 and len(item_nn) > 0: #if there's enough info to know the isotope
        correct_answer_list.extend([i for i in nn_answers if i not in correct_answer_list])
    else:
        incorrect_answer_list.extend([i for i in nn_answers if i not in correct_answer_list])

    if len(item_np) > 0 and len(item_ne) > 0: #if there's enough info to know the charge
        correct_answer_list.extend([i for i in ne_answers if i not in correct_answer_list])
    else:
        incorrect_answer_list.extend([i for i in ne_answers if i not in correct_answer_list])

    


    answers = ';'.join(correct_answer_list)
    distractors = ';'.join(incorrect_answer_list)

    #####------------------Shouldn't need to edit anything from here down--------------------------#####
    # Randomly select a question and its answer(s)
    question_row = random.choice(question_options) if len(question_options) > 1 else question_options[0]
    question_text = question_row.split(';')[0]
    answer_equation = question_row.split(';')[1]
    incorrect_answer_equation = question_row.split(';')[2]

   # Get a dictionary of all local variables
    namespace = locals()

    # Replace placeholders in the question with the generated values
    formatted_question = question_text.format(**namespace)

    # Calculate the answer using the provided equation
    answers = eval(answer_equation, globals(), namespace)
    incorrect_answers = eval(incorrect_answer_equation, globals(), namespace)

    return {
        'question': formatted_question,
        'correct_answers': answers,
        'incorrect_answers':incorrect_answers,
        'question_type': question_type
    }

def generate_questions():
    
    np = [
        'Number of protons',
        'Atomic number',
        'Element name',
        'Element symbol',
        ''
    ]

    nn = [
        'Number of neutrons',
        'Mass number',
        'Mass of the nucleus',
        ''
    ]
    
    ne = [
        'Number of electrons',
        'Atomic charge',
        'Net charge of the atom',
        ''
    ]

    synonyms_dict = {
        'Number of protons': {'Atomic number', 'Element name', 'Element symbol'},
        'Atomic number': {'Number of protons','Element name', 'Element symbol'},
        'Element name': {'Element symbol','Number of protons','Atomic number'},
        'Element symbol': {'Element name','Number of protons','Atomic number'},
        'Number of neutrons': {},
        'Mass number': {'Mass of the nucleus'},
        'Mass of the nucleus': {'Mass number'},
        'Number of electrons': {},
        'Atomic charge': {'Net charge of the atom'},
        'Net charge of the atom': {'Atomic charge'}
    }

    
    
    num_questions = len(np)*len(nn)*len(ne)

    basename = os.path.basename(__file__).removesuffix('.py')
    print(f"generating {num_questions} questions for question bank {basename}")
    questions = []

    for i in range(num_questions):
        question = generate_question(i,np,nn,ne, synonyms_dict)
        questions.append(question)

    questions_df = pd.DataFrame(questions)

    # Generate unique assessment ident based on the basename
    assessment_ident = hashlib.md5(basename.encode('utf-8')).hexdigest()

    return questions_df, basename, assessment_ident

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
