import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem.Draw import MolDraw2DSVG
from rdkit.Chem.Draw import IPythonConsole
from IPython.display import SVG
import os

def get_smiles_from_pubchem(compound_name):
    compound = pcp.get_compounds(compound_name, 'name')
    if compound:
        return compound[0].isomeric_smiles
    return None

def draw_molecule(smiles_string, output_filename):
    mol = Chem.MolFromSmiles(smiles_string)

    # Initialize the drawing options
    drawer = MolDraw2DSVG(300, 300)
    drawing_options = drawer.drawOptions()

    drawing_options.atomLabelFontSize = 48
    drawing_options.useBWAtomPalette()

    # Draw the molecule and save the SVG to a file
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    with open(output_filename, 'w') as f:
        f.write(drawer.GetDrawingText())

def main():
    compound_name = input("Enter the name of a molecule: ")
    folder_name = "svg"

    # Create the 'png' subfolder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    output_filename = os.path.join(folder_name, f"{compound_name}.svg")

    if not os.path.exists(output_filename):
        smiles_string = get_smiles_from_pubchem(compound_name)
        if smiles_string:
            print(f"SMILES string: {smiles_string}")
            draw_molecule(smiles_string, output_filename)
            print(f"Molecule image saved as {output_filename}")
        else:
            print("Molecule not found")
            return

    # Open the SVG file
    if os.name == 'nt':  # Windows
        os.startfile(output_filename)
    elif os.name == 'posix':  # macOS and Linux
        os.system(f'xdg-open "{output_filename}"')
    else:
        print("Could not open the image file. Please open it manually.")

if __name__ == "__main__":
    main()
