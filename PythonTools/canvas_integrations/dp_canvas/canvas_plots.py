import matplotlib
matplotlib.use('Agg')  # Use the non-GUI Agg backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import os
import numpy as np
import datetime

import dp_canvas.gets as gets
import dp_canvas.process as dp_process

def makeplots(search_str):
    practice_id = gets.search_for_quiz(search_str+" — Practice")
    graded_id = gets.search_for_quiz(search_str)

    practice_quiz, practice_report_df, practice_submissions = dp_process.download_report_submissions(practice_id)
    graded_quiz, graded_report_df, graded_submissions = dp_process.download_report_submissions(graded_id)
        

    

    #scores by bank across initial practice, final practice, and final graded attempt
    topic_trends(practice_quiz, practice_report_df, practice_submissions, graded_quiz, graded_report_df, graded_submissions)

    #number of attempts until students passed practice and graded quizzes
    plot_attempts_histogram(practice_quiz,practice_report_df)
    plot_unique_submission_days_histogram(practice_quiz,practice_report_df)
    attempts_until_passing(practice_quiz, practice_submissions)
    attempts_until_passing(graded_quiz, graded_submissions)
    n_passing_students_by_date(graded_quiz,graded_report_df)
    plot_student_attempts(graded_quiz, practice_report_df, graded_report_df)



def topic_trends(practice_quiz, practice_report_df, practice_submissions, graded_quiz, graded_report_df, graded_submissions):
    first_practice_subs = dp_process.first_attempts(practice_submissions)
    latest_practice_subs = dp_process.latest_attempts(practice_report_df,practice_submissions)
    latest_graded_subs = dp_process.latest_attempts(graded_report_df,graded_submissions)

    outcomes_first_practice = dp_process.outcomes_by_bank(practice_quiz, first_practice_subs,practice_report_df)
    outcomes_latest_practice = dp_process.outcomes_by_bank(practice_quiz, latest_practice_subs,practice_report_df)
    outcomes_graded = dp_process.outcomes_by_bank(graded_quiz, latest_graded_subs,graded_report_df)

    # Add a column to each dataframe to identify the type
    outcomes_first_practice['Type'] = 'First Practice'
    outcomes_latest_practice['Type'] = 'Latest Practice'
    outcomes_graded['Type'] = 'Graded'

    # Combine the dataframes
    combined_df = pd.concat([outcomes_first_practice, outcomes_latest_practice, outcomes_graded])

    # Pivot the dataframe for plotting
    agg_df = combined_df.groupby(['bank_name', 'Type']).agg(
        total_attempted=pd.NamedAgg(column='number_attempted', aggfunc='sum'),
        total_correct=pd.NamedAgg(column='number_correct', aggfunc='sum')
    ).reset_index()

    agg_df['percentage'] = (agg_df['total_correct'] / agg_df['total_attempted']) * 100

    pivot_df = agg_df.pivot(index='bank_name', columns='Type', values='percentage')
    
    # Force the column order for plotting
    pivot_df = pivot_df[['First Practice', 'Latest Practice', 'Graded']]


    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_df.plot(kind='bar', ax=ax)

    ax.set_title(f'Performance by Bank — {graded_quiz["title"]}')
    ax.set_ylabel('Percentage')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Attempt Type', loc='lower right', borderaxespad=1)
    ax.axhline(y=80, color='black', linestyle='--')
    ax.set_ylim(0, 100)
    
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{graded_quiz["title"]}_TopicTrends.png')
    plt.close(fig)

def attempts_until_passing(quiz, submissions):
    passing = dp_process.get_pass_threshold(quiz['title']) * quiz['points_possible']

    student_set = set()
    for s in submissions:
        student_set.add(s['user_id'])
    
    first_passing_attempt=[]

    for s_id in student_set:
        s_score_dict = {}
        for sub in submissions:
            if sub['user_id'] == s_id:
                s_score_dict[sub['attempt']] = sub['score']
        passing_attempt_numbers=[]
        for k in s_score_dict.keys():
            if s_score_dict[k] >= passing:
                passing_attempt_numbers.append(k)
        if len(passing_attempt_numbers)>0:
            first_passing_attempt.append(min(passing_attempt_numbers))

    min_value = int(np.floor(min(first_passing_attempt)))
    max_value = int(np.ceil(max(first_passing_attempt)))
    bins = np.arange(min_value - 0.5, max_value + 1.5, 1)

    fig, ax = plt.subplots()
    ax.hist(first_passing_attempt, bins=bins, edgecolor='black', align='mid')
    ax.set_ylabel('Number of Students')
    ax.set_xlabel('Number of Attempts Until Passing')
    ax.set_title(f'Attempts Until Passing — {quiz["title"]}')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{quiz["title"]}_AttemptsUntilPassing.png')
    plt.close(fig)

def n_passing_students_by_date(quiz,report_df):
    passing = dp_process.get_pass_threshold(quiz['title']) * quiz['points_possible']
    report_df['submitted'] = pd.to_datetime(report_df['submitted'])
    
    # Filter for passing attempts
    passing_attempts = report_df[report_df['score'] >= passing]
    first_passing_attempts = passing_attempts.sort_values(by='submitted').drop_duplicates(subset='id', keep='first')    
    passing_counts_by_date = first_passing_attempts.resample('D', on='submitted').count()['id']
    cumulative_passing_counts = passing_counts_by_date.cumsum()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    cumulative_passing_counts.plot(ax=ax, kind='line', marker='o', linestyle='-', color='black', label='Passing Students')

    deadline = pd.to_datetime(quiz['due_at'])
    ax.axvline(x=deadline, color='red', linestyle='--', label='Deadline')
    ax.axhline(y=47, color='black', label='Enrollment')

    ax.set_title(f'Number of Students Passing Over Time: {quiz["title"]}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Students')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{quiz["title"]}_NPassingOverTime.png')
    plt.close(fig)

def plot_student_attempts(quiz, practice_df, graded_df):
    # Calculate the passing score
    passing = dp_process.get_pass_threshold(quiz['title']) * quiz['points_possible']
    
    # Add a column to each DataFrame to distinguish between practice and graded attempts
    practice_df['Type'] = 'Practice'
    graded_df['Type'] = 'Graded'
    
    # Combine the DataFrames and sort by submission time
    combined_df = pd.concat([practice_df, graded_df])
    combined_df['submitted'] = pd.to_datetime(combined_df['submitted'], utc=True)  # Ensure datetime is timezone-aware
    combined_df['submitted'] = combined_df['submitted'].dt.tz_convert('America/Denver')
    combined_df = combined_df.dropna(subset=['submitted'])

    combined_df.sort_values(by='submitted', inplace=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))

    # Generate a unique color for each student
    unique_students = combined_df['id'].nunique()
    color_map = plt.cm.get_cmap('rainbow', unique_students)

    # Dictionary to hold student_id to color mapping
    student_color_mapping = {student_id: color_map(i) for i, student_id in enumerate(combined_df['id'].unique())}

    # Plot attempts
    for student_id, group_df in combined_df.groupby('id'):
        color = student_color_mapping[student_id]
        # Extract practice and graded attempts
        practice_attempts = group_df[group_df['Type'] == 'Practice']
        graded_attempts = group_df[group_df['Type'] == 'Graded']
        
        ax.plot(group_df['submitted'], group_df['score'], 'o-', mfc='none', mec=color, alpha=0.5)
        ax.plot(graded_attempts['submitted'], graded_attempts['score'], 'o', color=color, mfc=color, alpha=0.5)

    # Add passing score line
    ax.axhline(y=passing, color='green', linestyle='--', label='Passing Score')

    # Add deadline vertical line
    deadline = pd.to_datetime(quiz['due_at'])
    ax.axvline(x=deadline, color='red', linestyle='--', label='Deadline')

    # Enhance plot
    ax.set_title(f'Student Attempts Over Time:\n{quiz["title"]}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Score')

    # Custom legend handling to avoid duplicate entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Removes duplicates
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left')

    ax.grid(True)
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{quiz["title"]}_StudentAttemptsOverTime.png')
    plt.close(fig)

def plot_attempts_histogram(quiz,report_df):
    # Count the number of attempts by each student
    attempts_per_student = report_df.groupby('id').size()
    
    fig, ax = plt.subplots()
    ax.hist(attempts_per_student, bins=range(1, attempts_per_student.max() + 2), align='left', color='skyblue', edgecolor='black')
    ax.set_title(f'Attempts per Student:\n{quiz["title"]}')
    ax.set_xlabel('Number of Attempts')
    ax.set_ylabel('Number of Students')
    ax.set_xticks(np.arange(1, attempts_per_student.max() + 1))
    ax.grid(axis='y', alpha=0.75)
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{quiz["title"]}_NAttemptsEachStudent.png')
    plt.close(fig)

def plot_unique_submission_days_histogram(quiz,report_df):
    report_df['submitted'] = pd.to_datetime(report_df['submitted']).dt.date
    
    unique_days_per_student = report_df.groupby('id')['submitted'].nunique()
    fig, ax = plt.subplots()

    n, bins, patches = ax.hist(unique_days_per_student, bins=range(1, unique_days_per_student.max() + 2), align='left', color='lightgreen', edgecolor='black')
    ax.set_title(f'Unique Submission Days per Student:\n{quiz["title"]}')
    ax.set_xlabel('Number of Unique Submission Days')
    ax.set_ylabel('Number of Students')
    ax.set_xticks(np.arange(1, unique_days_per_student.max() + 1))
    ax.grid(axis='y', alpha=0.75)
    fig.tight_layout()
    if os.path.isdir('figs'):
        fig.savefig(f'figs/{quiz["title"]}_UniqueDays.png')
    plt.close(fig)


def plot_class_progress():
    # Load the gradebook
    gradebook = pd.read_csv('gradebook.csv')
    student_ids = gradebook['id'].values
    
    quiz_columns = [col for col in gradebook.columns if 'Quiz' in col]
    
    student_progress = {student_id: [] for student_id in gradebook['id']}
    due_dates=[]
    
    for quiz_name in quiz_columns:
        students_logged_this_quiz = set()
        if gradebook[quiz_name].isna().all():
            continue 
        
        assignment_id = gets.search_for_assignment(quiz_name)
        assignment = gets.get_assignment(assignment_id)
        due_dates.append(pd.to_datetime(assignment['due_at'], utc=True))
        passing_threshold = dp_process.get_pass_threshold(assignment['name'])
        passing_score = passing_threshold * assignment['points_possible']

        submissions = gets.get_assignment_submissions(assignment_id)
        for submission in submissions:
            if submission['user_id'] in student_ids and submission['user_id'] not in students_logged_this_quiz and submission['workflow_state'] == 'graded':
                score = submission.get('score')
                sub_time = submission['submitted_at']
                if sub_time is None:
                    sub_time = submission['graded_at']
                    if sub_time is None:
                        raise ValueError("failed to get a timestamp out of an assignment submission")
                if score is not None and score >= passing_score:
                    students_logged_this_quiz.add(submission['user_id'])
                    submitted_at = pd.to_datetime(sub_time)
                    student_progress[submission['user_id']].append(submitted_at)

    
    cumulative_quizzes_due = np.arange(1, len(due_dates) + 1)

    for student_id in student_progress:
        sorted_timestamps = sorted(student_progress[student_id])  # Sort timestamps
        cumulative_passes = np.arange(1, len(sorted_timestamps) + 1)
        student_progress[student_id] = list(zip(sorted_timestamps, cumulative_passes))
    
    fig, ax = plt.subplots(figsize=(10, 6))

    for student_id, progress in student_progress.items():
        if progress:  # Check if list is not empty
            dates, cumulative_passes = zip(*progress)  # Unpack dates and cumulative passes
            ax.plot(dates, cumulative_passes, 'o-')  # Plot with dots and lines on the axes object

    # Plotting course pacing on the same axes object
    ax.plot(due_dates, cumulative_quizzes_due, '-s', color='black', label="Course pacing", markersize=5, markerfacecolor='black')
    ax.axhline(y=9, color='blue', linestyle='--', label='D')
    ax.axhline(y=12, color='green', linestyle='--', label='C-')
    ax.axhline(y=17, color='orange', linestyle='--', label='B-')
    ax.axvline(x=datetime.datetime(2024, 4, 23), color='red', linestyle='-')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Quizzes Passed')
    ax.set_title('Cumulative Quizzes Passed by Each Student Over Time')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(loc='upper left')
    fig.tight_layout()

    if os.path.isdir('figs'):
        fig.savefig(f'figs/ClasswideProgress.png')
    plt.close(fig)

def main():
    return

if __name__ == '__main__':
    main()
