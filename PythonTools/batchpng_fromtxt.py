from molpng import *

def batch_generate_pngs(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            compound_name = line.strip()
            if compound_name:
                output_filename = os.path.join("png", f"{compound_name}.png")
            
                smiles_string = get_smiles_from_pubchem(compound_name)
                if smiles_string:
                    print(f"SMILES string for {compound_name}: {smiles_string}")
                    draw_molecule(smiles_string, output_filename)
                    print(f"Molecule image saved as {output_filename}")
                else:
                    print(f"Molecule not found: {compound_name}")

            else:
                print("Empty line encountered, skipping.")

def main():
# Check if a command-line argument is provided
  if len(sys.argv) > 1:
      file_path = sys.argv[1]
  else:
      file_path = input("Enter the name of the file: ")

  batch_generate_pngs(file_path)


if __name__ == "__main__":
    main()
