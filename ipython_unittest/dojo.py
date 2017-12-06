"""Load dojo timer and extensions"""

from IPython.display import Javascript, display
from pkg_resources import resource_string
from .magics import load_ipython_extension as load_magics


MODULE = __name__


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    print("This Extension were removed!")
    print("Please install the jupyter_dojo nbextension/labextension:")
    print("  https://github.com/JoaoFelipe/jupyter-dojo")
    print("And use only the top extension")
    print("  %load_ext ipython_unittest")


    load_magics(ipython)
