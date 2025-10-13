import inspect
import os
from dp_chem import molecule
import getpass
from datetime import datetime

def save_fig(fig, fname=None, dpi=200, annotate=True, fontsize=8):
    """
    Save a matplotlib.figure.Figure to disk. If fname is None, a default path
    is produced from main_dir() with a .png extension. Optionally annotate the
    figure with the user, save datetime, and the script that created it.
    """
    import matplotlib.pyplot as _plt

    # determine filename
    if fname is None:
        fname = fig_dir()

    # annotation
    if annotate:
        try:
            user = getpass.getuser()
        except Exception:
            user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"

        try:
            main_path = main_dir()
            script_name = os.path.basename(main_path)
        except Exception:
            script_name = "unknown"

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        annotation = f"{user} | {date_str} | {script_name}"

        # Add annotation in the lower-right corner of the figure
        # Use fig.text so it appears on all subplots and is saved with the figure.
        fig.text(0.99, 0.99, annotation, ha="right", va="top",
                 fontsize=fontsize, alpha=0.5)

    # save
    # Accept either a figure object or the pyplot state
    if hasattr(fig, "savefig"):
        fig.savefig(fname, dpi=dpi, bbox_inches="tight")
    else:
        # assume pyplot
        _plt.savefig(fname, dpi=dpi, bbox_inches="tight")

    return fname

def fig_dir():
    maindir = main_dir()
    return maindir.replace(".py", ".png")

def main_dir():
    # Find the outermost script (__main__)
    for frame in inspect.stack():
        module = inspect.getmodule(frame.frame)
        if module and module.__name__ == "__main__":
            parent_script = getattr(module, "__file__", None)
            if parent_script:
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
