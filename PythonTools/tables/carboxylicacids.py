import re

input_file = "crcacids.txt"
output_file = "cleaned_crcacids.txt"
csv_file = "carboxylic_acids.csv"

temp_pattern = re.compile(r'\d{2}(?=\s)')
name_pattern = re.compile(r'[A-Z][a-z]+')

with open(input_file, "r") as infile, open(output_file, "w") as outfile, open(csv_file, "w") as csvfile:
    compound_info = ""
    csvfile.write("formula,name,temp,pKa1,pKa2,pKa3,pKa4,pKa5\n")
    
    for line in infile:
        line = line.strip()

        # Ignore empty lines
        if not line:
            continue

        # Check if the line starts with a new compound
        if line.startswith("C") and not line.startswith("Cl"):
            if compound_info:
                # Process the current compound_info before starting a new one
                name_match = name_pattern.search(compound_info)
                formula = compound_info[:name_match.start()].replace(" ", "")
                name = name_match.group()
                rest = compound_info[name_match.end():].split()

                # Write output without brackets
                outfile.write(f"{formula} {name} {' '.join(rest)}\n")

                # Write CSV output
                csvfile.write(f"{formula},{name},")
                temp_written = False
                pKa_count = 0
                for item in rest:
                    if item.startswith("Step"):
                        continue
                    if temp_pattern.match(item):
                        if not temp_written:
                            csvfile.write(f"{item},")
                            temp_written = True
                    else:
                        csvfile.write(f"{item},")
                        pKa_count += 1

                csvfile.write("," * (5 - pKa_count) + "\n")

                # Reset the compound_info
                compound_info = ""

            # Start a new compound_info
            compound_info = line
        else:
            # Combine the line with the existing compound_info
            compound_info += " " + line

    # Process the last compound_info
    if compound_info:
        name_match = name_pattern.search(compound_info)
        formula = compound_info[:name_match.start()].replace(" ", "")
        name = name_match.group()
        rest = compound_info[name_match.end():].split()

        # Write output without brackets
        outfile.write(f"{formula} {name} {' '.join(rest)}\n")

        # Write CSV output
        csvfile.write(f"{formula},{name},")
        temp_written = False
        pKa_count = 0
        for item in rest:
            if item.startswith("Step"):
                continue
            if temp_pattern.match(item):
                if not temp_written:
                    csvfile.write(f"{item},")
                    temp_written = True
            else:
                csvfile.write(f"{item},")
                pKa_count += 1

        csvfile.write("," * (5 - pKa_count) + "\n")