import math
import random
import warnings
from decimal import Decimal, ROUND_HALF_UP

from units import units as units_class

class sigfig:

  def __init__(self, value, sig_figs=None, last_decimal_place=None, units_str=""):
    
    if not isinstance(value, str):
      raise TypeError("value input must be a string")  
    
    if not isinstance(units_str, str):
      raise TypeError("Units input must be a string")  

    self.value_str = value
    self.value = float(self.value_str)

    if sig_figs is not None and last_decimal_place is not None:
        raise ValueError("Cannot set both sig_figs and last_decimal_place.")
    
    self.units = units_class(units_str)

    if sig_figs is None and last_decimal_place is None:
        self.sig_figs = self._find_first_decimal_place(self.value_str)-self._find_last_decimal_place(self.value_str) +1
        self.last_decimal_place = self._find_last_decimal_place(self.value_str)
    elif sig_figs is not None:
        self.sig_figs = sig_figs
        self.last_decimal_place = self._find_first_decimal_place(self.value_str)-self.sig_figs +1
    else:
        self.last_decimal_place = last_decimal_place
        self.sig_figs = self._find_first_decimal_place(self.value_str) - self.last_decimal_place +1
   
  def scientific_notation(self):
    prec = self.sig_figs if self._check_rounded_exponent_increase(self.sig_figs-1) else self.sig_figs-1
    prec = 0 if prec < 0 else prec
    rounded_value = self._round_to_decimal_place()
    formatted = format(rounded_value, ".{}e".format(prec))
    split_s = formatted.split('e')
    exponent = int(split_s[1])
    if exponent < 0:
        new_exp = split_s[1].lstrip('-')
        new_exp = new_exp.lstrip('0')
        new_exp = '-' + new_exp
    elif exponent == 0:
        new_exp = '0'
    else:
        new_exp = split_s[1].strip('+')
        new_exp = new_exp.lstrip('0')
    split_s[1] = new_exp
    formatted = 'e'.join(split_s)
    return formatted
  
  def as_num(self):
    # return the value in scientific notation if it's out of the range 1e-6 to 1e6
    if abs(self.value) > 1e6 or abs(self.value) < 1e-6:
        return self.scientific_notation()
    
    #return the value as a floating point number with the correct sig figs, if possible
    if self.last_decimal_place >= 0:
      #if it's not a decimal, we need to handle the weird cases like 10. or 100 with 2 sig figs 
      if self._last_sf_is_zero():
        if self.last_decimal_place == 0:
          formatted = str(int(self._round_to_decimal_place())) + '.'
        else:
          formatted = self.scientific_notation()
      else:
        formatted = str(int(self._round_to_decimal_place()))
    #if it's a decimal do the easy formatting
    else:
      formatted = "{:.{}f}".format(self._round_to_decimal_place(), -1 * self.last_decimal_place)
    return formatted

  def answers(self, sf_tolerance=0):
    def _generate_answers(sf_value):
      sf_instance = sigfig(self.value_str, sig_figs=sf_value)
      answers = [
        sf_instance.as_num(),
        sf_instance.scientific_notation(),
        # sf_instance.scientific_notation().replace('e', ' e'),
        # sf_instance.scientific_notation().replace('e', 'e '),
        # sf_instance.scientific_notation().replace('e', ' e '),
        sf_instance.scientific_notation().replace('e', 'E'),
        # sf_instance.scientific_notation().replace('e', ' E'),
        # sf_instance.scientific_notation().replace('e', 'E '),
        # sf_instance.scientific_notation().replace('e', ' E ')
      ]
      if sf_instance.last_decimal_place == 0:
        answers += [sf_instance.as_num() + '.']
      
      # If the number is less than 1 and not 0, add the version without leading zero
      if abs(sf_instance.value) < 1 and sf_instance.value != 0:
        as_num_str = sf_instance.as_num()
        if '.' in as_num_str:
          no_lead_zero_str = '.'+as_num_str.split('.')[1]
          answers += [no_lead_zero_str]
  
      # # Add leading/trailing spaces for all answers
      # answers_with_leading_space = [' ' + ans for ans in answers]
      # answers_with_trailing_space = [ans + ' ' for ans in answers]

      # Combine both lists and join them with semicolons
      all_answers = answers# + answers_with_leading_space + answers_with_trailing_space
      return all_answers

    # Call _generate_answers for the current number of significant figures and for the numbers within the range specified by sf_tolerance
    final_answers = []
    
    # Process native sigfigs first
    final_answers.extend(_generate_answers(self.sig_figs))

    # Process the remaining values
    for sf_adjust in list(range(-sf_tolerance, 0)) + list(range(1, sf_tolerance + 1)):
      adjusted_sf = self.sig_figs + sf_adjust
      if adjusted_sf >= 1:
          final_answers.extend(_generate_answers(adjusted_sf))

    # Combine the generated answers and return the final answer string
    answer_string = ';'.join(final_answers)
    return answer_string

  def convert_to(self, output_unit_str):
    factor = self.units.convert_to(output_unit_str) 
    if factor is None:
      warnings.simplefilter("default")
      warnings.warn("Unit conversion of sigfig object failed. Conversion did not occur.")
      return self
    else:
      output_sf = self * factor
      return output_sf

  @staticmethod
  def random_value(value_range=(1e-3, 1000), sf_range=(1, 5), value_log=False):
    min_value, max_value = value_range
    min_sig_figs, max_sig_figs = sf_range
    
    if value_log:
      log_min_value = math.log(min_value) if min_value > 0 else 0
      log_max_value = math.log(max_value)
      log_value = random.uniform(log_min_value, log_max_value)
      value = math.exp(log_value)
    else:
      value = random.uniform(min_value, max_value)
  
    sig_figs = random.randint(min_sig_figs, max_sig_figs)
    
    value_str = "{:.{}e}".format(value, sig_figs - 1)
    return sigfig(value_str, sig_figs=sig_figs)

  def _round_to_decimal_place(self):
    factor = 10 ** self.last_decimal_place
    num_to_round = Decimal(self.value/factor)
    rounded_number = num_to_round.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return rounded_number * Decimal(factor)
  
  def _find_last_decimal_place(self, value_str):
    number_str = value_str
    if 'e' in value_str:
        exponent = int(number_str.split('e')[1])
        number_str = number_str.split('e')[0]
    
    if '.' in number_str:
        decimal_place = -1*len(number_str.split('.')[1])
    else:
        decimal_place = len(number_str)-len(number_str.rstrip('0'))
        
    if 'e' in value_str:
        return exponent + decimal_place
    else:
        return decimal_place
  
  def _find_first_decimal_place(self, number_str):
    #cases are 
    #sci notation (split out number from exponent, do recursion)
    #normal with decimal point greater than 1
    #normal with decimal point less than 1
    #normal without decimal point
    
    if 'e' in number_str:  # in sci not.
      exponent = int(number_str.split('e')[1])
      number_str = number_str.split('e')[0]
      decimal_place = self._find_first_decimal_place(number_str)+exponent

    else: #not sci not.
      if '.' in number_str:
        if abs(float(number_str)) < 1:
          number_str = number_str.split('.')[1]
          count = 0
          for c in number_str:
              if c == '0':
                  count += 1
              else:
                  break
          decimal_place = -(count+1)
        else:
          number_str = number_str.split('.')[0]
          decimal_place = len(number_str.strip('-').lstrip('0'))-1
      else:
        decimal_place = len(number_str.strip('-').lstrip('0'))-1
          
    return decimal_place 
  
  def _check_rounded_exponent_increase(self, dplaces):
    # Convert the original number to a string in scientific notation
    num = self.value
    dplaces = 0 if dplaces < 0 else dplaces
    rounded_sci_notation = format(num, f".{dplaces}e")
    rounded_exponent = int(rounded_sci_notation.split("e")[-1])
    # Round the number and convert it to a string in scientific notation
    original_sci_notation = format(num, f".{15}e")
    original_exponent = int(original_sci_notation.split("e")[-1])
    # Compare the exponents and return True if the exponent has increased, False otherwise
    return rounded_exponent > original_exponent
  
  def _last_sf_is_zero(self):
    return int(self._round_to_decimal_place()) % 10 ** (self.last_decimal_place+1) == 0

  def __str__(self):
    #if small or large use sci not
    if abs(self.value) < 1e-3 or abs(self.value) >= 1e4:     
      formatted = self.scientific_notation()
    else:        
      if self.last_decimal_place >= 0:
        #if it's not a decimal, we need to handle the weird cases like 10. or 100 with 2 sig figs 
        if self._last_sf_is_zero():
          if self.last_decimal_place == 0:
            formatted = str(int(self._round_to_decimal_place()))+'.'
          else:
            formatted = self.scientific_notation()
        else:
          formatted = str(int(self._round_to_decimal_place()))
      #if it's a decimal do the easy formatting
      else:
        formatted = "{:.{}f}".format(self.value, -1*self.last_decimal_place)
    return formatted
  
  def __add__(self, other):
    if isinstance(other, sigfig):
      result = self.value + other.value
      return sigfig(str(result), last_decimal_place=max(self.last_decimal_place, other.last_decimal_place))
    else:
      result = self.value + other
      return sigfig(str(result),last_decimal_place=self.last_decimal_place)

  def __sub__(self, other):
    if isinstance(other, sigfig):
      result = self.value - other.value
      return sigfig(str(result), last_decimal_place=max(self.last_decimal_place, other.last_decimal_place))
    else:
      result = self.value - other
      return sigfig(str(result),last_decimal_place=self.last_decimal_place)
  
  def __radd__(self, other):
    # Assuming other is a float
    result = other + self.value
    return sigfig(str(result),last_decimal_place=self.last_decimal_place)

  def __rsub__(self, other):
    # Assuming other is a float
    result = other - self.value
    return sigfig(str(result),last_decimal_place=self.last_decimal_place)
  
  def __mul__(self, other):
    if isinstance(other, sigfig):
      result = self.value * other.value
      return sigfig(str(result), sig_figs=min(self.sig_figs, other.sig_figs))
    else:
      result = self.value * other
      return sigfig(str(result),sig_figs=self.sig_figs)
    
  def __rmul__(self, other):
    # Assuming other is a basic numeric type
    result = other * self.value
    return sigfig(str(result), sig_figs=self.sig_figs)

  def __truediv__(self, other):
    if isinstance(other, sigfig):
      result = self.value / other.value
      return sigfig(str(result), sig_figs=min(self.sig_figs, other.sig_figs))
    else:
      result = self.value / other
      return sigfig(str(result),sig_figs=self.sig_figs)
    
  def __rtruediv__(self, other):
    # Assuming other is a basic numeric type
    result = other / self.value
    return sigfig(str(result), sig_figs=self.sig_figs)
    
  def __pow__(self, other):
    if isinstance(other, sigfig):
      result = self.value ** other.value
      increment_other_sf = other.sig_figs if other.sig_figs > 1 else 1
      return sigfig(str(result), sig_figs=min(self.sig_figs,increment_other_sf))
    else:
      result = self.value ** other
      return sigfig(str(result), sig_figs=self.sig_figs)

  def log(self, base=10):
    result_sig_figs = self.sig_figs + 1 
    return sigfig(str(math.log(self.value, base)),sig_figs=result_sig_figs)

  def ln(self):
    return sigfig(str(math.log(self.value)),last_decimal_place=-1*self.sig_figs)

  def exponent(self, base=math.e):
    result_sig_figs = self.sig_figs - 1 if self.sig_figs > 1 else 1
    return sigfig(str(base**self.value),sig_figs=result_sig_figs)
