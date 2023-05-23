import re

class units:
    unit_categories = {
            'distance': ['m', 'ft', 'in', 'mi'],
            'time': ['s', 'min', 'h', 'hr', 'd', 'day', 'hour'],
            'mass': ['kg', 'g', 'lb', 'oz'],
            'temperature': ['K', 'C', 'F'],
            'current': ['A'],
            'amount': ['mol', 'molec', 'mQ', 'molecules'],
            'volume': ['L', 'gal'],
            'energy': ['J','cal','Cal'],
            'frequency': ['Hz'],
            'force': ['N'],
            'pressure': ['Pa','bar','mmHg','Torr','atm','psi'],
            'power': ['W']
        }
    
    si_prefixes = {
            'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15,
            'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3,
            'h': 1e2, 'da': 1e1, 'd': 1e-1, 'c': 1e-2,
            'm': 1e-3, 'µ': 1e-6, 'n': 1e-9, 'p': 1e-12,
            'f': 1e-15, 'a': 1e-18, 'z': 1e-21, 'y': 1e-24
        }
    
    categories_si = {
            'distance': 'm',
            'time': 's',
            'mass': 'kg',
            'temperature': 'K',
            'current': 'A',
            'amount': 'mol',
            'volume': 'm3',
            'energy': 'kg m2 s-2',
            'frequency': 's-1',
            'force': 'kg m s-2',
            'pressure': 'kg m-1 s-2',
            'power': 'kg m2 s-3'
        }

    to_si_factors = {
            'ft': 0.3048,     # foot to meter
            'in': 0.0254,     # inch to meter
            'mi': 1609.34,    # mile to meter
            'min': 60,        # minute to second
            'h': 3600,        # hour to second
            'hr': 3600,       # hour to second
            'd': 86400,       # day to second
            'day': 86400,     # day to second
            'g': 1e-3,        # gram to kilogram
            'lb': 0.453592,   # pound to kilogram
            'oz': 0.0283495,  # ounce to kilogram
            # 'C': 'x+273.15',           # Celsius to Kelvin; note: requires offset
            # 'F': '(x-32)*5/9',         # Fahrenheit to Kelvin; note: requires offset and scaling
            'molec':  1 / 6.02214076e23,  # molecules to mole
            'mQ':  1 / 6.02214076e23,  # molecules to mole
            'molecules': 1 / 6.02214076e23,  # molecules to mole
            'L': 1e-3,        # liter to cubic meter
            'gal': 0.00378541, # US gallon to cubic meter
            'cal': 4.184,     # calorie to joule
            'Cal': 4184,      # Calorie (kilocalorie) to joule
            'bar': 1e5,       # bar to pascal
            'mmHg': 133.322,  # millimeter of mercury to pascal
            'Torr': 133.322,  # torr to pascal
            'atm': 101325,    # standard atmosphere to pascal
            'psi': 6894.76,   # pound-force per square inch to pascal
        }


    def __init__(self, units_str):
        self.units_str = units_str
        self.to_si_factor = 1
        self.unit_coefs = self._parse_units()
        self.units_str_si = self._construct_si_units_str()
        self.unit_type = self._determine_unit_type()

    def _parse_units(self, str_to_parse=None):

        str_to_parse = self.units_str if str_to_parse is None else str_to_parse    

        unit_exponents = {
            'mass': 0,
            'distance': 0,
            'time': 0,
            'temperature': 0,
            'current': 0,
            'amount': 0
        }

        unit_list = str_to_parse.split()
        for unit_exp in unit_list:
            # Extract the unit and exponent if present
            match = re.match(r'([a-zA-Zµ]+)([-0-9]*)', unit_exp)
            if match:
                unit, exp = match.groups()

                # Check for base unit and prefix
                for category, units in self.unit_categories.items():
                    for base_unit in units:                    
                        if unit.endswith(base_unit):
                            prefix = unit.rstrip(base_unit)

                            # Check for exponent
                            exponent = int(exp) if exp else 1
                            
                            if category in unit_exponents:  # if category is a key in unit_exponents
                                unit_exponents[category] += exponent
                            else:  # recursively parse units string from categories_si
                                si_unit_str = self.categories_si[category]
                                si_unit_str = f"{si_unit_str}{exp}"
                                si_unit_exponents = self._parse_units(si_unit_str)
                                for si_category, si_exponent in si_unit_exponents.items():
                                    unit_exponents[si_category] += si_exponent * exponent

                            # Adjust self.to_si_factor with conversion factor and prefix
                            conv_factor = self.to_si_factors.get(base_unit, 1)
                            prefix_factor = self.si_prefixes.get(prefix, 1)
                            self.to_si_factor *= (conv_factor * prefix_factor) ** exponent
                            break
        return unit_exponents

    def _construct_si_units_str(self):
        units_str_si_parts = []
        for category, exponent in self.unit_coefs.items():
            if exponent != 0:
                si_unit = self.categories_si[category]
                units_str_si_part = f"{si_unit}{exponent if exponent != 1 else ''}"
                units_str_si_parts.append(units_str_si_part)
        return ' '.join(units_str_si_parts)

    def _determine_unit_type(self):
        for unit_type, si_units_str in self.categories_si.items():
            if self.units_str_si == si_units_str:
                return unit_type
        return None

    def __str__(self):
        return self.units_str
    
    def convert_to(self, output_unit_str):
        output_unit = units(output_unit_str)
        
        factor = self.to_si_factor / output_unit.to_si_factor

        if output_unit.unit_type is not self.unit_type:
            factor = None

        return factor
    

def main():
    test_unit = units("day")
    print(test_unit.unit_coefs)
    print(test_unit.units_str_si)
    print(test_unit.unit_type)
    print(test_unit.to_si_factor)
    print(test_unit.convert_to('hr'))

if __name__ == "__main__":
    main()