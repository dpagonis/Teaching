import re

from .periodictable import periodictable as pt
from .sigfig import sigfig as sf

periodictable = pt() #load pt at the module level so it doesn't have to happen with every new instance of molecule

class molecule:
    """
    Represents a chemical molecule and provides methods for molecular calculations and manipulations.
    
    Args:
        molec_string (str): The chemical formula of the molecule.
        charge (int, optional): The charge of the molecule (default is 0).
        phase (str, optional): The phase of the molecule (e.g., 'gas', 'liquid') (default is None).
        coefficient (int, optional): Coefficient for balancing chemical reactions (default is None).
        concentration (float, optional): Concentration of the molecule in a reaction (default is None).
    
    Attributes:
        charge (int): The total charge of the molecule.
        formula (str): The chemical formula of the molecule.
        element_dict (dict): A dictionary with elements as keys and their corresponding counts as values.
        molecular_weight (sf): The molecular weight of the molecule (in g mol^-1).
        tex (str): LaTeX formatted representation of the molecule's formula.
        phase (str): The phase of the molecule.
        coefficient (int): Coefficient for balancing chemical reactions.
        concentration (float): Concentration of the molecule in a reaction.
    
    Methods:
        add(addstr): Adds another molecule or chemical formula to the current molecule.
        subtract(substr): Subtracts another molecule or chemical formula from the current molecule.
    """
    
    def __init__(self, molec_string, charge=0, phase=None, coefficient=None, concentration=None):
        #note that if you include charge in molec_string and in the charge argument it will be double-counted
        self.charge = charge
        while '+' in molec_string:
            self.charge += 1
            molec_string = molec_string.replace('+', '', 1)
        while '-' in molec_string:
            self.charge -= 1
            molec_string = molec_string.replace('-', '', 1)
        self.formula = molec_string
        
        self.element_dict = self._parse_formula(molec_string)
        self.molecular_weight = self._calculate_molecular_weight()
        self.tex = self._generate_formula_tex()
        self.simple_html = self._generate_simple_html()

        self.phase = str(phase) if phase is not None else None
        self.coefficient = coefficient
        self.concentration = concentration
        
    def _parse_formula(self, formula_str):
        
        element_dict = {}
        
        if formula_str == 'e':
            element_dict['e-']=1
            return element_dict

        while formula_str:
            # If the formula starts with a parenthesis, find the subgroup
            if formula_str[0] == '(':
                end_index = formula_str.index(')')
                subgroup_str = formula_str[1:end_index]
                
                # Recursively create a Molecule object for the subgroup
                subgroup_mol = molecule(subgroup_str)
                
                # Extract the count following the subgroup, if present
                rest_str = formula_str[end_index+1:]
                match = re.match(r'(\d+)', rest_str)
                if match:
                    subgroup_count = int(match.group())
                    rest_str = rest_str[match.end():]
                else:
                                    subgroup_count = 1
                
                # Add the counts of each element in the subgroup, multiplied by its count, to the total element dictionary
                for element, count in subgroup_mol.element_dict.items():
                    if element in element_dict:
                        element_dict[element] += count * subgroup_count
                    else:
                        element_dict[element] = count * subgroup_count

                # Update the formula to continue with the rest of it
                formula_str = rest_str

            # If the formula doesn't start with a parenthesis, find the first atomic component and its count
            else:
                match = re.match(r'([A-Z][a-z]?)(\d*)', formula_str)
                if match:
                    element = match.group(1)
                    count_str = match.group(2)
                    count = int(count_str) if count_str else 1
                    if element in element_dict:
                        element_dict[element] += count
                    else:
                        element_dict[element] = count
                    formula_str = formula_str[match.end():] 

        return element_dict

    
    def _calculate_molecular_weight(self):
        
        # Create a copy of the formula to work with
        formula = self.formula

        molecular_weight = sf('0',sig_figs=999,units_str="g mol-1")

        if formula == 'e':
            return molecular_weight

        while formula:
            # If the formula starts with a parenthesis, find the subgroup
            if formula[0] == '(':
                end_index = formula.index(')')
                subgroup_str = formula[1:end_index]

                # Recursively create a Molecule object for the subgroup
                subgroup_mol = molecule(subgroup_str)
                
                # Extract the count following the subgroup, if present
                rest_str = formula[end_index+1:]
                match = re.match(r'(\d+)', rest_str)
                if match:
                    subgroup_count = int(match.group())
                    rest_str = rest_str[match.end():]
                else:
                    subgroup_count = 1
                
                # Add the molecular weight of the subgroup, multiplied by its count, to the total molecular weight
                molecular_weight += subgroup_mol.molecular_weight * subgroup_count

                # Update the formula to continue with the rest of it
                formula = rest_str

            # If the formula doesn't start with a parenthesis, find the first atomic component and its count
            else:
                match = re.match(r'([A-Z][a-z]?)(\d*)', formula)
                if match:
                    element = match.group(1)
                    count = match.group(2)
                    atomic_mass = sf(str(periodictable.property(element, prop='mass')))
                    if count:
                        atomic_mass *= int(count)
                    molecular_weight += atomic_mass
                    formula = formula[match.end():]

        return molecular_weight

    def _generate_formula_tex(self):
        # Add subscript inside parentheses
        tex_string = re.sub(r'\((.*?)\)', lambda m: '(' + re.sub(r'([A-Z][a-z]*)(\d+)', r'\1_{\2}', m.group(1)) + ')', self.formula)
        # Add subscript outside parentheses
        tex_string = re.sub(r'([A-Za-z\(\)]+)(\d+)', r'\1_{\2}', tex_string)
        
        if self.charge == 1:
            tex_string += '^{+}'
        elif self.charge == -1:
            tex_string += '^{-}'
        elif self.charge > 1:
             tex_string += '^{'+f'{abs(self.charge)}'+'+}'
        elif self.charge < -1:
             tex_string += '^{'+f'{abs(self.charge)}'+'-}'
        
        return tex_string
    
    def _generate_simple_html(self):

        formula_string = self.formula 
        if self.charge >= 1:
             formula_string += abs(self.charge)*'+'
        elif self.charge <= -1:
             formula_string += abs(self.charge)*'-'

        # Replace all numbers with <sub> tags
        simple_html_string = re.sub(r'(\d+)', r'<sub>\1</sub>', formula_string)
        
        # Replace consecutive + and - with <sup> tags
        simple_html_string = re.sub(r'([+-]+)', r'<sup>\1</sup>', simple_html_string)

        return simple_html_string
    
    def add(self, addstr):
        # Initialize a temporary molecule with addstr
        if isinstance(addstr,molecule):
            temp_molec=addstr
        else:
            temp_molec = molecule(addstr)
        
        # Create a new dictionary for the new formula
        new_formula_dict = dict(self.element_dict)  # Make a copy of the original dict

        # For each element in temp_molec's element_dict, increment its count in new_formula_dict
        for element, count in temp_molec.element_dict.items():
            if element in new_formula_dict:
                new_formula_dict[element] += count
            else:
                new_formula_dict[element] = count

        # Construct the new formula string from new_formula_dict
        new_formula = ''
        for element, count in sorted(new_formula_dict.items()):  # Sort by element symbol for consistency
            new_formula += element
            if count > 1:
                new_formula += str(count)

        new_charge = self.charge + temp_molec.charge

        # Create a new molecule instance
        new_molec = molecule(new_formula,charge=new_charge)

        return new_molec
    
    def subtract(self, substr):
        # Initialize a temporary molecule with substr
        if isinstance(substr,molecule):
            temp_molec=substr
        else:
            temp_molec = molecule(substr)
        
        # Create a new dictionary for the new formula
        new_formula_dict = dict(self.element_dict)  # Make a copy of the original dict

        # For each element in temp_molec's element_dict, decrement its count in new_formula_dict
        for element, count in temp_molec.element_dict.items():
            if element in new_formula_dict:
                if new_formula_dict[element] < count:
                    raise ValueError(f"Cannot subtract more {element} than present in the molecule.")
                new_formula_dict[element] -= count
                if new_formula_dict[element] == 0:
                    del new_formula_dict[element]
            else:
                raise ValueError(f"{element} is not present in molecule {self.formula} / {temp_molec.formula} to subtract.")

        # Construct the new formula string from new_formula_dict
        new_formula = ''
        for element, count in sorted(new_formula_dict.items()):  # Sort by element symbol for consistency
            new_formula += element
            if count > 1:
                new_formula += str(count)
        
        new_charge = self.charge - temp_molec.charge

        # Create a new molecule instance
        new_molec = molecule(new_formula, charge=new_charge)

        return new_molec

    def __str__(self):
        if self.charge > 0:
            chargestr = '+' * self.charge
        elif self.charge < 0:
            chargestr = '-' * abs(self.charge)
        else:
            chargestr = ''
            
        return self.formula + chargestr
        
def main():
    test = molecule('H2O')
    print(test, test.charge)
    new = test.subtract('H+')
    print(new, new.charge)


if __name__ == '__main__':
    main()