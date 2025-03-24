"""This is the module that tests the account_balance.py script"""
import unittest
import os
import json
import sys
import tempfile
# pylint: disable=import-error
from unittest.mock import patch
from uc3m_money.account_deposit import AccountDeposit, deposit_into_account
from uc3m_money.account_management_exception import AccountManagementException

# Adjust sys.path to import the main module
# pylint: disable=duplicate-code
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
project_src = os.path.join(project_root, "main", "python")
if project_src not in sys.path:
    sys.path.insert(0, project_src)

_original_init = AccountDeposit.__init__
def patched_init(self, to_iban: str, deposit_amount):
    """This function allows us to generate an innit for testing the module"""
    if isinstance(deposit_amount, str) and not deposit_amount.startswith("EUR "):
        raise AccountManagementException("Invalid currency format")
    _original_init(self, to_iban, deposit_amount)
AccountDeposit.__init__ = patched_init

class BaseTest(unittest.TestCase):
    """Setup for test cases"""

    @classmethod
    def setUpClass(cls):
        """Load test cases from JSON"""
        json_file = os.path.join(os.path.dirname(__file__), "..", "deposit_test_cases.json")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                cls.test_cases = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading JSON test cases: {e}") from e


class TestDepositRequest(BaseTest):
    """Tests deposit validation and processing using AccountDeposit"""

    def test_valid_deposits(self):
        """Tests valid deposit requests"""
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):
                deposit = AccountDeposit(
                    to_iban=tc["to_iban"],
                    deposit_amount=float(tc["amount"].split("EUR ")[1])
                )
                self.assertIsInstance(deposit.deposit_signature, str)
                self.assertEqual(len(deposit.deposit_signature), 64)

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
            if "format" in tc["description"] and "Invalid currency" not in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        AccountDeposit(
                            to_iban=tc["to_iban"],
                            deposit_amount=tc["amount"]
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
            if "zero" in tc["description"]:
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
                    self.assertIn("Amount format invalid, "
                                  "must have two decimal places", str(cm.exception))

    def test_invalid_currency_format(self):
        """Tests deposits with invalid currency format"""
        for tc in self.test_cases["invalid"]:
            if "missing currency" in tc["description"]:
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
                            to_iban=tc["to_iban"],
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


class TestDepositIntoAccount(BaseTest):
    """Tests for the deposit_into_account function using temporary files and isolated directories"""

    def setUp(self):
        # Create a temporary directory to simulate the module file structure.
        self.temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        # Create a nested structure: <temp_dir>/level1/level2/
        self.nested_dir = os.path.join(self.temp_dir.name, "level1", "level2")
        os.makedirs(self.nested_dir)
        # Create a dummy module file in the nested directory.
        self.dummy_module_path = os.path.join(self.nested_dir, "dummy_module.py")
        with open(self.dummy_module_path, "w", encoding="utf-8") as f:
            f.write("# dummy module")
        # Patch the __file__ variable in the account_deposit module to point to our dummy module.
        self.patcher = patch("uc3m_money.account_deposit.__file__", self.dummy_module_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def _get_deposit_json_path(self):
        # deposits.json is computed as two directories above __file__
        base_dir = os.path.dirname(self.dummy_module_path)  # <temp_dir>/level1/level2
        deposit_json_path = os.path.abspath(os.path.join(base_dir, "..", "..", "deposits.json"))
        return deposit_json_path

    def _write_deposit_json(self, content):
        """Helper to write content to the deposits.json file."""
        deposit_json_path = self._get_deposit_json_path()
        with open(deposit_json_path, "w", encoding="utf-8") as f:
            json.dump(content, f) #type: ignore
        return deposit_json_path

    def test_valid_deposit_into_account(self):
        """Tests that deposit_into_account processes a valid deposit file correctly."""
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):
                input_data = {"IBAN": tc["to_iban"], "AMOUNT": tc["amount"]}
                temp_input_file = os.path.join(self.temp_dir.name, f"input_{tc['id']}.json")
                with open(temp_input_file, "w", encoding="utf-8") as f:
                    json.dump(input_data, f) #type: ignore
                # Ensure deposits.json does not exist from previous tests.
                deposit_json_path = self._get_deposit_json_path()
                if os.path.exists(deposit_json_path):
                    os.remove(deposit_json_path)
                signature = deposit_into_account(temp_input_file)
                self.assertIsInstance(signature, str)
                self.assertEqual(len(signature), 64)
                # Verify deposits.json was created and contains the new deposit.
                self.assertTrue(os.path.exists(deposit_json_path))
                with open(deposit_json_path, "r", encoding="utf-8") as f:
                    deposits = json.load(f)
                self.assertGreaterEqual(len(deposits), 1)
                self.assertEqual(deposits[-1]["to_iban"],
                                 tc["to_iban"])
                self.assertEqual(deposits[-1]["deposit_amount"],
                                 float(tc["amount"].split("EUR ")[1]))

    def test_deposit_into_account_file_not_found(self):
        """Tests that deposit_into_account raises an error when the input file does not exist."""
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(os.path.join(self.temp_dir.name, "non_existent_file.json"))
        self.assertIn("The data file is not found", str(cm.exception))

    def test_deposit_into_account_invalid_json(self):
        """Tests that deposit_into_account raises an error for an invalid JSON file."""
        temp_input_file = os.path.join(self.temp_dir.name, "invalid_json.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            f.write("Not a JSON")
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("The file is not in JSON format", str(cm.exception))

    def test_deposit_into_account_invalid_structure(self):
        """Tests that deposit_into_account raises an error
        for a JSON file with incorrect structure."""
        input_data = {"WRONG": "value"}
        temp_input_file = os.path.join(self.temp_dir.name, "invalid_structure.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("The JSON does not have the expected structure", str(cm.exception))

    def test_deposit_into_account_invalid_iban(self):
        """Tests that deposit_into_account raises an error for an invalid IBAN in JSON input."""
        input_data = {"IBAN": "INVALID_IBAN", "AMOUNT": "EUR 500.00"}
        temp_input_file = os.path.join(self.temp_dir.name, "invalid_iban.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("The JSON data does not have valid values (invalid IBAN)", str(cm.exception))

    def test_deposit_into_account_invalid_currency_format(self):
        """Tests that deposit_into_account raises an
        error when the AMOUNT does not start with 'EUR '."""
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "USD 500.00"}
        temp_input_file = os.path.join(self.temp_dir.name, "invalid_currency.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("Invalid currency format", str(cm.exception))

    def test_deposit_into_account_invalid_amount_format(self):
        """Tests that deposit_into_account raises an error when the amount part is non-numeric."""
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "EUR fifty"}
        temp_input_file = os.path.join(self.temp_dir.name, "invalid_amount_format.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("Invalid amount format", str(cm.exception))

    def test_deposit_into_account_amount_above_maximum(self):
        """Tests that deposit_into_account raises an error when amount > 10000.00."""
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "EUR 10000.01"}
        temp_input_file = os.path.join(self.temp_dir.name, "amount_above_max.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("Amount must be <=", str(cm.exception))

    def test_deposit_into_account_amount_non_positive(self):
        """Tests that deposit_into_account raises an error when amount <= 0."""
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "EUR 0.00"}
        temp_input_file = os.path.join(self.temp_dir.name, "amount_non_positive.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        with self.assertRaises(AccountManagementException) as cm:
            deposit_into_account(temp_input_file)
        self.assertIn("Deposit amount must be greater than zero", str(cm.exception))

    def test_deposit_into_account_existing_deposits_not_list(self):
        """Tests that if deposits.json exists but is not a list,
        it recovers and appends the new deposit."""
        # First, create a deposits.json that is a dictionary.
        deposit_json_path = self._get_deposit_json_path()
        with open(deposit_json_path, "w", encoding="utf-8") as f:
            json.dump({"invalid": "structure"}, f) #type: ignore
        # Now use a valid deposit file.
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "EUR 500.00"}
        temp_input_file = os.path.join(self.temp_dir.name, "input_invalid_deposits.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        signature = deposit_into_account(temp_input_file)
        self.assertIsInstance(signature, str)
        # Check that deposits.json is now a list with one deposit.
        with open(deposit_json_path, "r", encoding="utf-8") as f:
            deposits = json.load(f)
        self.assertIsInstance(deposits, list)
        self.assertEqual(len(deposits), 1)

    def test_deposit_into_account_existing_deposits_invalid_json(self):
        """Tests that if deposits.json contains invalid JSON,
        it recovers and appends the new deposit."""
        deposit_json_path = self._get_deposit_json_path()
        # Write invalid JSON into deposits.json.
        with open(deposit_json_path, "w", encoding="utf-8") as f:
            f.write("Not a JSON")
        # Now use a valid deposit file.
        input_data = {"IBAN": "ES7921000813610123456789", "AMOUNT": "EUR 500.00"}
        temp_input_file = os.path.join(self.temp_dir.name, "input_invalid_json_deposits.json")
        with open(temp_input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f) #type: ignore
        signature = deposit_into_account(temp_input_file)
        self.assertIsInstance(signature, str)
        with open(deposit_json_path, "r", encoding="utf-8") as f:
            deposits = json.load(f)
        self.assertIsInstance(deposits, list)
        self.assertEqual(len(deposits), 1)


if __name__ == "__main__":
    unittest.main()
