"""This module tests function3 account_balance script"""
import unittest
import os
import json
# pylint: disable=import-error
from unittest.mock import patch
from uc3m_money.account_balance import store_new_balance, AccountManagementException


def fake_exists_tc2(path):
    """For tc2, simulate that account_balances.json is missing"""
    if path.endswith("account_balances.json"):
        return False
    return True

def fake_exists_tc4(path):
    """For tc4, simulate that all_transactions.json is missing"""
    if path.endswith("all_transactions.json"):
        return False
    return True

class BaseTest(unittest.TestCase): # pylint: disable=duplicate-code
    """Here we set up the json values for our unittests"""
    @classmethod
    def setUpClass(cls):
        """Loads our tests class json values"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tests_root = os.path.abspath(os.path.join(current_dir, ".."))
        json_file = os.path.join(tests_root, 'account_balance_test_cases.json')
        # pylint: disable=duplicate-code
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                cls.test_cases = json.load(f)
            print("Loaded test cases from JSON.")
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            raise
    @classmethod
    def tearDownClass(cls):
        """cleans the test class environment once finished"""
        print("Tearing down class environment...")
    def setUp(self):
        """Set Ups the test"""
        print("Setting up test...")
        self.sample_data = "common value"
    def tearDown(self):
        """Ends the test"""
        print("Ending test...")

class TestAccountBalanceTests(BaseTest):
    """Here we will be testing our code seeing that it passes all the graph nodes."""

    def test_case_1_ok(self):
        """Here we check that our code passes test case 1.
        PATH: valid IBAN and transactions"""
        iban = self.test_cases["tc1"]["iban"]
        self.assertEqual(store_new_balance(iban), True)

    def test_case_2_ko(self):
        """Here we check that our code raises an exception for tc2.
        Path: valid IBAN no balance json file"""
        iban = self.test_cases["tc2"]["iban"]
        with patch("uc3m_money.account_balance.os.path.exists", side_effect=fake_exists_tc2):
            with self.assertRaises(AccountManagementException):
                store_new_balance(iban)

    def test_case_3_ko(self):
        """Here we check that our code raises an exception for tc3.
        Path: valid IBAN not in all iban json file"""
        iban = self.test_cases["tc3"]["iban"]
        with self.assertRaises(AccountManagementException):
            store_new_balance(iban)

    def test_case_4_ko(self):
        """Here we check that our code raises an exception for tc4.
        Path: valid IBAN  but no json all_transactions file"""
        iban = self.test_cases["tc4"]["iban"]
        with patch("uc3m_money.account_balance.os.path.exists", side_effect = fake_exists_tc4):
            with self.assertRaises(AccountManagementException):
                store_new_balance(iban)

    def test_case_5_ko(self):
        """Here we check that oour code raises an exception for tc5.
        Path Not valid IBAN"""
        iban = self.test_cases["tc5"]["iban"]
        with self.assertRaises(AccountManagementException):
            store_new_balance(iban)


if __name__ == '__main__':
    unittest.main()
