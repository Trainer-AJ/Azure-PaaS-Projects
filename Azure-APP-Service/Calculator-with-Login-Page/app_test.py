import unittest
from app import *

class TestCalculator(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Calculator', response.data)

    def test_addition(self):
        response = self.app.post('/calculate', data=dict(num1=2, operation='add', num2=3))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The result is: 5.0', response.data)

    def test_subtraction(self):
        response = self.app.post('/calculate', data=dict(num1=5, operation='subtract', num2=3))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The result is: 2.0', response.data)

    def test_multiplication(self):
        response = self.app.post('/calculate', data=dict(num1=2, operation='multiply', num2=3))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The result is: 6.0', response.data)

    def test_division(self):
        response = self.app.post('/calculate', data=dict(num1=6, operation='divide', num2=3))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The result is: 2.0', response.data)

    def test_divide_by_zero(self):
        response = self.app.post('/calculate', data=dict(num1=6, operation='divide', num2=0))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error: Cannot divide by zero!', response.data)

if __name__ == '__main__':
    unittest.main()
