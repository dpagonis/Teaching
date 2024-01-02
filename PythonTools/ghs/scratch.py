import requests
import os

# Function to download and save a single SVG file
def download_svg(ghs_number):
    url = f'https://pubchem.ncbi.nlm.nih.gov/images/ghs/GHS{ghs_number:02}.svg'
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'GHS{ghs_number:02}.svg', 'wb') as file:
            file.write(response.content)
    else:
        print(f'Failed to download GHS{ghs_number:02}.svg')

# Download SVGs for GHS numbers 01 through 09
for ghs_number in range(1, 10):
    download_svg(ghs_number)
