import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path



class periodictable:
    def __init__(self):
        self.table = {}
        
        
        # Get the directory where the current Python file is located
        current_dir = Path(__file__).resolve().parent

        # Define the relative path to your CSV file
        csv_rel_path = Path('tables/elements.csv')

        # Join the current directory with the relative path
        csv_path = current_dir / csv_rel_path

        # Check if the file exists
        if csv_path.exists():
            self.df = pd.read_csv(csv_path)
        else:
            raise FileNotFoundError(f"periodictable.py cannot find the elements CSV file at '{csv_path}'.")
        
        for _, row in self.df.iterrows():
            element = row.to_dict()
            self.table[element['symbol']] = element

    def element(self,val,lookupkey=None):
        if lookupkey is None:
            if type(val) is int:
                lookupkey = 'atomic_number'
            elif type(val) is str and len(val) < 3:
                lookupkey = 'symbol'
            elif type(val) is str:
                lookupkey = 'name'
            else:
                raise TypeError("val was not atomic number, symbol, or name")
        
        for _, item in self.table.items():
            if item[lookupkey] == val:
                return item
        
        # Explicitly return None if no element is found
        return None

    
    def property(self, element, prop):
        element_dict = self.element(element)
        if element_dict is not None:
            return element_dict[prop]
        else:
            return None

    
    def random(self, weighted=False):
        if weighted and np.random.uniform(0,1) < 0.9:
                atomicno = np.random.randint(1,31)
        else:
            atomicno = np.random.randint(1,119)
        return self.element(atomicno)
    
    def create_table(self, additional_properties=None):
        if additional_properties is None:
            additional_properties = []

        # Define the periodic table layout
        layout = [
            [1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 2],
            [3, 4, None, None, None, None, None, None, None, None, None, None, 5, 6, 7, 8, 9, 10],
            [ 11, 12, None, None, None, None, None, None, None, None, None, None,13,14,15,16,17,18],
            list(range(19, 37)),
            list(range(37, 55)),
            list(range(55, 57)) + list(range(71, 87)),
            list(range(87, 89)) + list(range(103, 119)),
            [None],
            [None,None]+list(range(57, 71)),
            [None,None]+list(range(89, 103)),
        ]

        # Generate the table data
        table_data = []
        for row in layout:
            table_row = []
            for atomic_number in row:
                cell = {
                    'class': 'empty',
                    'symbol': '',
                    'atomic_number': '',
                    'name': '',
                    'mass': None,
                    'extra_properties': {},
                    'border_class': ''

                }
                if atomic_number is not None:
                    for symbol, element in self.table.items():
                        if int(element['atomic_number']) == atomic_number:
                            cell = {
                                'class': '',
                                'symbol': element['symbol'],
                                'atomic_number': element['atomic_number'],
                                'name': element['name'],
                                'mass': element['atomic_weight'],
                                'extra_properties': {prop: element[prop] for prop in additional_properties},
                                'border_class': 'dashed-right-border' if int(element['atomic_number']) in (56, 88) else ('dashed-left-border' if int(element['atomic_number']) in (71, 103) else ''),
                            }
                table_row.append(cell)
            table_data.append(table_row)

         # Load the template and render the table
        env = Environment(loader=FileSystemLoader(""), trim_blocks=True, lstrip_blocks=True)
        env.filters["format_mass"] = format_mass
        template = env.get_template("periodic_table_template.html")
        rendered_table = template.render(table=table_data)

        return rendered_table  # Add this line

def format_mass(value):
    if isinstance(value, int):
        return "({:.0f})".format(value)
    elif value % 1 == 0:
        return "({:.0f})".format(value)
    else:
        return "{:.06f}".format(value).rstrip('0').rstrip(".")

        
# def main():
#     pt = periodictable()
#     additional_properties = []
#     custom_table_html = pt.create_table(additional_properties)
#     print(custom_table_html)

# # Save the custom table HTML to a file
#     with open('custom_periodic_table.html', 'w') as output_file:
#         output_file.write(custom_table_html)


# if __name__ == '__main__':
#     main()