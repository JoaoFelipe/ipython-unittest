"""Load dojotools and extensions"""

import os
import sys
from fnmatch import fnmatch
from IPython.display import Javascript, display
from pkg_resources import resource_string
from time import ctime
# ToDo

MODULE = __name__


class Monitor:

    def __init__(self):
        self.run_args = None
        self.patterns = self._get_patterns()
        self.directory = "."


    def register(self, magic, line, cell):
        self.run_args = (magic, line, cell)

    def _get_patterns(self, patterns_file=None):
        """Get patterns list without notebook and patterns file"""
        patterns = []
        if patterns_file is not None:
            try:
                with open(patterns_file, "r") as pat:
                    patterns = [pattern.strip() for pattern in pat.readlines()]
            except IOError:
                print("Could not find {}. Patterns will not be ignored".format(
                    patterns_file
                ))
            patterns.append(os.path.basename(patterns_file))

        display(Javascript("""
            var kernel = IPython.notebook.kernel;
            var thename = window.document.getElementById("notebook_name").innerHTML;
            var command = "_the_notebook = " + "'" + thename + "'";
            kernel.execute(command);
        """))
        patterns.append(get_ipython().user_ns["_the_notebook"])
        return patterns

    def _filter_files(self, files):
        """Filter files according to patterns"""
        for pattern in self.patterns:
            files = [name for name in files if not fnmatch(name, pattern)]
        return files

    def git_commit_all(self):
        """Commit all files when using git"""
        ipython = get_ipython()
        ipython.system("cd {} && git add . && git commit -m {}".format(
            self.directory, ctime()
        ))
        if ipython.user_ns["_exit_code"] == 128:
            raise OSError("Impossible to commit. Make sure git is installed")

    def run_command(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        stdout = StringIO()
        stderr = StringIO()

        if self.run_args is None:
            return
        ipython = get_ipython()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = ipython.run_cell_magic(*self.run_args)

        sys.stdout.close()

    def notify(self, status, msg, error):
        content = (msg + "\n" + error)
        display(Javascript("""
            notify.requestPermission();
            notify.config({pageVisibility: false});
            notify.createNotification("%s", {body:"%s", icon:"%s"});
        """ % (
            ["Failed", "Passed"][int(status)],
            content.replace("\n", "\\n"),
            ["fail.ico", "pass.ico"][int(status)],
        )))
        print(content)

def load_ipython_extension(ipython):
    from .dojo import load_ipython_extension as load_dojo
    display(Javascript(
        resource_string(MODULE, "resources/desktop-notify-min.js")
        .decode("utf-8")
    ))
    display(Javascript("""
        notify.requestPermission();
    """))
    load_dojo(ipython)
