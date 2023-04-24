import math
import scipy.stats as stats

from sigfig import sigfig as sf

0
class uncertainvalue:
    def __init__(self, mean, stdev, n=math.inf):
        if stdev <= 0:
            raise TypeError("Expected stdev to be a positive number")
        if n <= 0:
            raise TypeError("Expected n to be a positive number")
        
        self.n = n
        self.stdev = sf(str(stdev),sig_figs=1)
        if self.stdev.scientific_notation().split('e')[0] == '1':
            self.stdev = sf(str(stdev), sig_figs=2)    
        self.mean = sf(str(mean),last_decimal_place=self.stdev.last_decimal_place)
        self.stderr = self.stdev / n**0.5
        if self.stderr.scientific_notation().split('e')[0] == '1':
            self.stderr = sf(str(self.stdev.value/n**0.5), sig_figs=2)

    def answers(self):
        answers = ["{} ± {}".format(self.mean.as_num(),self.stdev.as_num())]
        answers += ["{}±{}".format(self.mean.as_num(),self.stdev.as_num())]
        answers += ["{} ± {}".format(self.mean.scientific_notation(),self.stdev.scientific_notation())]
        answers += ["{}±{}".format(self.mean.scientific_notation(),self.stdev.scientific_notation())]
        answer_string = ';'.join(answers)
        return answer_string
    
    def ci(self,confidence_level=0.95):
        if confidence_level >= 1: #catch '95' as 0.95
            confidence_level /= 100
        elif confidence_level < 0 or confidence_level > 1:
            raise TypeError("Expected a confidence_level value between 0 and 1")
        dof = self.n - 1 if self.n > 1 else 1
        t = stats.t.ppf((1 + confidence_level) / 2, dof)
        ci = sf(str(t*self.stdev.value/(self.n**0.5)),sig_figs=1)
        if ci.scientific_notation().split('e')[0] == '1':
            ci = sf(str(t*self.stdev.value/(self.n**0.5)),sig_figs=2)
        return ci

    def __str__(self):
        if self.mean.value > 1e3 or self.mean.value < 1e-3:
            formatted = "{} ± {}".format(self.mean.scientific_notation(),self.stdev.scientific_notation())
        else:
            formatted = "{} ± {}".format(self.mean.as_num(),self.stdev.as_num())    
        return formatted
    
    def __add__(self, other):
        if isinstance(other, uncertainvalue):
            result_mean = self.mean.value + other.mean.value
            result_stdev = (self.stdev.value**2 + other.stdev.value**2)**0.5
        else:
            result_mean = self.mean.value + other
            result_stdev = self.stdev.value
        return uncertainvalue(result_mean,result_stdev)

    def __sub__(self, other):
        if isinstance(other, uncertainvalue):
            result_mean = self.mean.value - other.mean.value
            result_stdev = (self.stdev.value**2 + other.stdev.value**2)**0.5
        else:
            result_mean = self.mean.value - other
            result_stdev = self.stdev.value
        return uncertainvalue(result_mean,result_stdev)
    
    def __mul__(self, other):
        if isinstance(other, uncertainvalue):
            result_mean = self.mean.value * other.mean.value
            result_stdev = result_mean*((self.stdev.value/self.mean.value)**2 + (other.stdev.value/other.mean.value)**2)**0.5
        else:
            result_mean = self.mean.value * other
            result_stdev = self.stdev.value * other
        return uncertainvalue(result_mean,result_stdev)

    def __truediv__(self, other):
        if isinstance(other, uncertainvalue):
            result_mean = self.mean.value / other.mean.value
            result_stdev = result_mean*((self.stdev.value/self.mean.value)**2 + (other.stdev.value/other.mean.value)**2)**0.5
        else:
            result_mean = self.mean.value / other
            result_stdev = self.stdev.value / other
        return uncertainvalue(result_mean,result_stdev)

    def __pow__(self,other):
        result_mean = self.mean.value ** other 
        result_stdev = result_mean * ((self.stdev.value/self.mean.value) * other)
        return uncertainvalue(result_mean,result_stdev)

    def log(self,base=10):
        result_mean = math.log(self.mean.value,base)
        result_stdev = self.stdev.value / (math.log(base) * self.mean.value)
        return uncertainvalue(result_mean,result_stdev) 

    def ln(self):
        result_mean = math.log(self.mean.value)
        result_stdev = self.stdev.value / self.mean.value
        return uncertainvalue(result_mean,result_stdev)
    
    def exponent(self, base=math.e):
        result_mean = base**self.mean.value
        result_stdev = result_mean * math.log(base) * self.stdev.value
        return uncertainvalue(result_mean,result_stdev)

def main():
    x = uncertainvalue(5,0.2,10)
    
    print("")
    print(x.answers())

if __name__ == "__main__":
    main()