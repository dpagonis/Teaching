import pandas as pd
import os
import msvcrt
import numpy as np

from .gets import *
from .process import *


def interact(quiz_id=None):  #quiz id optional
    
    quiz, report_df, submissions = download_report_submissions(quiz_id)
    qname = quiz['title']

    # Define a dictionary mapping menu items to their corresponding functions
    menu_options = [
        "Grade all submissions",
        "Outcomes by bank",
        "Stats",
        "Search for a different quiz",  
        "Exit"
    ]

    while True:
        print(f"-----{qname}-----\nMenu:")
        menu_dict={}
        for i, option in enumerate(menu_options, start=1):
            print(f"{i}. {option}")
            menu_dict[i]=option

        choice = int(input("Enter your choice: "))

        if menu_dict[choice] == 'Grade all submissions':
            grade_all_submissions(quiz,report_df)
            hold()
        elif menu_dict[choice] == 'Outcomes by bank':
            interact_outcomes_by_bank(quiz,submissions,report_df)
        elif menu_dict[choice] == 'Search for a different quiz':
            quiz, report_df, submissions = download_report_submissions()
            qname = quiz['title']
        elif menu_dict[choice]== 'Stats':
            report_stats(quiz, report_df, submissions)
        elif menu_dict[choice] == 'Exit':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    return 0

######################################################################################################
######################################################################################################

def interact_outcomes_by_bank(quiz,submissions,report_df):
    
    # Define a dictionary mapping menu items to their corresponding functions
    menu_options = [
        "All attempts",
        "First attempts",
        "Latest attempts",
        "Attempts that passed",
        "Attempts that did not pass",
        "Exit"
    ]

    print("\nMenu:")
    menu_dict={}
    for i, option in enumerate(menu_options, start=1):
        print(f"{i}. {option}")
        menu_dict[i]=option

    choice = int(input("Enter your choice: "))

    if menu_dict[choice] == "All attempts":
        outcomes_by_bank(quiz,submissions,report_df)
    
    elif menu_dict[choice] == "First attempts":
        first_attempt_submissions = []
        for s in submissions:
            if s['attempt']==1:
                first_attempt_submissions.append(s)
        outcomes_by_bank(quiz,first_attempt_submissions,report_df)
    
    elif menu_dict[choice] == "Latest attempts":
        latest_attempt_submissions=latest_attempts(report_df,submissions)
        outcomes_by_bank(quiz,latest_attempt_submissions,report_df)

    elif menu_dict[choice] == "Attempts that passed":
        passing = get_pass_threshold(quiz['title'])
        passing_subs = []
        for s in submissions:
            score = submission_score(s['user_id'],s['attempt'],report_df)
            if score>=quiz['points_possible']*passing:
                passing_subs.append(s)
        outcomes_by_bank(quiz,passing_subs,report_df)

    elif menu_dict[choice] == "Attempts that did not pass":
        passing = get_pass_threshold(quiz['title'])
        not_passing_subs = []
        for s in submissions:
            score = submission_score(s['user_id'],s['attempt'],report_df)
            if score<quiz['points_possible']*passing:
                not_passing_subs.append(s)
        outcomes_by_bank(quiz,not_passing_subs,report_df)
        
    elif menu_dict[choice] == 'Exit':
        print("Bye bye!")
    else:
        print("Invalid choice. Please try again.")
        interact_outcomes_by_bank(quiz,submissions,report_df) #recursive try again since we're not in a loop
    hold()
    return 0

#---------------------------------------------------------------------------------------------------------------------------

if os.name == 'nt':  # Windows
    import msvcrt
    def hold():
        print('Press any key to continue...')
        msvcrt.getch()
else:
    def hold():
        input('Press Enter to continue...')







def report_stats(quiz,report_df, submissions):
    print('\n',quiz['title'])
    students = set(report_df['id'])
    print(f'{len(students)} students')
    print(f'{len(submissions)} attempts')
    print(f"Range: {min(report_df['attempt'])}-{max(report_df['attempt'])} attempts")

    first = first_attempts(submissions)
    latest = latest_attempts(report_df,submissions)
    passing = get_pass_threshold(quiz['title'])
    N_pass = 0
    for s in latest:
        if s['score']>= passing*quiz['points_possible']:
            N_pass += 1
    print(f'{N_pass}/{len(students)} students passed the quiz ({round(100*N_pass/len(students))}%)')
    
    N_pass_1a = 0
    for s in first:
        if s['score']>= passing*quiz['points_possible']:
            N_pass_1a += 1
    print(f'{N_pass_1a}/{len(students)} students passed the quiz on the first attempt ({round(100*N_pass_1a/len(students))}%)')
    
    N_passing_att= 0
    for s in submissions:
        passed = (s['score'] >= passing*quiz['points_possible'])
        if passed:
            N_passing_att += 1
    print(f'{N_passing_att}/{len(submissions)} attempts were passing ({round(100*N_passing_att/len(submissions))}%)')
    hold()

def update_gradebook(student_id, quiz_title, outcome):
    filename = 'gradebook.csv'
    df = pd.read_csv(filename, index_col='id')

    if quiz_title in df.columns:
        df[quiz_title] = df[quiz_title].astype(str)

        # Update the outcome for the specified student_id
        if student_id in df.index:
            df.at[student_id, quiz_title] = str(outcome)
            df.to_csv(filename)
        else:
            print(f"Student ID {student_id} not found in the gradebook.")
    else:
        print(f"Column '{quiz_title}' not found in the gradebook.")
