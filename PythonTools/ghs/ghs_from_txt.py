import os
import subprocess

from ghs_v2 import get_process_pubchem_data

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


# Read compound names from a text file, one per line
with open('compounds.txt', 'r') as file:
    compound_names = file.read().splitlines()

# String to hold all the concatenated HTML body contents
all_bodies = ""

# Process each compound name
for i, name in enumerate(compound_names):
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

# Now, create the final HTML with all the concatenated body contents
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

# Overwrite the 'safety_information.html' with the new concatenated HTML content
with open('safety_information.html', 'w') as file:
    file.write(final_html_content)

# Open the final HTML file in the default browser
file_path = os.path.abspath('safety_information.html')
subprocess.run(['start', file_path], shell=True)
