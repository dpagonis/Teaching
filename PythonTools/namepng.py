import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
import os
import sys


def get_smiles_from_pubchem(compound_name):
    compound = pcp.get_compounds(compound_name, 'name')
    if compound:
        return compound[0].isomeric_smiles
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
        compound_name = sys.argv[1]
    else:
        compound_name = input("Enter the name of a molecule: ")

    output_filename = os.path.join(folder_name, f"{compound_name}.png")


    smiles_string = get_smiles_from_pubchem(compound_name)
    if smiles_string:
        print(f"SMILES string: {smiles_string}")
        draw_molecule(smiles_string, output_filename)
        print(f"Molecule image saved as {output_filename}")
    else:
        print("Molecule not found")
        return

    # Open the PNG file
    if os.name == 'nt':  # Windows
        os.startfile(output_filename)
    elif os.name == 'posix':  # macOS and Linux
        os.system(f'xdg-open "{output_filename}"')
    else:
        print("Could not open the image file. Please open it manually.")

if __name__ == "__main__":
    main()
