import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
import os
import sys

def get_common_name_from_pubchem(smiles_string):
    compound = pcp.get_compounds(smiles_string, 'smiles')
    if compound:
        return compound[0].iupac_name
    return None

def draw_molecule(smiles_string, output_filename):
    mol = Chem.MolFromSmiles(smiles_string)
    AllChem.Compute2DCoords(mol)
    AllChem.StraightenDepiction(mol)
    img = Draw.MolToImage(mol)

    # Save the image as a PNG file
    img.save(output_filename)

def main():
    folder_name = "png"

    # Create the 'png' subfolder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Check if a command-line argument is provided
    if len(sys.argv) > 1:
        smiles_string = sys.argv[1]
    else:
        smiles_string = input("Enter a SMILES string: ")

    common_name = get_common_name_from_pubchem(smiles_string)

    if common_name:
        output_filename = os.path.join(folder_name, f"{common_name}.png")
        print(f"name found: {common_name}")
    else:
        output_filename = os.path.join(folder_name, f"{smiles_string}.png")
        print(f"no name found, saving using smiles")

    draw_molecule(smiles_string, output_filename)

    # Open the PNG file
    if os.name == 'nt':  # Windows
        os.startfile(output_filename)
        print(output_filename)
    elif os.name == 'posix':  # macOS and Linux
        os.system(f'xdg-open "{output_filename}"')
    else:
        print("Could not open the image file. Please open it manually.")

if __name__ == "__main__":
    main()
