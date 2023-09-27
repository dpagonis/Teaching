from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
import os
import pandas as pd

def align_to_substructure(mol, template_mol):
    # Generate a substructure match between the template and the molecule
    match = mol.GetSubstructMatch(template_mol)
    
    # If a match is found, align the molecule to the template
    if match:
        AllChem.AlignMol(mol, template_mol, atomMap=list(zip(match, range(template_mol.GetNumAtoms()))))

def draw_molecule(smiles_string, output_filename):
    mol = Chem.MolFromSmiles(smiles_string)
    AllChem.Compute2DCoords(mol)

    template_smiles = "NCC(=O)O"  # A simple template (glycine) could be used for demonstration
    template_mol = Chem.MolFromSmiles(template_smiles)
    AllChem.Compute2DCoords(template_mol)

    align_to_substructure(mol, template_mol)

    img = Draw.MolToImage(mol)
    img.save(output_filename)


def main():
    folder_name = "png"

    # Create the 'png' subfolder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Read the amino acids from the CSV file
    df = pd.read_csv('aminoacids.csv')

    for index, row in df.iterrows():
        abbreviation = row['Abbreviation']
        smiles_string = row['SMILES']

        if pd.isna(smiles_string):
            print(f"SMILES string for {abbreviation} is missing.")
            continue

        output_filename = os.path.join(folder_name, f"{abbreviation}.png")
        print(f"Generating image for {abbreviation}...")
        
        draw_molecule(smiles_string, output_filename)
        print(f"Molecule image saved as {output_filename}")

if __name__ == "__main__":
    main()
