import requests
import urllib.parse
import json
import subprocess
import os
import csv
from datetime import datetime, timedelta

from GHShtml import *

def file_is_recent(file_path, max_age_days=30):
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    if (datetime.now() - file_mod_time) < timedelta(days=max_age_days):
        return True
    else:
        return False

def get_cid(compound_name):
    
    csv_path='cid.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['name'].lower() == compound_name.lower():
                    date_retrieved = datetime.strptime(row['date_retrieved'], '%Y-%m-%d')
                    if (datetime.now() - date_retrieved).days < 30:
                        # The CID is recent enough to use
                        return row['cid']
    
    # If the compound is not in the CSV or the date is too old, make the API call
    encoded_compound_name = urllib.parse.quote(compound_name)
    search_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded_compound_name}/cids/JSON'
    response = requests.get(search_url)

    if response.status_code == 200:
        data = response.json()
        cid = data['IdentifierList']['CID'][0]

        # Write the new CID to the CSV
        with open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Check if the CSV was empty and write the header
            if os.path.getsize(csv_path) == 0:
                writer.writerow(['name', 'CAS', 'cid', 'date_retrieved'])
            # Write the compound data
            writer.writerow([compound_name, '', cid, datetime.now().strftime('%Y-%m-%d')])
        
        return cid
    else:
        err = f"{response.status_code}: There was an error with the CID request."
        print(err)
        return None

# Function to get GHS classification for a given compound name using the PubChem API
def get_process_pubchem_data(compound_name):
    
    cid = get_cid(compound_name)
    
    cache_folder = 'data'
    cache_file_path = os.path.join(cache_folder, f'{cid}.json')

    # Check if the file exists and is recent
    if os.path.exists(cache_file_path) and file_is_recent(cache_file_path):
        print(f"Using cached data for CID: {cid}")
        with open(cache_file_path, 'r') as file:
            data = json.load(file)
    else:
        search_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?SourceID=GHS+Classification'

        try:
            # Make the request to the PubChem API
            response = requests.get(search_url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the response JSON data
            data = response.json()
            
            with open(f'data/{cid}.json', 'w') as file:
                json.dump(data, file, indent=4)
    
        except requests.HTTPError as http_err:
            return f'HTTP error occurred: {http_err}'
        except Exception as err:
            return f'Other error occurred: {err}'

    name = data['Record']['RecordTitle']
    SafetyInfo = next((item for item in data['Record']['Section'] if item['TOCHeading'] == 'Safety and Hazards'), None)
    if SafetyInfo:
        HazardID = next((item for item in SafetyInfo['Section'] if item['TOCHeading'] == 'Hazards Identification'), None)
        if HazardID:
            GHS = next((item for item in HazardID['Section'] if item['TOCHeading'] == 'GHS Classification'), None)
            if GHS:
                process_GHS(GHS, name)
                return True
    else:
        return 'No GHS classification information found for this compound.'

def process_GHS(GHS, name):
    pictogram_list = []
    pictogram_keywords = []
    signal_word = None
    hazard_statements = []
    
    #Get the name
    

    #Get the list of svgs to render and their keywords
    Pictograms = next((item for item in GHS['Information'] if item['Name'] == 'Pictogram(s)'), None)
    if Pictograms:
        Markup = Pictograms['Value']['StringWithMarkup'][0]['Markup']
        if Markup:
            for m in Markup:
                url = m['URL']
                pictogram_file = url.split('/')[-1]
                pictogram_list.append(pictogram_file)
                pictogram_keywords.append(m['Extra'])


    #Get the Signal word for the compound
    Signal = next((item for item in GHS['Information'] if item['Name'] == 'Signal'), None)
    if Signal:
        signal_word = Signal['Value']['StringWithMarkup'][0]['String']

    #Get the hazard statements
    HazStatements = next((item for item in GHS['Information'] if item['Name'] == 'GHS Hazard Statements'), None)
    if HazStatements:
        Statements = HazStatements['Value']['StringWithMarkup']
        if Statements:
            for s in Statements:
                statement = s['String']
                hazard_statements.append(statement)
    
    
    print('pictogram_keywords',pictogram_keywords)
    print('signal word',signal_word)
    for s in hazard_statements:
        print(s)

    generate_html(name,pictogram_list, signal_word, hazard_statements)

if __name__ == "__main__":
    # Call the function with "acetone" as the argument
    compound_name = input('Enter compound name:')
    resp = get_process_pubchem_data(compound_name)
    if resp is True:
        file_path = os.path.abspath('safety_information.html')
        subprocess.run(['start', file_path], shell=True)
