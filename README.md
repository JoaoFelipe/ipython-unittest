IPython-Unittest
==========

This extension provides three cell magics for IPython/Jupyter

First magic is `%%unittest_main`. This magic runs testcases defined in a cell

```python
%%unittest_main
class MyTest(unittest.TestCase):
    def test_1_plus_1_equals_2(self):
        sum = 1 + 1
        self.assertEqual(sum, 2)
	
    def test_2_plus_2_equals_4(self):
        self.assertEqual(2 + 2, 4)
```

Second magic is `%%unittest_testcase`. This magic creates a testcase with
functions defined in the cell and execute it.

```python
%%unittest_testcase
def test_1_plus_1_equals_2(self):
    sum = 1 + 1
    self.assertEqual(sum, 2)

def test_2_plus_2_equals_4(self):
    self.assertEqual(2 + 2, 4)
```

Third magic is `%%unittest`. This magic converts Python assert into
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
-c (--color):      change logo color to indicate whether or not the tests
                   have passed
-p (--previous) P: set cursor to P cells before (default: -1 = next cell)
-s (--stream) S:   set test output stream (default: 'sys.stdout')
-t (--testcase) T: define TestCase name.
                   Valid for '%%unittest' and '%%unittest_testcase'
-u (--unparse):    print cell source code after transformations.
```

How to Install
----

```pip install ipython_unittest```


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

