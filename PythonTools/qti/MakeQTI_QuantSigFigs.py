import random
import numpy as np
import csv
import sys
import pandas as pd
from typing import Tuple

from sigfig import sigfig
from makeqti import *
from uncertainvalue import uncertainvalue as uv

def generate_random_numbers() -> Tuple[float, float]:
    number1 = np.random.choice(np.logspace(np.log10(0.011), np.log10(1012))) 
    number2 = np.random.choice(np.logspace(np.log10(0.0001 * number1), np.log10(0.9 * number1))) 
    return number1, number2

def generate_question_and_answer() -> Tuple[str, str]:
    number1, number2 = generate_random_numbers()
    value = uv(number1,number2)
    question = f"Propagate error through the following calculation. Use the ± symbol: {format(number1, '.9f')} ± {format(number2, '.9f')}"
    answer = value.answers()
    return question, answer

def main():
    num_questions = 1000
    
    basename = 'QuantSigFigs'
    output_csv = basename+'.csv'
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['question', 'correct_answers'])

        for _ in range(num_questions):
            question, correct_answer = generate_question_and_answer()
            writer.writerow([question, correct_answer])
    
    questions_df = pd.read_csv(output_csv, encoding='utf-8')
    output_zip = basename+".zip" # Output ZIP file path
    qti_xml = create_qti_xml(questions_df, basename)
    save_to_zip(qti_xml, output_zip)

    print("zip file has been generated.")
if __name__ == "__main__":
    main()
