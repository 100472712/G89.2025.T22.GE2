"""This is our testing script for transfer_request.py
 which intends to build the necessary tests for the task"""
import unittest
import os
import json
import sys
# pylint: disable=import-error
from uc3m_money.transfer_request import (process_transfer,
                                         AccountManagementException)

# pylint: disable=duplicate-code
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
project_src = os.path.join(project_root, "main", "python")
if project_src not in sys.path:
    sys.path.insert(0, project_src)


class BaseTest(unittest.TestCase): # pylint: disable=duplicate-code
    """Here we set up the json values for our unittests"""
    @classmethod
    def setUpClass(cls):
        """Loads our tests class json values"""
        current_dir_1 = os.path.dirname(os.path.abspath(__file__))
        tests_root = os.path.abspath(os.path.join(current_dir_1, ".."))
        json_file = os.path.join(tests_root, 'transfer_request_test_cases.json')
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


class TestValidatingIbans(BaseTest):
    """Here we validate our Ibans both from and to"""


    def test_iban_spanish_ok(self):
        """
        Test IBAN Spanish format.
        Iterates over invalid test cases that mention a Spanish IBAN issue.
        """
        for tc in self.test_cases["invalid"]:
            if "IBAN" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                            )
                    self.assertIn("Not valid IBANS", str(cm.exception))


class TestConceptValidation(BaseTest):
    """We check our concept in this class with several methods"""

    def test_concept_amount_words_ok(self):
        """
        Test that the concept has at least 2 words.
        Uses invalid test cases where the concept is too short.
        """
        for tc in self.test_cases["invalid"]:
            if "one word" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Concept is not valid", str(cm.exception))

    def test_concept_chars_amount_ok(self):
        """
        Test that the concept has a valid number
        of characters.
        Uses invalid test cases where the concept
        length is out of range.
        """
        for tc in self.test_cases["invalid"]:
            if "length" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Concept is not valid", str(cm.exception))


class TestTypeValidation(BaseTest):
    """Here we check that our transaction Type is one of the possible ones"""

    def test_type_possible_values_ok(self):
        """
        Test transfer type validation.
        Checks invalid test cases where the transfer type is not allowed and also validates
        the valid ones.
        """
        # Test invalid transfer types:
        for tc in self.test_cases["invalid"]:
            if "Transfer type is not" in tc["description"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Transfer type is not valid", str(cm.exception))
        # Test valid transfer types:
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):
                result = process_transfer(
                    from_iban=tc["from_iban"],
                    to_iban=tc["to_iban"],
                    concept=tc["concept"],
                    transfer_type=tc["transfer_type"],
                    date=tc["date"],
                    amount=tc["amount"]
                )
                self.assertIsInstance(result, str)
                self.assertIn("Transfer Code", result)


class TestDateValidation(BaseTest):
    """This class checks that our transaction date is correct."""

    def test_date_format_ok(self):
        """
        Test date format validation.
        Uses invalid test cases where the date format is not DD/MM/YYYY.
        """
        for tc in self.test_cases["invalid"]:
            if "date" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Transfer date is not valid", str(cm.exception))
        # Also test valid dates:
        for tc in self.test_cases["valid"]:
            if "dfate" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    result = process_transfer(
                        from_iban=tc["from_iban"],
                        to_iban=tc["to_iban"],
                        concept=tc["concept"],
                        transfer_type=tc["transfer_type"],
                        date=tc["date"],
                        amount=tc["amount"]
                    )
                    self.assertIsInstance(result, str)
                    self.assertIn("Transfer Code", result)

    def test_date_values_ok(self):
        """
        Test date component values.
        Uses invalid test cases where the date components are out of range.
        """
        for tc in self.test_cases["invalid"]:
            if "date" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Transfer date is not valid", str(cm.exception))

    def test_date_before_current_ok(self):
        """
        Test that a date before the current system date raises an error.
        """
        for tc in self.test_cases["invalid"]:
            if "dpate" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Transfer date is in the past", str(cm.exception))


class TestAmountValidation(BaseTest):
    """This class checks that the amount of the transaction is valid"""

    def test_amount_data_type_float_ok(self):
        """
        Test that a valid amount (numeric string) is accepted.
        """
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):
                result = process_transfer(
                    from_iban=tc["from_iban"],
                    to_iban=tc["to_iban"],
                    concept=tc["concept"],
                    transfer_type=tc["transfer_type"],
                    date=tc["date"],
                    amount=tc["amount"]
                )
                self.assertIsInstance(result, str)
                self.assertIn("Transfer Code", result)

    def test_amount_float_decimals_2_ok(self):
        """
        Test that valid amounts with exactly 2 decimals pass.
        """
        for tc in self.test_cases["valid"]:
            with self.subTest(tc=tc["id"]):

                result = process_transfer(
                    from_iban=tc["from_iban"],
                    to_iban=tc["to_iban"],
                    concept=tc["concept"],
                    transfer_type=tc["transfer_type"],
                    date=tc["date"],
                    amount=tc["amount"]
                )
                self.assertIsInstance(result, str)
                self.assertIn("Transfer Code", result)

    def test_amount_boundary_values_ko(self):
        """
        Test that amounts outside the boundary values raise an error.
        Checks for amounts below the minimum (<10.00), above the maximum (>10,000.00),
        or with more than 2 decimal places.
        """
        for tc in self.test_cases["invalid"]:
            if "Abmount" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Amount is not valid", str(cm.exception))

    def test_amount_format_values_ko(self):
        """
        Test that amount has a float format
        """
        for tc in self.test_cases["invalid"]:
            if "Afmount" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Amount is not valid", str(cm.exception))

    def test_amount_decimals_values_ko(self):
        """
        Test that amount has a float format
        """
        for tc in self.test_cases["invalid"]:
            if "Admount" in tc["expected"]:
                with self.subTest(tc=tc["id"]):
                    with self.assertRaises(AccountManagementException) as cm:
                        process_transfer(
                            from_iban=tc["from_iban"],
                            to_iban=tc["to_iban"],
                            concept=tc["concept"],
                            transfer_type=tc["transfer_type"],
                            date=tc["date"],
                            amount=tc["amount"]
                        )
                    self.assertIn("Amount is not valid", str(cm.exception))



if __name__ == '__main__':
    unittest.main()
