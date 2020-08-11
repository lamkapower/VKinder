import unittest
from unittest.mock import patch
import main


class TestMainFunctions(unittest.TestCase):     
    token = '7790cde08d1b920be3256bb4c437eea14ea40cf715a0d568ab635d076e552dda9f383249a542426bf1bb9'
    
    def setUp(self):
        self.users = main.Users(self.token, '33', 'жен', 'Москва')
    
    def test_get_cities(self):
        self.assertEqual(1, self.users.get_cities())

    def test_define_sex(self):
         self.assertEqual(1, self.users.define_sex())

    def test_get_users(self):
        self.assertGreater(len(self.users.get_users()), 1)

    def test_get_photos(self):
        self.assertGreater(len(self.users.get_photos()), 1)

if __name__ == "__main__":
    unittest.main()
            