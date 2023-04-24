import csv
import random
import re
import sys
import os
import numpy as np
import pandas as pd
from typing import List, Tuple

from makeqti import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sigfig import *

def generate_questions(question_template: str, relation: str, bounds: List[Tuple[int, int]], n_sig_figs: List[int], num_questions: int) -> List[Tuple[str, str]]:
    questions = []
    variables = re.findall(r'\{(\w+)\}', question_template)
    for _ in range(num_questions):
        var_values = {var: sigfig(sigfig(str(np.random.choice(np.logspace(np.log10(low), np.log10(high)))), sig_figs=np.random.randint(2, 4)).scientific_notation()) for var, (low, high), nsf in zip(variables, bounds, n_sig_figs)}
        question = question_template.format(**var_values)
        correct_answer_instance = eval(relation, {}, var_values)
        correct_answer = f"{correct_answer_instance};{correct_answer_instance.scientific_notation()}"
        numeric_value = correct_answer_instance.value
        questions.append((question, correct_answer, numeric_value))
    return questions

def main():
    question_template = "10^{x} = ?" #input("Enter the question template with placeholders in braces (e.g., What is {x} + {y}?): ")
    relation = "x.exponent(base=10)" # input("Enter the mathematical relationship between the variables (e.g., x+y): ")
    n_questions = 1000
    basename = "SigFigExponent" #str(input("base name of csv (omit .csv extension): "))


    bounds = []
    n_sig_figs =[]
    variables = re.findall(r'\{(\w+)\}', question_template)
    for variable in variables:
        #print(f"Enter the lower and upper bounds for {variable}:")
        lower = 1 #float(input("Lower bound: "))
        upper = 10 #float(input("Upper bound: "))
        bounds.append((lower, upper))
        nsf = 0# int(input("Number of significant figures: "))
        n_sig_figs.append(nsf)

    
    questions = generate_questions(question_template, relation, bounds, n_sig_figs, n_questions)

    
    output_csv = basename+".csv"

    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["question", "correct_answers", "floating_point_value"])
        for question, correct_answer, val in questions:
            writer.writerow([question, correct_answer, val])

    print("CSV file has been generated.")
    
    questions_df = pd.read_csv(output_csv)
    output_zip = basename+".zip" # Output ZIP file path
    qti_xml = create_qti_xml(questions_df, basename)
    save_to_zip(qti_xml, output_zip)

    print("zip file has been generated.")

if __name__ == "__main__":
    main()