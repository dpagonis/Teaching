from scipy.optimize import brentq

from .molecule import molecule
from .sigfig import sigfig as sf

class weakacid(molecule):
    """
    Represents a weak acid and its various properties.

    Attributes:
        neutral_formula (str): Chemical formula of the weak acid in its neutral form.
        pKa (list): List containing the acid dissociation constant(s).
        n_H (int): Number of acidic protons in the molecule.
        n_H_neutral (int, optional): Number of acidic protons in the neutral molecule. Defaults to `n_H`.
        forms (list): List of `molecule` class instances representing the weak acid's varying degrees of protonation.
        F (float, optional): Formal concentration in mol/L. Default is None.
        alpha (list): List of degree of dissociation values corresponding to each form of the molecule.
        _pH (float, private): The pH of the solution.
        pH (property & setter): Represents the pH of the solution. 
            Setting a new value for pH recalculates the alpha values accordingly. 
            When setting pH, the value is stored with significant figures. 
            Use as:
            acid.pH to retrieve the value
            acid.pH = new_value  # where `acid` is an instance of `weakacid` and `new_value` is the desired pH.

    Methods:
        getforms(): Generates a list of molecule forms based on protonation states.
        calcpH(): Calculates the pH where the charge balance equals zero.
        calcalpha(pH): Calculates the degree of dissociation for each form at a given pH.
        charge_balance(pH): Returns the net charge of the solution at a given pH.

    Usage:
        acid = weakacid()
        If no arguments are provided during instantiation, the program will prompt for necessary inputs.

    Note:
        This class inherits from the `molecule` class.
    """


    def __init__(self, neutral_formula=None, pKa=None, n_H_neutral=None, F=None):
        # Check if neutral_formula is not provided and prompt user
        
        ask_for_inputs=False
        if (not neutral_formula) and (not pKa):
            ask_for_inputs=True
        
        if not neutral_formula:
            neutral_formula = input("Enter the neutral formula: ")

        # Call the parent class (molecule)'s __init__ method first
        super().__init__(neutral_formula)
        self.neutral_formula = neutral_formula

        # Check if pKa is not provided and prompt user
        if not pKa:
            # Note: here we're assuming user will enter a comma-separated list of pKa values
            pKa_values = input("Enter pKa values (comma-separated if multiple): ").split(',')
            pKa = [float(value.strip()) for value in pKa_values]
        else:
            pKa = pKa if type(pKa) is list else [pKa]

        self.pKa = pKa
        self.n_H = len(self.pKa)

        # Check if n_H_neutral is not provided and prompt user
        if n_H_neutral is None and ask_for_inputs:
            n_H_neutral_input = input("Enter number of acidic protons in neutral molecule: ")
            self.n_H_neutral = self.n_H if not n_H_neutral_input else int(n_H_neutral_input)
        else:
            self.n_H_neutral = n_H_neutral

        self.forms = self.getforms()  # list of molecule class instances with varying degrees of protonation

        # Check if F is not provided and prompt user
        if F is None and ask_for_inputs:
            F_input = input("Enter formal concentration F in mol/L (optional, press enter to skip): ")
            self.F = None if not F_input else float(F_input)
        else:
            self.F = F

        self._pH = self.calcpH() if self.F is not None else None
        self.alpha = self.calcalpha(self._pH) if self.F is not None else None

        if ask_for_inputs:
            print('-------------Key Attributes--------------')
            print('forms (list): List of `molecule` class instances representing the weak acid\'s varying degrees of protonation.')
            print('alpha (list): List of degree of dissociation values corresponding to each form of the molecule.')
            print('pH: The pH of the solution.')
            print('-----------------------------------------')

        
    @property
    def pH(self):
        return self._pH
    
    @pH.setter
    def pH(self,new_value):
        self._pH = sf(str(new_value))
        self.alpha = self.calcalpha(self._pH)

    def getforms(self):
        # Start with the neutral form, removing any salt ions
        alkali_metals = ['Na', 'K', 'Li']
        acid_anions = ['Cl', 'Br', 'I']
        formula = self.neutral_formula

        for metal in alkali_metals:
            if metal in formula:
                formula = formula.replace(metal, '')
                formula += '-'
                
        for anion in acid_anions:
            if anion in formula:
                formula = formula.replace(anion, '')
                formula += '+'
        
        base_form = molecule(formula)

        forms = [base_form]  # Begin the list of forms with the base form
        
        # Generate forms by successively removing H+ ions, as many times as n_H_neutral
        form_deprot= base_form
        for _ in range(self.n_H_neutral):
            form_deprot = form_deprot.subtract('H+')
            forms.append(form_deprot)
        
        # Generate forms by successively adding H+ ions, as many times as n_H - n_H_neutral
        form_prot = base_form
        for _ in range(self.n_H - self.n_H_neutral):
            form_prot = form_prot.add('H+')
            forms.append(form_prot)

        # Sort the list based on the charge of each molecule object in forms
        forms.sort(key=lambda f: f.charge)
        forms.reverse()

        return forms

    def calcpH(self):
        # find pH where charge_balance equals zero
        pH = brentq(self.charge_balance, 0, 14)
        return sf(str(pH),last_decimal_place=-2)
    
    def calcalpha(self, pH):
        if isinstance(pH, sf):
            pH=pH.value

        Ka = [10**(-pK) for pK in self.pKa]
        H = 10**(-pH)

        D_terms = []
        prod_Ka = 1

        for i in range(len(Ka) + 1):

            # Try to compute D_term, but handle any OverflowErrors
            try:
                D_term = H**(len(Ka)-i) * prod_Ka
            except OverflowError:
                D_term = 0
            
            if i < len(Ka):
                prod_Ka *= Ka[i]
            D_terms.append(D_term)

        D = sum(D_terms)

        alpha = [D_term / D for D_term in D_terms]
        return alpha

    def charge_balance(self, pH):
        
        H = 10**(-pH)
        alpha = self.calcalpha(pH)

        concs = [a* self.F for a in alpha]
        
        charge = H - 1e-14/H    # H+ and OH-
        
        # For each form of the molecule
        for i, form in enumerate(self.forms):
            # Multiply the charge of the form by the corresponding concentration
            charge += form.charge * concs[i]

        # subtract the charge from alkali metals or add the charge from acid anions
        alkali_metals = ['Na', 'K', 'Li']
        acid_anions = ['Cl', 'Br', 'I']
        n_alkali = 0
        n_anion = 0

        # Count the alkali metals and acid anions
        for element in alkali_metals:
            n_alkali += self.element_dict.get(element, 0)
        for element in acid_anions:
            n_anion += self.element_dict.get(element, 0)

        # Update the charge
        charge += self.F * n_alkali
        charge -= self.F * n_anion  # Subtracting as anions have negative charge
        
        #print(pH,charge)
        if isinstance(charge, sf):
            charge = charge.value
        
        return charge