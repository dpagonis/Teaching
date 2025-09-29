import inspect
import os

from dp_chem import molecule



def fig_dir():
    maindir = main_dir()
    return maindir.replace(".py",".png")

def main_dir():
    # Find the outermost script (__main__)
    for frame in inspect.stack():
        module = inspect.getmodule(frame.frame)
        if module and module.__name__ == "__main__":
            parent_script = module.__file__
            break
    else:
        raise RuntimeError("Could not determine the outermost script (__main__).")

    parent_dir = os.path.dirname(os.path.abspath(parent_script))
    script_name = os.path.basename(parent_script)
    main_path = os.path.join(parent_dir, script_name)
    return main_path

def MW(s):
    if isinstance(s,str):
        m=molecule(s)
    if isinstance(s,molecule):
        m=s
    return f'{m.formula}: {m.molecular_weight.as_num()} g/mol'

def N(T_K,P_mbar):
    mol_m3 = P_mbar*100/(8.3145*T_K)
    molec_cm3 = mol_m3 * 1e-6 * 6.02214076e23
    return molec_cm3
