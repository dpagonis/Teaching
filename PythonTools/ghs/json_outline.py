import json


def print_json_outline(data, level=0, max_level=None):
    # If max_level is defined and reached, return without printing further
    if max_level is not None and level >= max_level:
        return
    
    indent = "  " * level
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{indent}- {key}:")
            print_json_outline(value, level + 1, max_level)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, dict):
                print(f"{indent}- List of Dicts Item {index + 1}: {', '.join(item.keys())}")
                for key, value in item.items():
                    print(f"{indent}- {key}:")
                    print_json_outline(value, level + 1, max_level)
            elif isinstance(item, list):
                print(f"{indent}- List of Lists Item {index + 1}")
                print_json_outline(item, level + 1, max_level)
            else:
                print(f"{indent}- List Item: {item}")
    else:
        print(f"{indent}- Value: {data}")

# Load JSON data from 'data.json' which is assumed to be in the same directory as the script
filename = 'data.json'  # The file 'data.json' should be in the current working directory

# Read the JSON data from the file
with open(filename, 'r') as file:
    json_data = json.load(file)

# Call the function with the JSON data and a max_level parameter
print_json_outline(json_data, max_level=3) 
