"""Load dojo timer and extensions"""

from IPython.display import Javascript, display
from pkg_resources import resource_string
from .magics import load_ipython_extension as load_magics


MODULE = __name__


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    display(Javascript(
        resource_string(MODULE, "resources/index.js")
        .decode("utf-8")
        .replace("define([", "define('jupyter_dojo', [")
    ))
    display(Javascript("""
        require(["jupyter_dojo"], function(j){
          j.load_ipython_extension();
        });
    """))
    load_magics(ipython)
