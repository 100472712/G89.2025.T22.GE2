import unittest
import os
import json
import sys

# Adjust sys.path to import the main module
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
project_src = os.path.join(project_root, "main", "python")
if project_src not in sys.path:
    sys.path.insert(0, project_src)

from src.main.python.uc3m_money.account_deposit import AccountDeposit
from src.main.python.uc3m_money.account_management_exception import AccountManagementException


class BaseTest(unittest.TestCase):
    """Setup for test cases"""

    @classmethod
    def setUpClass(cls):
        """Load test cases from JSON"""
        json_file = os.path.join(os.path.dirname(__file__), "deposit_test_cases.json")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                cls.test_cases = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading JSON test cases: {e}")


class TestDepositRequest(BaseTest):
    """Tests deposit validation and processing"""

    def test_valid_deposits(self):
        """Tests valid deposit requests"""
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):
                deposit = AccountDeposit(
                    to_iban=tc["to_iban"],
                    deposit_amount=float(tc["amount"].split("EUR ")[1])
                )
                self.assertIsInstance(deposit.deposit_signature, str)
                self.assertEqual(len(deposit.deposit_signature), 64)  # SHA-256 hash length

    def test_invalid_ibans(self):
        """Tests invalid IBANs"""
        for tc in self.test_cases["invalid"]:
            if "IBAN" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Invalid IBAN format", str(cm.exception))

    def test_invalid_amount_format(self):
        """Tests deposits with incorrect amount formatting"""
        for tc in self.test_cases["invalid"]:
            if "format" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        deposit_amount = tc["amount"]
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=deposit_amount
                        )
                    self.assertIn("Invalid amount format", str(cm.exception))

    def test_amount_below_minimum(self):
        """Tests deposits below minimum allowed"""
        for tc in self.test_cases["invalid"]:
            if "below minimum" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Amount must be >=", str(cm.exception))

    def test_amount_above_maximum(self):
        """Tests deposits exceeding the maximum allowed"""
        for tc in self.test_cases["invalid"]:
            if "exceeds maximum" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Amount must be <=", str(cm.exception))

    def test_negative_amount(self):
        """Tests deposits with negative amounts"""
        for tc in self.test_cases["invalid"]:
            if "Negative deposit amount" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Amount must be positive", str(cm.exception))

    def test_zero_amount(self):
        """Tests deposits with zero amount"""
        for tc in self.test_cases["invalid"]:
            if "Amount is zero" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Amount must be positive", str(cm.exception))

    def test_more_than_two_decimal_places(self):
        """Tests deposits with invalid decimal places"""
        for tc in self.test_cases["invalid"]:
            if "more than two decimal places" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        deposit_amount = float(tc["amount"].split("EUR ")[1])
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=deposit_amount
                        )
                    self.assertIn("Amount format invalid, must have two decimal places", str(cm.exception))

    def test_invalid_currency_format(self):
        """Tests deposits with invalid currency format"""
        for tc in self.test_cases["invalid"]:
            if "Invalid currency format" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=tc["amount"]
                        )
                    self.assertIn("Invalid currency format", str(cm.exception))

    def test_leading_trailing_spaces_in_iban(self):
        """Tests IBANs with leading or trailing spaces"""
        for tc in self.test_cases["invalid"]:
            if "contains spaces" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"].strip(),
                            deposit_amount=float(tc["amount"].split("EUR ")[1])
                        )
                    self.assertIn("Invalid IBAN format", str(cm.exception))

    def test_amount_contains_comma(self):
        """Tests deposits where decimal separator is a comma instead of a period"""
        for tc in self.test_cases["invalid"]:
            if "contains commas" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=tc["amount"]
                        )
                    self.assertIn("Invalid amount format", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
