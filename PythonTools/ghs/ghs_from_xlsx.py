import shutil
import os
import glob
import subprocess
import pandas as pd

from ghs_v2 import get_process_pubchem_data

EXCEL_FILE = 'Courses/CHEM3000.xlsx'

def extract_html_body(html_content, is_last_compound):
    # Utility function to extract the <body> content from a given HTML string
    body_start = html_content.find('<body>')
    body_end = html_content.find('</body>')
    
    if body_start != -1 and body_end != -1:
        # Extract body content and add an <hr> tag if it's not the last compound
        body_content = html_content[body_start + 6:body_end]  # +6 to move past the <body> tag itself
        if not is_last_compound:
            body_content += '<hr>'
        return body_content
    else:
        return ""

def process_compounds(compound_names, experiment_name, output_directory):
    all_bodies = ""
    
    # Process each compound name
    for i, name in enumerate(compound_names):
        if pd.isnull(name):  # Skip empty cells
            continue
        # Call your existing function to generate the HTML
        status = get_process_pubchem_data(name)
        
        if status is True:
            # Read the generated HTML file
            with open('safety_information.html', 'r') as file:
                html_content = file.read()
                
            # Check if this is the last compound
            is_last_compound = (i == len(compound_names) - 1)
            
            # Extract the body content, including an <hr> if not the last compound
            all_bodies += extract_html_body(html_content, is_last_compound)
        else:
            err_html = f"<div class=\"compound-name\">{name}</div><ul class=\"hazard-statements\">Error: compound retrieval failed</ul><hr>"
            all_bodies += err_html
    
    # Create the final HTML content
    final_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compound Safety Information</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .compound-name {{ font-size: 32px; font-weight: bold; margin-bottom: 20px; }}
        .pictograms {{ display: flex; }}
        img {{ max-width: 100px; max-height: 100px; margin-right: 10px; }}
        .signal-word {{ font-weight: bold; font-size: 24px; }}
        .hazard-statements {{ list-style-type: none; padding: 0; }}
    </style>
</head>
<body>
    {all_bodies}
</body>
</html>"""
    
    # Write to a HTML file named after the experiment
    html_filename = f"{output_directory}/{experiment_name}.html"
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(final_html_content)

# Read the Excel file
df = pd.read_excel(EXCEL_FILE, sheet_name=0)  # Assumes the compounds are in the first sheet

# Directory to store the HTML files, named after the Excel file without the extension
output_directory = EXCEL_FILE.rsplit('.', 1)[0]
os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist

# List to hold all the links to the experiment HTML files
experiment_links = []

# Iterate over each experiment (column)
for experiment_name in df.columns:
    compound_names = df[experiment_name].dropna().tolist()  # List of compounds for the experiment
    process_compounds(compound_names, experiment_name, output_directory)
    
    # Add a link for the experiment to the list
    experiment_links.append(f'<li><a href="{experiment_name}.html">{experiment_name}</a></li>')

# Generate the directory index HTML content
directory_index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experiment Directory</title>
</head>
<body>
    <h1>Experiment Directory</h1>
    <ul>
        {''.join(experiment_links)}
    </ul>
</body>
</html>"""

# Write the directory index HTML file
index_html_filename = f"{output_directory}/index.html"
with open(index_html_filename, 'w', encoding='utf-8') as file:
    file.write(directory_index_html)


# Move all the SVGs into the course folder
source_dir = os.getcwd()
for svg_file in glob.glob(os.path.join(source_dir, 'GHS*.svg')):
    shutil.copy(svg_file, output_directory)


# Open the directory index HTML file in the default browser
index_html_path = os.path.abspath(index_html_filename)
subprocess.run(['start', index_html_path], shell=True)
