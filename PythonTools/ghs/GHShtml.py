def generate_html(name,pictogram_list, signal_word, hazard_statements):
    pictograms_html = ''.join(f'<img src="{pict}" alt="Pictogram">' for pict in pictogram_list)
    hazard_statements_html = format_hazard_statements(hazard_statements)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Safety Information</title>
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
    <div class="compound-name">
        {name}
    </div>
    <div class="pictograms">
        {pictograms_html}
    </div>
    <div class="signal-word">
        Signal Word: {signal_word}
    </div>
    <ul class="hazard-statements">
        {hazard_statements_html}
    </ul>
</body>
</html>"""
    with open('safety_information.html', 'w') as file:
        file.write(html_content)

def format_hazard_statements(hazard_statements):
    # Separate the hazard statements into two groups
    danger_statements = [statement for statement in hazard_statements if "[Danger" in statement]
    warning_statements = [statement for statement in hazard_statements if "[Warning" in statement]

    # Sort each group if needed (alphabetically in this case, but could be any criteria)
    danger_statements.sort()
    warning_statements.sort()

    # Combine the lists with a blank list item as a separator
    combined_statements = danger_statements + [''] + warning_statements

    # Iterate over the combined list and format with HTML tags
    hazard_statements_html = ''.join(
        f'<li>{statement.replace("[Danger", "[<strong>Danger</strong>").replace("[Warning", "[<strong>Warning</strong>")}</li>'
        if statement else '<li style="list-style-type:none;">&nbsp;</li>'
        for statement in combined_statements
    )
    
    return hazard_statements_html   