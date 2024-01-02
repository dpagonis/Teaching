import pubchempy as pcp
import csv

from dp_qti import sf

# Function to get logP value for a given compound name
def get_logp(compound_name):
    try:
        results = pcp.get_compounds(compound_name, 'name')
        if results:
            return results[0].xlogp
    except Exception as e:
        print(f"An error occurred while fetching logP for {compound_name}: {e}")
    return None

# Add more functions to fetch other properties here
# For example:
# def get_molecular_weight(compound_name):
#     ...

# Main function to fetch properties and write to CSV
def write_properties_to_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write the header row with the properties you want to include
        writer.writerow(['Molecule Name', 'K_ow'])  # Add more headers for new properties

        for row in reader:
            compound_name = row[0]
            
            # Fetch all properties
            logp = get_logp(compound_name)
            K_ow = sf(str(logp)).exponent(base=10) if logp else None
            # You can fetch more properties here and add them to the properties list
            
            # Write the row for the current compound
            writer.writerow([compound_name, K_ow])

# File names
input_file = 'organic_molecules.txt'
output_file = 'organics.csv'

# Execute the main function
write_properties_to_csv(input_file, output_file)
