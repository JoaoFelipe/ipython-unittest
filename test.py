import unittest
def soma(x, y):
    return x + y

class JupyterTest(unittest.TestCase):

    def test_soma_1_1_retorna_2(self):
        'soma 1 + 1 retorna 2'
        self.assertEqual(soma(1, 1), 2)

    def test_soma_1_2_retorna_3(self):
        'soma 1 + 2 retorna 3'
        self.assertEqual(soma(1, 2), 3)

    def test_soma_2_2_retorna_4(self):
        'soma 2 + 2 retorna 4'
        self.assertEqual(soma(2, 2), 4)