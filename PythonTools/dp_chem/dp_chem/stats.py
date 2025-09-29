from scipy.stats import t, f
import math
import numpy as np

from .uncertainvalue import uncertainvalue

def t_table(confidence, dof):
    """
    Calculate the critical t-value for a given confidence level and degrees of freedom.

    Parameters:
        confidence (float): Confidence level as a decimal (e.g., 0.95) or percentage (e.g., 95).
        dof (int): Degrees of freedom.

    Returns:
        float: Critical t-value.
    """
    # Normalize confidence to a decimal if entered as a percentage
    if confidence > 1:  # Assume percentage if greater than 1
        confidence /= 100.0
    
    # Ensure valid confidence and dof
    if not (0 < confidence < 1):
        raise ValueError("Confidence level must be between 0 and 1 or 0% and 100%.")
    if dof < 1:
        raise ValueError("Degrees of freedom must be a positive integer.")
    
    # Calculate the critical t-value
    alpha = 1 - confidence
    t_critical = t.ppf(1 - alpha / 2, dof)
    
    return t_critical

def f_table(confidence, dof1, dof2):
    """
    Calculate the critical F-value for a given confidence level and degrees of freedom.

    Parameters:
        confidence (float): Confidence level (e.g., 0.95 or 95 for 95% confidence).
        dof1 (int): Degrees of freedom for the numerator.
        dof2 (int): Degrees of freedom for the denominator.

    Returns:
        float: Critical F-value.
    """
    # Normalize confidence to a decimal if entered as a percentage
    if confidence > 1:
        confidence /= 100.0
    
    # Ensure valid input
    if not (0 < confidence < 1):
        raise ValueError("Confidence level must be between 0 and 1 or 0% and 100%.")
    if dof1 < 1 or dof2 < 1:
        raise ValueError("Degrees of freedom must be positive integers.")

    alpha = 1 - confidence
    upper_critical_value = f.ppf(1 - alpha / 2, dof1, dof2)

    return upper_critical_value

def f_test(s1,n1,s2,n2,confidence=95,show=True):
    
    if n1 < 3 or n2 < 3:
        raise ValueError("Insufficient replicates. Need three replicates to test. n1={n1}, n2={n2}")
    
    if math.isinf(n1):
        n1=1e9
    if math.isinf(n2):
        n2=1e9

    if s1 < s2:
        dummy = s2
        s2=s1
        s1 = dummy
        dummy = n2
        n2=n1
        n1=dummy

    if confidence > 1:
        confidence /= 100.0

    H0 = True
    conclude = "Standard deviations ARE NOT different"

    f_calc = (s1**2)/(s2**2)
    f_tab = f_table(confidence,n1-1,n2-1)

    if f_calc > f_tab:
        H0 = False
        conclude = "Standard deviations ARE different"

    if show:
        print("")
        print("-------------F Test-------------")
        print(f"{s1:.02f} (n={n1}) vs {s2:.02f} (n={n2})")
        print(f"Fcalc = {f_calc:.02f}; F_table = {f_tab:.02f}")
        print(f"{'ACCEPT' if H0 else 'REJECT'} null hypothesis")
        print(conclude)
        print("")

    return H0, f_calc, f_tab

    

def t_test(uv1, uv2, confidence=95, show=True, show_Ftest=False):
    
    if not isinstance(uv1,uncertainvalue):
        try:
            a=np.array(uv1)
            uv1=uncertainvalue(a.mean(),a.std(ddof=1),n=len(a))
        except:
            ValueError("Could not turn input 1 of t_test into uncertainvalue")
    
    if not isinstance(uv2,uncertainvalue):
        try:
            a=np.array(uv2)
            uv2=uncertainvalue(a.mean(),a.std(ddof=1),n=len(a))
        except:
            ValueError("Could not turn input 2 of t_test into uncertainvalue")

    if confidence > 1:
            confidence /= 100.0

    H0 = True
    conclude= "Measurements ARE NOT different"

    x1=uv1.mean.value
    s1=uv1.stdev.value
    n1=uv1.n if not math.isinf(uv1.n) else 1e9
    x2 = uv2.mean.value
    s2=uv2.stdev.value
    n2=uv2.n if not math.isinf(uv1.n) else 1e9

    F_H0, _, _ = f_test(s1,n1,s2,n2,confidence=confidence, show=show_Ftest)

    if F_H0:
        case = "2a"
        s_pool = ((s1**2*(n1-1)+s2**2*(n2-1))/(n1+n2-2))**0.5
        t_calc = abs(x1-x2)*(n1*n2/(n1+n2))**0.5/s_pool
        dof = n1+n2-2
    else:
        case="2b"
        u1 = s1/n1**0.5
        u2 = s2/n2**0.5
        t_calc = abs(x1-x2)/(u1**2+u2**2)**0.5
        dof = ((u1**2+u2**2)**2)/((u1**4/(n1-1))+(u2**4/(n2-1)))

    t_tab = t_table(confidence,dof)

    if t_calc > t_tab:
        H0=False
        conclude= "Measurements ARE different"

    if show:
        print("")
        print(f"-------------t Test (Case {case})-------------")
        print(f"{uv1} (n={uv1.n}) vs {uv2} (n={uv2.n})")
        if F_H0:
            print(f's_pooled = {s_pool:.03f}')
        print(f"t_calc = {t_calc:.02f}; t_table = {t_tab:.02f}")
        print(f"{'ACCEPT' if H0 else 'REJECT'} null hypothesis")
        print(conclude)
        print("")

    return H0, t_calc, t_tab

def paired_t_test(l1,l2, confidence=95, show=True):

    try:
        l1=np.array(l1)
        l2=np.array(l2)
    except:
        raise ValueError("Could not turn inputs of pair_t_test into arrays")
    
    if len(l1) != len(l2):
        raise ValueError("Datasets are not the same length")
    
    if confidence > 1:
            confidence /= 100.0

    H0 = True
    conclude = "Methods ARE NOT different"

    d = l1-l2
    d_bar = d.mean()
    s_d = d.std(ddof=1)
    diff=uncertainvalue(d_bar,s_d,len(l1))

    t_calc = abs(d_bar)*len(l1)**0.5/s_d 
    t_tab = t_table(confidence,len(l1)-1)

    if t_calc > t_tab:
        H0 = False
        conclude = "Methods ARE different"

    if show:
        print("")
        print(f"-------------t Test (Case 3)-------------")
        print(f"{l1} vs {l2}")
        print(f"differences: {diff}; {s_d}")
        print(f"t_calc = {t_calc:.02f}; t_table = {t_tab:.02f}")
        print(f"{'ACCEPT' if H0 else 'REJECT'} null hypothesis")
        print(conclude)
        print("")

def stats():
    """
    Simple interactive console to choose tests or lookup table values.
    Options:
        1 - two-sample t-test (independent)
        2 - paired t-test
        3 - F test (compare variances)
        4 - lookup t-table value
        5 - lookup F-table value
        q - quit
    For samples you may enter raw data (comma-separated numbers) or summary stats (mean, stdev, n).
    """

    def _read_raw(prompt):
        s = input(prompt).strip()
        try:
            return [float(x) for x in s.split(',') if x.strip() != '']
        except Exception:
            raise ValueError("Could not parse raw data; provide comma-separated numbers.")

    def _read_summary(prompt_prefix):
        try:
            mean = float(input(f"{prompt_prefix} mean: ").strip())
            stdev = float(input(f"{prompt_prefix} stdev: ").strip())
            n = int(float(input(f"{prompt_prefix} n (integer): ").strip()))
            return uncertainvalue(mean, stdev, n)
        except Exception:
            raise ValueError("Could not parse summary stats. Provide numeric mean, stdev and integer n.")

    def _read_sample(name):
        """
        Prompt for either a single mean (then ask stdev and n) or a comma-separated raw list.
        Returns either a Python list of floats (raw data) or an uncertainvalue instance (summary).
        """
        s = input(f"Enter {name} mean OR a comma-separated list of raw values: ").strip()
        if s == '':
            raise ValueError("No input provided for sample")

        # Treat as raw list if there's a comma
        if ',' in s:
            try:
                vals = [float(x) for x in s.split(',') if x.strip() != '']
                if len(vals) == 0:
                    raise ValueError("No numeric values found in raw list")
                return vals
            except Exception:
                raise ValueError("Could not parse raw data; provide comma-separated numbers.")
        # Otherwise treat as a single mean and ask for stdev and n
        else:
            try:
                mean = float(s)
            except Exception:
                raise ValueError("Could not parse mean; provide a numeric value or a comma-separated list.")

            try:
                stdev = float(input(f"{name} stdev: ").strip())
                n = int(float(input(f"{name} n (integer): ").strip()))
                return uncertainvalue(mean, stdev, n)
            except Exception:
                raise ValueError("Could not parse summary stats. Provide numeric stdev and integer n.")

    def _read_confidence():
        s = input("Confidence (default 95): ").strip()
        if s == '':
            return 95
        return float(s)
    
    def _hold():
        # show ellipses and wait for user to press Enter
        print("...", end="", flush=True)
        try:
            input(" Press Enter to continue...")
        except (KeyboardInterrupt, EOFError):
            pass

    while True:
        print("\nAvailable options:")
        print("  1) two-sample t-test (independent)")
        print("  2) paired t-test")
        print("  3) F test (compare variances)")
        print("  4) lookup t-table value")
        print("  5) lookup F-table value")
        print("  q) quit")
        choice = input("Choose an option: ").strip().lower()

        try:
            if choice == '1':
                a = _read_sample("sample 1")
                b = _read_sample("sample 2")
                conf = _read_confidence()
                # call t_test; it accepts lists or uncertainvalue
                H0, t_calc, t_tab = t_test(a, b, confidence=conf, show=True, show_Ftest=True)
                _hold()

            elif choice == '2':
                print("Paired t-test requires two equal-length raw datasets.")
                x = _read_raw("Enter first list (comma-separated): ")
                y = _read_raw("Enter second list (comma-separated): ")
                conf = _read_confidence()
                H0, t_calc, t_tab = paired_t_test(x, y, confidence=conf, show=True)
                _hold()
                

            elif choice == '3':
                print("F test compares two sample standard deviations.")
                # For F test we need s (stdev) and n for each sample
                def _get_s_n(which):
                    typ = input(f"Provide {which} as 'raw' or 'summary' [raw/summary]: ").strip().lower()
                    if typ.startswith('r'):
                        data = _read_raw(f"Enter {which} values (comma-separated): ")
                        arr = np.array(data)
                        s = arr.std(ddof=1)
                        n = len(arr)
                        return s, n
                    else:
                        stdev = float(input(f"{which} stdev: ").strip())
                        n = int(float(input(f"{which} n (integer): ").strip()))
                        return stdev, n

                s1, n1 = _get_s_n("sample 1")
                s2, n2 = _get_s_n("sample 2")
                conf = _read_confidence()
                H0, f_calc, f_tab = f_test(s1, n1, s2, n2, confidence=conf, show=True)
                _hold()

            elif choice == '4':
                conf = _read_confidence()
                dof = int(float(input("Degrees of freedom (integer): ").strip()))
                val = t_table(conf, dof)
                print(f"t-table (confidence={conf}, dof={dof}) = {val : .04f}")
                _hold()

            elif choice == '5':
                conf = _read_confidence()
                dof1 = int(float(input("Degrees of freedom numerator (dof1): ").strip()))
                dof2 = int(float(input("Degrees of freedom denominator (dof2): ").strip()))
                val = f_table(conf, dof1, dof2)
                print(f"F-table (confidence={conf}, dof1={dof1}, dof2={dof2}) = {val : .04f}")
                _hold()

            elif choice == 'q' or choice == 'quit' or choice == 'exit':
                print("Exiting interactive tests.")
                break

            else:
                print("Unknown option. Choose 1-5 or q to quit.")

        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")