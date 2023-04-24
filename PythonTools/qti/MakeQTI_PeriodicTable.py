import csv
import re
import pandas as pd
from makeqti import *

def generate_question_bank(question_template: str, answer_template: str, elements_df: pd.DataFrame) -> list:
    question_bank = []
    for index, row in elements_df.iterrows():
        try:
            question = question_template.format(**row)
            correct_answer = answer_template.format(**row)

            pattern = re.compile(r'[a-zA-Z]')
            if pattern.search(correct_answer):
                correct_answers = [correct_answer, correct_answer.lower()]
            else:
                correct_answers = correct_answer

            question_bank.append((question, correct_answers))
        except (ValueError, KeyError, TypeError):
            # Skip the current element if there's an error or the value is NaN
            pass

    return question_bank

def main():
    question_template = "What is the atomic mass of {symbol}?"
    answer_template = "{mass}"

    basename = "AtomicMassFromSymbol"
    
    #---------------end inputs--------------------------

    elements_df = pd.read_csv("tables/elements.csv")
    question_bank = generate_question_bank(question_template, answer_template, elements_df)

    output_csv = basename+".csv"
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["question", "correct_answers"])
        for question, correct_answer in question_bank:
            writer.writerow([question, correct_answer])
    
    questions_df = pd.read_csv(output_csv)
    output_zip = basename+".zip" # Output ZIP file path
    qti_xml = create_qti_xml(questions_df, basename)
    save_to_zip(qti_xml, output_zip)

    print("zip file has been generated.")
if __name__ == "__main__":
    main()
