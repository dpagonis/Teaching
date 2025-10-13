import os
import inspect

def save(fig):
    # Find the outermost script (__main__)
    for frame in inspect.stack():
        module = inspect.getmodule(frame.frame)
        if module and module.__name__ == "__main__":
            parent_script = module.__file__
            break
    else:
        raise RuntimeError("Could not determine the outermost script (__main__).")

    # Construct the figure path
    parent_dir = os.path.dirname(os.path.abspath(parent_script))
    script_name = os.path.basename(parent_script)
    fig_name = script_name.replace('.py', '.png')
    fig_path = os.path.join(parent_dir, fig_name)

    # Save the figure
    fig.savefig(fig_path)
    print(f"Figure saved to: {fig_path}")
    return