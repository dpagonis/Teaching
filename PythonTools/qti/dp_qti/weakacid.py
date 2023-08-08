from scipy.optimize import brentq

from .molecule import molecule
from .sigfig import sigfig as sf

class weakacid(molecule):
    def __init__(self,neutral_formula,pKa,n_H_neutral=None,F=None):
        # Call the parent class (molecule)'s __init__ method first
        super().__init__(neutral_formula)
        
        self.neutral_formula = neutral_formula
        
        self.pKa = pKa if type(pKa) is list else [pKa]

        self.n_H = len(self.pKa)
        self.n_H_neutral = self.n_H if n_H_neutral is None else n_H_neutral #default is to assume we're starting with a fully protonated weak acid
        self.forms = self.getforms() #list of molecule class instances with varying degrees of protonation
        self.F = F
        self._pH = self.calcpH() if F is not None else None
        self.alpha = self.calcalpha(self._pH) if F is not None else None 
        
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

def main():
    a = weakacid('C9H11NO2',[2.18,9.09],n_H_neutral=1,F=0.2)
    print(a.neutral_formula)
    print(a.pH)


if __name__ == '__main__':
    main()