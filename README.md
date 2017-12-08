IPython-Unittest
==========

This extension provides testing support to IPython through cell magics. Currently, we have three magics that transforms the cell code and executes unittest: `%%unittest_main`, `%%unittest_testcase` and `%%unittest`; one magic to run external tests: `%%external`; and one associated magic to write external files: `%%write {mode}`

Please, take a look at [jupyter_dojo](https://github.com/JoaoFelipe/jupyter-dojo) to improve the jupyter support of this extension with:
* Test status in toolbar
* Argument --previous, to move to previous cells after execution
* Timer, pair programming log, function generation for coding dojo sessions
* Syntax highlight for `%%write {mode}` magic

How to Install
----

Install the python package by running

```
pip install ipython_unittest
```

or

```
conda install -c conda-forge ipython_unittest
```

Note that conda releases take more time to update. Use the pypi version if you want to get the most recent release at any given time.

It is strongly advisable to install the `jupyter_dojo` package as well:
```
pip install jupyter_dojo
```


To load the extension, please run:
```python
%load_ext ipython_unittest
```


Cell Magics
----

The first magic is `%%unittest_main`. This magic runs testcases defined in a cell

```python
%%unittest_main
class MyTest(unittest.TestCase):
    def test_1_plus_1_equals_2(self):
        sum = 1 + 1
        self.assertEqual(sum, 2)

    def test_2_plus_2_equals_4(self):
        self.assertEqual(2 + 2, 4)
```

The second magic is `%%unittest_testcase`. This magic creates a testcase with
functions defined in the cell and execute it.

```python
%%unittest_testcase
def test_1_plus_1_equals_2(self):
    sum = 1 + 1
    self.assertEqual(sum, 2)

def test_2_plus_2_equals_4(self):
    self.assertEqual(2 + 2, 4)
```

The third magic is `%%unittest`. This magic converts Python assert into
unittest functions.

```python
%%unittest
"1 plus 1 equals 2"
sum = 1 + 1
assert sum == 2
"2 plus 2 equals 4"
assert 2 + 2 == 4
```

By default, docstring in this magic will separate unittest methods.
However, if docstrings are not provided, the magic will create a method for
for each assert.

These magics support optional arguments:
```
-p (--previous) P: set cursor to P cells before (default: -1 = next cell)
-s (--stream) S:   set test output stream (default: 'sys.stdout')
-t (--testcase) T: define TestCase name.
                   Valid for '%%unittest' and '%%unittest_testcase'
-u (--unparse):    print cell source code after transformations.
```

The `--previous` argument only works with the [jupyter_dojo](https://github.com/JoaoFelipe/jupyter-dojo) extension installed.

The fourth magic is `%%external`. This magic runs external system commands and check their exit codes. This way, it is possible to run tests from other languages:
```python
%%external -p 1
mocha test.js
```

The `%external` magic supports the argument `--previous` described before.


Finally, since it is possible to run external commands, we included an extra magic, `%%write` to write files and keep the syntax highlight.
This magic receives a CodeMirror mode as first argument and the remaining arguments are redirected to IPython's `%%writefile`

Once again, the `%external` magic only provides syntax highlighting should you have the [jupyter_dojo](https://github.com/JoaoFelipe/jupyter-dojo) extension installed.

```javascript
%%write javascript test.js
var assert = require('assert');
describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when the value is not present', function() {
      assert.equal(-1, [1,2,3].indexOf(4));
    });
  });
});
```


## Links

- [Jupyter Dojo](https://github.com/JoaoFelipe/jupyter-dojo)
- [Pypi.org](https://pypi.org/project/ipython-unittest/)
- [Conda Forge Feedstock](https://github.com/conda-forge/ipython_unittest-Feedstock)

Contact
----

Do not hesitate to contact me:

* João Felipe Pimentel <joaofelipenp@gmail.com>

License Terms
-------------

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
