import pandas as pd
import os
import dp_canvas.gets as gets
from .gets import *

def download_report_submissions(quiz_id=None,skip_download=False,quiet=False):
    if quiz_id is None:
        quiz_id = search_for_quiz()
    
    #get quiz meta json
    quiz = get_quiz(quiz_id)

    #get report and submissions
    if not quiet:
        print('Getting submissions...')
    submissions = get_all_submissions(quiz_id,skip_download=skip_download)
    if not quiet:
        print('Getting student report...')
    report_df = pd.read_csv(get_student_report(quiz_id, quiet=quiet, skip_download=skip_download),low_memory=False)
    if not quiet:
        print("Submissions and student report successfully retreived")
    
    students = set(report_df['id'])
    student_submissions = []
    for sub in submissions:
        if sub['user_id'] in students:
            sub['score'] = submission_score(sub['user_id'],sub['attempt'],report_df)
            student_submissions.append(sub)
    
    return quiz, report_df, student_submissions

def grade_all_submissions(quiz,df):
    
    passing = get_pass_threshold(quiz['title'])
    if passing < 1:
        passing *= 100
    
    students = set(df['id'].values)
    N_passed = 0
    N_attempted = len(students)

    for id in students:
        dff_graded = df[df['id']==id]
        scores = dff_graded['score'].values
        score = 100*max(scores)/quiz['points_possible'] if len(scores) > 0 else 0
        if score >= passing:
            N_passed += 1
            outcome = 'Pass'
        else:
            outcome = 'Needs Revision'
        update_gradebook(id,quiz['title'],outcome)

    print(f'\n{len(students)} took the quiz. \n{N_passed} passed the quiz')
    return 0

def submission_outcome_1200(quiz,score):
    passing = get_pass_threshold(quiz['title'])
    if passing < 1:
        passing *= 100
    if score >= passing:
        outcome = 'Pass'
    else:
        outcome = 'Needs Revision'
    return outcome

def submission_outcome_3000(name,score):
    passing = get_pass_threshold(name)
    if passing < 1:
        passing *= 100
    if score == 100 and 'problem set' not in name.lower():
        outcome = 'A'
    elif score >= passing:
        outcome = 'Pass'
    else:
        outcome = 'Needs Revision'
    return outcome

def get_pass_threshold(assignment_name):
    file_path = 'pass_threshold.csv'

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, index_col='name')
            if assignment_name in df.index:
                return float(df.loc[assignment_name].iloc[0])
            elif 'default' in df.index:
                return float(df.loc['default'].iloc[0])
            else:
                print("Default threshold not set in the file. Using 0.75.")
                return 0.75
        except (ValueError, IOError):
            print(f"Error reading from {file_path}. Using default value of 0.75.")
            return 0.75
    else:
        return 0.75



def update_gradebook(student_id, quiz_title, outcome):
    filename = 'gradebook.csv'

    if not os.path.exists(filename):
        gets.create_gradebook()

    df = pd.read_csv(filename, index_col='id')

    if quiz_title in df.columns:
        df[quiz_title] = df[quiz_title].fillna('').astype(str)

        # Update the outcome for the specified student_id
        if student_id in df.index:
            outcomestr = str(outcome)
            df.at[student_id, quiz_title] = outcomestr
            df.to_csv(filename)
        else:
            print(f"Student ID {student_id} not found in the gradebook.")
    else:
        print(f"Column '{quiz_title}' not found in the gradebook.")

def submission_score(user_id,attempt,report_df):
    filtered_df = report_df[(report_df['id'] == user_id) & (report_df['attempt'] == attempt)]
    if not filtered_df.empty:
        return filtered_df.iloc[0]['score']
    else:
        raise ValueError(f'failed to find submission in student report: student id {user_id}, attempt {attempt}')  
    

def grade_all_assignments_1200(course_id=course_id):
    assignments = get_assignments(course_id=course_id)
    for a in assignments:
        if a['workflow_state']=='published':
            quiz = gets.get_quiz(a['quiz_id'])
            points_possible = quiz['points_possible']
            print(a['name'])
            submissions = get_assignment_submissions(a['id'],course_id=course_id)
            for s in submissions:
                points = s['score']
                if points is not None:
                    score = 100*points/points_possible
                    outcome = submission_outcome_1200(quiz,score)
                    update_gradebook(s['user_id'],quiz['title'],outcome)

def grade_all_assignments_3000(course_id=course_id,force_download=False):
    assignments = get_assignments(course_id=course_id)
    for a in assignments:
        if a['workflow_state']=='published':
            name = a['name']
            print(name)
            submissions = get_assignment_submissions(a['id'],course_id=course_id, force_download=force_download)
            for s in submissions:
                points = s['score']
                if points is not None:
                    if 'problem' in name.lower():
                        name_for_outcome = 'problem set'
                        points_possible = 6
                    else:
                        name_for_outcome = 'default'
                        points_possible = 4
                    score = 100*points/points_possible
                    outcome = submission_outcome_3000(name_for_outcome,score)
                    if 'problem' in name.lower() and 'revision' in outcome.lower():
                        outcome = "Not Passed"
                    update_gradebook(s['user_id'],name,outcome)

def grade_all_assignments(course_id=course_id,force_download=False):
    assignments = get_assignments(course_id=course_id)
    for a in assignments:
        if a['workflow_state']=='published':
            name = a['name']
            print(name)
            submissions = get_assignment_submissions(a['id'],course_id=course_id, force_download=force_download)
            for s in submissions:
                points = s['score']
                update_gradebook(s['user_id'],name,points)

def first_attempts(submissions):
    fs = []
    for s in submissions:
        if s['attempt'] == 1:
            fs.append(s)
    return fs 

def latest_attempts(report_df, submissions):
    la=[]
    students = set(report_df['id'].values)
    student_attempt_dict={}
    for stu in students:
        dff=report_df[report_df['id']==stu]
        student_attempt_dict[stu]=max(dff['attempt'])
    
    for sub in submissions:
        stu = sub['user_id']
        att = sub['attempt']
        if student_attempt_dict[stu]==att:
            la.append(sub)
    return la

def outcomes_by_bank(quiz, submissions,report_df):
    df_resultsbybank = pd.DataFrame(columns=['number_attempted', 'number_correct'])

    for sub in submissions:
        
        student_id = sub['user_id']
        if student_id not in report_df['id'].values:
            continue   #e.g. test student appears in submissions but not student report
        attempt = sub['attempt']
        # finished = sub['finished_at']
        # finished_mt = pd.to_datetime(finished).tz_convert('America/Denver')
        Qlist = sub['quiz_submission_questions'] #get_submission_questions(sub_id, quiz['id'])
        
        for Q in Qlist:
            question_id = Q['id']
            group_id = Q['quiz_group_id']
            Q_correct, Q_answered = was_Q_answered(student_id, attempt, question_id, report_df)
            if Q_answered:   # only include questions that were answered in the results tracking
                if group_id not in df_resultsbybank.index:
                    # Add a new row for this quiz group
                    df_resultsbybank.loc[group_id] = [0, 0]  # Initialize with zeros
                df_resultsbybank.at[group_id, 'number_attempted'] += 1
                if Q_correct:
                    df_resultsbybank.at[group_id, 'number_correct'] += 1
    
    banknamedf = pd.read_csv('banks.csv', index_col='bank_id')
    bank_dict = banknamedf.iloc[:, 0].to_dict()
    group_dict = {}
    for group_id in df_resultsbybank.index:
        groupinfo=get_question_group_info(quiz['id'],group_id)
        group_dict[group_id]=bank_dict[groupinfo['assessment_question_bank_id']]

    df_resultsbybank['bank_name'] = df_resultsbybank.index.map(group_dict)
    for index,row in df_resultsbybank.iterrows():
        if row['number_attempted'] == 0:
            df_resultsbybank.at[index, 'percentage'] = 0
        else:
            percentage = 100 * row['number_correct'] / row['number_attempted']
            df_resultsbybank.at[index, 'percentage'] = round(percentage)
    print(df_resultsbybank)
    return df_resultsbybank



def was_Q_answered(student_id, attempt, question_id, df):
    # Filter the DataFrame for the specific student and attempt
    filtered_df = df[(df['id'] == student_id) & (df['attempt'] == attempt)]
    Q_correct = False 
    # Check if the filtered DataFrame is not empty
    if not filtered_df.empty:
        # Iterate through columns to find the one that starts with question_id
        for col in filtered_df.columns:
            if str(col).startswith(str(question_id)):
                # This is the answer column, The next column contains the score
                answer_col = filtered_df.columns[filtered_df.columns.get_loc(col)]
                score_col = filtered_df.columns[filtered_df.columns.get_loc(col)+1]
                # Check if the answer cell is empty or not
                answer = filtered_df.iloc[0][answer_col]
                score = filtered_df.iloc[0][score_col]
                Q_answered = not pd.isna(answer)
                if Q_answered:
                    Q_correct = True if float(score)>0 else False

                return Q_correct, Q_answered

    else:
        raise ValueError(f'failed to find submission in student report: student id {student_id}, attempt {attempt}')  
    
