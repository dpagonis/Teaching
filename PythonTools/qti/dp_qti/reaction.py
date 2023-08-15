import re
from itertools import permutations

from .molecule import molecule




class reaction:
    """
    Class representing a chemical reaction.

    Attributes:
        isbalanced (bool): Boolean result of checking charge and mass balance.
        plaintext (str): String with plain text representation of the reaction.
        plaintext_answers (str): All permutations of order in plaintext.
        Q_eqn (str): String with plain text representation of the reaction coefficient.
        Q_eqn_answers (str): All permutations of order in Q_eqn.
        Q_tex (str): TeX representation of the reaction quotient.
        reactants (list): Lists of molecule objects representing the reactants.
        products (list): Lists of molecule objects representing the products.
        reversible (bool): Boolean that determines what type of arrow goes in self.tex.
        tex (str): String with reaction as TeX.

    Methods:
        setconcentration(formula, conc): Function to set the concentration of a given molecule. Pass the formula as a string.
    """


    def __init__(self, reactants, products=None,reversible=True,k=None):

        # Introducing flag to track if initial setup is in progress
        self._initializing = True
        
        if "=" in reactants and products is None: #entered the whole reaction directly as a string
            reactants, products = reactants.split("=")

        self.reactants = self._parse_and_validate_input(reactants)
        self.products = self._parse_and_validate_input(products)
        self.reversible = reversible
        self.k=k
        # End of initialization
        self._initializing = False
        self._update()  # Call update once at the end of initialization

    @property
    def reactants(self):
        return self._reactants

    @reactants.setter
    def reactants(self, new_value):
        self._reactants = self._parse_and_validate_input(new_value)
        if not self._initializing and hasattr(self, '_products'):  # Check if _products exists and we are not in initialization phase
            self._update()

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, new_value):
        self._products = self._parse_and_validate_input(new_value)
        if not self._initializing and hasattr(self, '_reactants'):  # Check if _reactants exists and we are not in initialization phase
            self._update()

    def _update(self):
        self.plaintext, self.plaintext_answers = self._generate_rxn_plain_text()
        self.tex = self._generate_rxn_tex()
        self.isbalanced = self._check_balance()
        self.Q_eqn, self.Q_eqn_answers, self.Q_tex, self.Q = self._generate_rxn_quotient()
        self.rate_eqn, self.rate_eqn_answers, self.rate_eqn_tex, self.rate = self._generate_rate_expression()

    def _parse_and_validate_input(self, input_val):
        if isinstance(input_val, str):
            return self._parse_input_str(input_val)
        elif isinstance(input_val, molecule):
            return [input_val]
        elif isinstance(input_val, list) and all(isinstance(i, str) for i in input_val):
            return[self._parse_compound_str(i) for i in input_val]
        elif isinstance(input_val, list) and all(isinstance(i, molecule) for i in input_val):
            return input_val
        else:
            s = f'list of {type(input_val[0])}' if isinstance(input_val, list) else type(input_val)
            raise TypeError(f'{self.__class__.__name__} was passed a {s} as input. input = {input_val}')

    def _parse_compound_str(self,s):
        s_in = s
        s = s.strip()
        phase_re = re.compile(r'\(([a-z\s]+)\)$')
        coef_formula_re = re.compile(r'(\d+)?([A-Za-z\(\)\d\+\-]+)')

        phase_match = phase_re.search(s)

        if phase_match:
            phase = phase_match.group(1)
            s = s[:phase_match.start()]  # remove the phase from the string
        else:
            phase = None  # if no phase is found
        
        coef_formula_match = coef_formula_re.match(s.strip())  # strip any whitespace

        if not coef_formula_match:
            raise ValueError(f"Invalid compound format: {s_in}")

        coef = int(coef_formula_match.group(1)) if coef_formula_match.group(1) else 1
        formula = coef_formula_match.group(2)
        return molecule(formula, coefficient=coef, phase=phase)  # list of molecule objects

    def _parse_input_str(self,s):
        compound_list = s.split(' + ')
        return [self._parse_compound_str(c) for c in compound_list]
        
        
    def _generate_rxn_plain_text(self):
        def _get_rxn_term(m):
            coef_str = f'{m.coefficient}' if m.coefficient > 1 else ''
            phase_str = f'({m.phase})' if m.phase is not None else ''
            return coef_str+str(m)+phase_str
        
        reactant_terms = [_get_rxn_term(m) for m in self.reactants]
        product_terms = [_get_rxn_term(m) for m in self.products]
        
        plaintext = f'{" + ".join(reactant_terms)}'+' = '+f'{" + ".join(product_terms)}'
        
        reactant_perm = list(permutations(reactant_terms))
        product_perm = list(permutations(product_terms))
        all_combinations = [(r, p) for r in reactant_perm for p in product_perm]
        all_answer = [f'{" + ".join(r)}'+' = '+f'{" + ".join(p)}' for r,p in all_combinations]
        plaintext_answers=';'.join(all_answer)

        return plaintext,plaintext_answers
    
    
   
    def _generate_rxn_tex(self):
        reactant_terms = [f'{m.coefficient if m.coefficient != 1 else ""}{m.tex}{"("+m.phase+")" if m.phase else ""}' for m in self.reactants]
        product_terms = [f'{m.coefficient if m.coefficient != 1 else ""}{m.tex}{"("+m.phase+")" if m.phase else ""}' for m in self.products]
        
        arrow = '\\leftrightarrows{}' if self.reversible is True else '\\rightarrow{}'

        tex = f'{"+".join(reactant_terms)}'+arrow+f'{"+".join(product_terms)}'
        return tex
    
    def _check_balance(self):
        
        charge_reactants = sum([m.charge for m in self.reactants])
        charge_products = sum([m.charge for m in self.products])

        # Cumulative element dictionary for reactants
        reactant_elements = {}
        for m in self.reactants:
            for elem, count in m.element_dict.items():
                if elem == 'e-':  # Skip if the element is 'e-'
                    continue
                if elem in reactant_elements:
                    reactant_elements[elem] += count*m.coefficient
                else:
                    reactant_elements[elem] = count*m.coefficient

        # Cumulative element dictionary for products
        product_elements = {}
        for m in self.products:
            for elem, count in m.element_dict.items():
                if elem == 'e-':  # Skip if the element is 'e-'
                    continue
                if elem in product_elements:
                    product_elements[elem] += count*m.coefficient
                else:
                    product_elements[elem] = count*m.coefficient

        # Check if the two dictionaries match and charges are the same
        if reactant_elements == product_elements and charge_reactants == charge_products:
            return True
        else:
            return False

    def _generate_rxn_quotient(self):
        reactants = [m for m in self.reactants if (str(m) != 'e-' and m.phase is None)]
        products = [m for m in self.products if (str(m) != 'e-' and m.phase is None)]
        
        reactant_terms = [f'[{m}]^{m.coefficient}' if m.coefficient > 1 else f'[{m}]' for m in reactants]
        product_terms = [f'[{m}]^{m.coefficient}' if m.coefficient > 1 else f'[{m}]' for m in products]

        Q_eqn = f'{"".join(product_terms)}'+('/' if len(reactant_terms)>0 and len(product_terms)>0 else '')+f'{"".join(reactant_terms)}'

        reactant_perm = list(permutations(reactant_terms))
        product_perm = list(permutations(product_terms))

        all_combinations = [(r, p) for r in reactant_perm for p in product_perm]
        all_Q = [f'{"".join(p)}'+('/' if len(r)>0 and len(p)>0 else '')+f'{"".join(r)}' for r,p in all_combinations]
        Q_eqn_answers=';'.join(all_Q)

        reactant_terms_tex = [f'[{m.tex}]^{{{m.coefficient}}}' if m.coefficient > 1 else f'[{m.tex}]' for m in reactants]
        product_terms_tex = [f'[{m.tex}]^{{{m.coefficient}}}' if m.coefficient > 1 else f'[{m.tex}]' for m in products]
        Q_tex = f'\\frac{{{"".join(product_terms_tex)}}}{{{"".join(reactant_terms_tex)}}}'


        if all(m.concentration is not None for m in reactants) and all(m.concentration is not None for m in products):
            Q=1
            for r in reactants:
                Q *= r.concentration**(-1*r.coefficient)
            for p in products:
                Q *= p.concentration**(p.coefficient)
        else:
            Q = None

        return Q_eqn, Q_eqn_answers, Q_tex, Q
    
    def _generate_rate_expression(self):
        reactants = [m for m in self.reactants if (str(m) != 'e-' and m.phase is None)]
        
        reactant_terms = [f'[{m}]^{m.coefficient}' if m.coefficient > 1 else f'[{m}]' for m in reactants]

        rate_eqn = 'k'+f'{"".join(reactant_terms)}'

        reactant_perm = list(permutations(reactant_terms))
        
        all_eqn = ['k'+f'{"".join(r)}' for r in reactant_perm]
        rate_eqn_answers=';'.join(all_eqn)

        reactant_terms_tex = [f'[{m.tex}]^{{{m.coefficient}}}' if m.coefficient > 1 else f'[{m.tex}]' for m in reactants]
        rate_eqn_tex = f'k{"".join(reactant_terms_tex)}'


        if all(m.concentration is not None for m in reactants) and self.k is not None:
            rate=self.k
            for r in reactants:
                rate *= r.concentration**(r.coefficient)
        else:
            rate = None

        return rate_eqn, rate_eqn_answers, rate_eqn_tex, rate

    def set_concentration(self, s, conc):
        """
        s is the plaintext representation of the species whose concentration is to be set. e.g. 'SO4--' for sulfate
        conc is the concentration, entered as a number

        this function automatically calls the updater, ensuring that the Q value is calculated once all concentrations are defined
        """
        
        # Search for the molecule in reactants and set the concentration
        for m in self.reactants:
            if str(m) == s:
                m.concentration = conc
                self._update()
                return

        # Search for the molecule in products and set the concentration
        for m in self.products:
            if str(m) == s:
                m.concentration = conc
                self._update()
                return

        # If the molecule was not found in either list, you can optionally raise an error or print a message
        print(f"Molecule {s} not found in reactants or products.")
