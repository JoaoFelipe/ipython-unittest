# coding: utf-8
"""
`%%unittest`, `%%unittest_testcase`, `%%unittest_main` magics for IPython
===========================================

This extension provides three cell magics.

First magic is `%%unittest_main`. This magic runs testcases defined in a cell

    %%unittest_main
    class MyTest(unittest.TestCase):
        def test_1_plus_1_equals_2(self):
            sum = 1 + 1
            self.assertEqual(sum, 2)

Second magic is `%%unittest_testcase`. This magic creates a testcase with
functions defined in the cell and execute it.

    %%unittest_testcase
    def test_1_plus_1_equals_2(self):
        sum = 1 + 1
        self.assertEqual(sum, 2)

Third magic is `%%unittest`. This magic converts Python assert into
unittest functions.

    %%unittest
    "1 plus 1 equals 2"
    sum = 1 + 1
    assert sum == 2

By default, docstring in this magic will separate unittest methods.
However, if docstrings are not provided, the magic will create a method for
for each assert.


These magics support optional arguments:

    -d (--dojo):       add timer and change timer color to indicate whether or
                       not the tests have passed
    -c (--color):      change logo color to indicate whether or not the tests
                       have passed
    -p (--previous) P: set cursor to P cells before (default: -1 = next cell)
    -s (--stream) S:   set test output stream (default: 'sys.stdout')
    -t (--testcase) T: define TestCase name.
                       Valid for '%%unittest' and '%%unittest_testcase'
    -u (--unparse):    print cell source code after transformations.
                       Valid for '%%unittest' and '%%unittest_testcase'

License for ipython-unittest
----------------------------------

The MIT License (MIT)

Copyright (c) 2016 João Felipe Nicolaci Pimentel (joaofelipenp@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import ast
import sys
import unittest
import re
import subprocess

from copy import copy
from collections import OrderedDict
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.display import display


MODULE = __name__


def create_module(body, node):
    """Create AST Module"""
    kwargs = {}
    if sys.version_info >= (3, 8):
        kwargs['type_ignores'] = node.type_ignores

    return ast.copy_location(ast.Module(body, **kwargs), node)


def maybe(obj, name, default=None):
    """Return atributte if it exists or default"""
    if hasattr(obj, name):
        return getattr(obj, name)
    return default


def class_def(name, bases, body, decorators, keywords=None):
    """Create ClassDef Node on both python 2 and 3"""
    keywords = keywords or []
    constructor = [name, bases]
    if sys.version_info > (3, 0):
        constructor.append(keywords)
    constructor.append(body)
    constructor.append(decorators)
    return ast.ClassDef(*constructor)


def param(value, annotation=None):
    """Create function definition param"""
    if sys.version_info > (3, 0):
        return ast.arg(value, annotation)
    return ast.Name(value, ast.Param())


def function_def(name, args, body, decs, returns=None):
    """Create FunctionDef Node on both python 2 and 3"""
    constructor = [name, args, body, decs]
    if sys.version_info > (3, 0):
        constructor.append(returns)

    return ast.FunctionDef(*constructor)


def arguments(args, vararg, kwarg, default, kwonlyargs=None, kw_defaults=None, posonlyargs=None):
    """Create arguments Node on both python 2 and 3"""
    # pylint: disable=too-many-arguments
    kwonlyargs = kwonlyargs or []
    kw_defaults = kw_defaults or []

    constructor = []
    if sys.version_info >= (3, 8):
        constructor.append(posonlyargs or [])
    constructor.append(args or [])
    constructor.append(vararg)
    if sys.version_info > (3, 0):
        constructor.append(kwonlyargs or [])
        constructor.append(kw_defaults or [])
    constructor.append(kwarg)
    constructor.append(default or [])
    return ast.arguments(*constructor)


def call(func, args, keywords=None, star=None, kwargs=None):
    """Create call with args, keywords, star args and kwargs"""
    keywords = keywords or []
    create_call = [func, args, keywords]
    if sys.version_info < (3, 5):
        create_call += [star, kwargs]
    return ast.Call(*create_call)


class TransformFunction(ast.NodeTransformer):
    """Create test cases with all outer level functions

    In [1]: %%unittest_assert
       ...: def test_1_plus_1_equals_2(self):
       ...:     self.assertEqual(1 + 1, 2)

    Become: class JupyterTestCase(unittest.TestCase):
       ...:     def test_1_plus_1_equals_2(self):
       ...:         self.assertEqual(1 + 1, 2)


    In [2]: %%unittest_assert
       ...: 'True is True'
       ...: assert True
       ...: '1 plus 1 equals 2'
       ...: assert 1 + 1 == 2

    Become: def test_True_is_True(self):
       ...:     self.assertTrue(True)
       ...: def test_1_plus_1_equals_2(self):
       ...:     self.assertEqual(1 + 1, 2)
    """
    def __init__(self, testcase_name):
        self.testcase_name = testcase_name

    def visit_Module(self, node):                                                # pylint: disable=invalid-name
        """Visit module. Create TestCase with outerlevel functions"""
        body, functions = [], []
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                functions.append(stmt)
            else:
                body.append(self.visit(stmt))

        if functions:
            body.append(ast.fix_missing_locations(class_def(
                self.testcase_name,
                [ast.Attribute(ast.Name('unittest', ast.Load()),
                               'TestCase', ast.Load())],
                functions, []
            )))

        return create_module(body, node)


class TransformAssert(ast.NodeTransformer):
    """Create tests for each assert

    In [1]: %%unittest_assert
       ...: assert True
       ...: assert 1 + 1 == 2

    Become: def test_1(self):
       ...:     self.assertTrue(True)
       ...: def test_2(self):
       ...:     self.assertEqual(1 + 1, 2)


    In [2]: %%unittest_assert
       ...: 'True is True'
       ...: assert True
       ...: '1 plus 1 equals 2'
       ...: assert 1 + 1 == 2

    Become: def test_True_is_True(self):
       ...:     self.assertTrue(True)
       ...: def test_1_plus_1_equals_2(self):
       ...:     self.assertEqual(1 + 1, 2)
    """

    def visit_Module(self, node):                                                # pylint: disable=invalid-name
        """Visit Module.
        Find isolated Str to separate functions.
        If there is no Str, use Asserts to separate functions
        """

        starts = [i for i, stmt in enumerate(node.body)
                  if isinstance(stmt, ast.Expr)
                  and isinstance(stmt.value, ast.Str)]
        if not starts:
            starts = [i + 1 for i, stmt in enumerate(node.body)
                      if isinstance(stmt, ast.Assert)]
        if not starts:
            return node

        if not starts[0]:
            starts.pop(0)
        starts.append(len(node.body))
        body, function_body, pos, name = [], [], 0, ''

        for i, stmt in zip_longest(range(len(node.body) + 1), node.body):
            if i == starts[pos]:
                name = "test_{}".format(name if name else pos + 1)
                body.append(ast.fix_missing_locations(function_def(
                    name, arguments([param('self')], None, None, []), function_body, []
                )))
                function_body, pos, name = [], pos + 1, ''
            if stmt:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str):
                    name = re.sub('[^A-Za-z0-9]+', '_', stmt.value.s.strip())
                visit_stmt = self.visit(stmt)

                if visit_stmt:
                    function_body.append(visit_stmt)

        return create_module(body, node)

    def visit_Assert(self, node):                                                # pylint: disable=invalid-name, no-self-use
        """Visit Assert
        Convert BinOp asserts into unittest's assert equals
        """
        args = [node.test]
        assertion = 'assertTrue'
        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1:
            args = [node.test.left, node.test.comparators[0]]
            assertion = {
                ast.Eq: 'assertEqual',
                ast.NotEq: 'assertNotEqual',
                ast.Lt: 'assertLess',
                ast.LtE: 'assertLessEqual',
                ast.Gt: 'assertGreater',
                ast.GtE: 'assertGreaterEqual',
                ast.Is: 'assertIs',
                ast.IsNot: 'assertIsNot',
                ast.In: 'assertIn',
                ast.NotIn: 'assertNotIn',
            }[node.test.ops[0].__class__]
        if node.msg:
            args.append(node.msg)
        return ast.copy_location(ast.Expr(ast.copy_location(call(
            ast.copy_location(ast.Attribute(
                ast.Name('self', ast.Load()),
                assertion, ast.Load()
            ), node),
            args
        ), node)), node)


class Status:
    """Represent a Test Result"""
    # pylint: disable=too-few-public-methods

    def __init__(self, color, message="", previous=-1):
        self.color = color
        self.message = message
        self.previous = previous

    def _ipython_display_(self):
        bundle = OrderedDict([
            ('application/unittest.status+json', {
                'color': self.color,
                'message': self.message,
                'previous': - (self.previous + 1)
            }),
            ('text/plain', "")
        ])
        if self.color == "salmon":
            bundle['text/plain'] = "Fail"
        elif self.color == "lightgreen":
            bundle['text/plain'] = "Success"

        display(bundle, raw=True)


@magics_class
class IPythonUnittest(Magics):
    """Define unittest magics"""

    def run_tests(self, ipython, args, tree):
        """Execute tests for compiled code"""
        # pylint: disable=no-self-use
        # pylint: disable=bare-except
        # pylint: disable=W0122
        # pylint: disable=W0123

        display(Status("yellow"))

        if not 'unittest' in ipython.user_ns:
            ipython.user_ns['unittest'] = unittest
        if not 'sys' in ipython.user_ns:
            ipython.user_ns['sys'] = sys

        if hasattr(args, 'unparse') and args.unparse:
            import astor
            print(astor.to_source(tree))
        try:
            if hasattr(args, 'stream'):
                stream = eval(
                    args.stream, ipython.user_global_ns, ipython.user_ns
                )
        except:
            stream = sys.stdout
        compiled = compile(tree, 'Cell Tests', 'exec')
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        original_ns = copy(ipython.user_ns)

        exec(compiled, ipython.user_global_ns, ipython.user_ns)
        for key, value in copy(ipython.user_ns).items():
            if ((key not in original_ns or original_ns[key] is not value)
                    and (isinstance(value, type))
                    and (issubclass(value, unittest.TestCase))):
                suite.addTests(loader.loadTestsFromTestCase(value))

        sio = StringIO()
        runner = unittest.TextTestRunner(verbosity=1, stream=sio).run(suite)
        text = sio.getvalue()
        display(Status(
            "lightgreen" if runner.wasSuccessful() else "salmon",
            message=text,
            previous=args.previous
        ))
        stream.write(text)
        return runner

    @magic_arguments()
    @argument(
        '-p', '--previous', default=-1, type=int,
        help="set cursor to P cells before"
    )
    @argument(
        '-s', '--stream', default='sys.stdout',
        help="set output stream"
    )
    @cell_magic
    def unittest_main(self, line, cell):
        """Run defined TestCases

        Parameters
            -p (--previous) P: Set cursor to P cells before
            -s (--stream) S: Set output stream (default: sys.stdout)

        In [1]: %%unittest_main
           ...: class JupyterTestCase(unittest.TestCase):
           ...:     def test_sum(self):
           ...:         self.assertEqual(1 + 1, 2)
        Out[1]: <unittest.runner.TextTestResult run=1 errors=0 failures=0>
        """
        args = parse_argstring(self.unittest_main, line)
        tree = ast.parse(cell)
        return self.run_tests(get_ipython(), args, tree)

    @magic_arguments()
    @argument(
        '-p', '--previous', default=-1, type=int,
        help="set cursor to P cells before"
    )
    @argument(
        '-s', '--stream', default='sys.stdout',
        help="set output stream"
    )
    @argument(
        '-t', '--testcase', default='JupyterTest', type=str,
        help="define TestCase name"
    )
    @argument(
        '-u', '--unparse', action='store_true',
        help="print cell source code"
    )
    @cell_magic
    def unittest_testcase(self, line, cell):
        """Create test case from functions

        Parameters
            -p (--previous) P: Set cursor to P cells before
            -s (--stream) S: Set output stream (default: sys.stdout)
            -t (--testcase): Define TestCase name (default: JupyterTest)
            -u (--unparse): Show TestCase source code

        In [1]: %%unittest_testcase -t JupyterTestCase
           ...: def test_sum(self):
           ...:     self.assertEqual(1 + 1, 2)
        Out[1]: <unittest.runner.TextTestResult run=1 errors=0 failures=0>
        """
        args = parse_argstring(self.unittest_testcase, line)
        tree = ast.parse(cell)
        tree = TransformFunction(args.testcase).visit(tree)
        return self.run_tests(get_ipython(), args, tree)

    @magic_arguments()
    @argument(
        '-p', '--previous', default=-1, type=int,
        help="set cursor to P cells before"
    )
    @argument(
        '-s', '--stream', default='sys.stdout',
        help="set output stream"
    )
    @argument(
        '-t', '--testcase', default='JupyterTest', type=str,
        help="define TestCase name"
    )
    @argument(
        '-u', '--unparse', action='store_true',
        help="print cell source code"
    )
    @cell_magic
    def unittest(self, line, cell):
        """Create test case from functions

        Parameters
            -p (--previous) P: Set cursor to P cells before
            -s (--stream) S: Set output stream (default: sys.stdout)
            -t (--testcase): Define TestCase name (default: JupyterTest)
            -u (--unparse): Show TestCase source code

        In [1]: %%unittest -t JupyterTestCase
           ...: assert 1 + 1 == 2
           ...: 'other test'
           ...: assert 1 + 1 != 3
        Out[1]: <unittest.runner.TextTestResult run=2 errors=0 failures=0>
        """
        args = parse_argstring(self.unittest, line)
        tree = ast.parse(cell)
        tree = TransformAssert().visit(tree)
        tree = TransformFunction(args.testcase).visit(tree)
        return self.run_tests(get_ipython(), args, tree)

    @magic_arguments()
    @argument(
        '-p', '--previous', default=-1, type=int,
        help="set cursor to P cells before"
    )
    @cell_magic
    def external(self, line, cell):
        """Run external tests

        Parameters
            -p (--previous) P: Set cursor to P cells before

        In [1]: %%external
           ...: rspec fizzbuzz_spec.rb
        """
        args = parse_argstring(self.external, line)
        display(Status("yellow"))
        fail = False
        output = b""
        for command in cell.split("\n"):
            if command:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                output += process.stdout.read()
                output += process.stderr.read()
                status = process.wait()
                fail = fail or status
        display(Status(
            "lightgreen" if not fail else "salmon",
            message=output,
            previous=args.previous
        ))
        return not fail


    @magic_arguments()
    @argument(
        '-a', '--append', action='store_true', default=False,
        help='Append contents of the cell to an existing file. '
             'The file will be created if it does not exist.'
    )
    @argument(
        'mode', type=str,
        help='CodeMirror Mode for syntax highlighting'
    )
    @argument(
        'filename', type=str,
        help='file to write'
    )
    @cell_magic
    def write(self, line, cell):
        """Write the contents of the cell to a file.

          The file will be overwritten unless the -a (--append) flag is specified.
          Applies syntax highlighting after first execution
        """
        new_line = " ".join(line.split(" ")[1:])
        return self.shell.run_cell_magic("writefile", new_line, cell)


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(IPythonUnittest)
