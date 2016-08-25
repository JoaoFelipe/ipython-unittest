
from .magics import load_ipython_extension

def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="resources",
        dest="jupyter_dojo",
        require="jupyter_dojo/index"
    )]