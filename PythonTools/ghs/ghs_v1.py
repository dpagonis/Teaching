import requests
import urllib.parse
import json

# Function to get GHS classification for a given compound name using the PubChem API
def get_ghs_classification(compound_name):
    # Define the PubChem API endpoint for property search
    
    encoded_compound_name = urllib.parse.quote(compound_name)

    # Create the search URL
    search_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded_compound_name}/cids/JSON'

    # Make the request
    response = requests.get(search_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the CID from the response
        cid = data['IdentifierList']['CID'][0]
        print(f"The CID for {compound_name} is: {cid}")
    else:
        err = f"{response.status_code}: There was an error with the CID request."
        print(err)
        return err
    
    search_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/classification/JSON'
    
    try:
        # Make the request to the PubChem API
        response = requests.get(search_url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the response JSON data
        data = response.json()
        properties = data.get('PropertyTable', {}).get('Properties', [])
        
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)

        if properties:
            # Assuming the first result is the most relevant, extract the GHS information
            ghs_data = properties[0]
            signal_word = ghs_data.get('GHSSignalWord', 'Not available')
            hazard_statements = ghs_data.get('GHSStatements', 'Not available')
            
            # Display the GHS classification information
            return {
                'Signal Word': signal_word,
                'Hazard Statements': hazard_statements
            }
        else:
            return 'No GHS classification information found for this compound.'
    
    except requests.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}'
    except Exception as err:
        return f'Other error occurred: {err}'

# Call the function with "acetone" as the argument
acetone_ghs_info = get_ghs_classification("acetone")
print(acetone_ghs_info)
