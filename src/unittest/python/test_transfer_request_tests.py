"""This is our testing script for transfer_request.py
 which intends to build the necessary tests for the task"""
import unittest
import os
import json
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
project_src = os.path.join(project_root, "main", "python")
if project_src not in sys.path:
    sys.path.insert(0, project_src)

from uc3m_money.transfer_request import process_transfer, AccountManagementException, TransferRequest
class BaseTest(unittest.TestCase):
    """Here we set up the json values for our unittests"""
    @classmethod
    def setUpClass(cls):
        """Loads our tests class json values"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tests_root = os.path.abspath(os.path.join(current_dir, ".."))
        json_file = os.path.join(tests_root, 'transfer_request_test_cases.json')

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

    def test_iban_formats_ok(self):
        """
        Test valid IBAN formats.
        Iterates over valid test cases that are not flagged with IBAN-specific errors.
        """
        for tc in self.test_cases["valid"]:
            # Here we assume that if the test case description mentions "IBAN" in a generic way,
            # the IBAN formats are correct.
            if "IBAN" in tc["description"] and "Spanish" not in tc["description"]:
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

    def test_iban_spanish_ok(self):
        """
        Test IBAN Spanish format.
        Iterates over invalid test cases that mention a Spanish IBAN issue.
        """
        for tc in self.test_cases["invalid"]:
            if "Spanish" in tc["description"]:
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
            if "Date not in DD/MM/YYYY" in tc["description"]:
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
            if "Date" in tc["description"]:
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
            if "components out of range" in tc["description"]:
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
            if "before the current date" in tc["description"]:
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

    def test_amount_boundary_values_ok(self):
        """
        Test that amounts outside the boundary values raise an error.
        Checks for amounts below the minimum (<10.00), above the maximum (>10,000.00),
        or with more than 2 decimal places.
        """
        for tc in self.test_cases["invalid"]:
            if (("below" in tc["description"] or
                    "above" in tc["description"] or
                    "more than" in tc["description"]) and ("amount" in tc["description"])):
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


class TestJsonValidation(BaseTest):
    """Here we check that our transaction is not in our JSON and that we added it"""

    def test_json_not_existing_ok(self):
        """
        Test that a valid transfer request is not already registered
        and returns a transfer code.
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

    def test_json_dump_ok(self):
        """
        Test that attempting a duplicate transfer (already existing in JSON)
        raises an exception.
        """
        for tc in self.test_cases["invalid"]:
            if "Duplicate transfer" in tc["description"]:
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
                    self.assertIn("Output JSON file already has that transfer", str(cm.exception))


class TestTransferRequest(unittest.TestCase):

    def setUp(self):
        # Set up the initial object for testing
        self.transfer = TransferRequest(
            from_iban="DE89370400440532013000",
            transfer_type="ORDINARY",
            to_iban="GB29NWBK60161331926819",
            transfer_concept="Payment for services",
            transfer_date="2025-03-09",
            transfer_amount=100.00
        )

    def test_setter_getter_from_iban(self):
        # Test setter and getter for 'from_iban'
        self.transfer.from_iban = "DE89370400440532013001"
        self.assertEqual(self.transfer.from_iban, "DE89370400440532013001")

    def test_setter_getter_to_iban(self):
        # Test setter and getter for 'to_iban'
        self.transfer.to_iban = "GB29NWBK60161331926820"
        self.assertEqual(self.transfer.to_iban, "GB29NWBK60161331926820")

    def test_setter_getter_transfer_type(self):
        # Test setter and getter for 'transfer_type'
        self.transfer.transfer_type = "IMMEDIATE"
        self.assertEqual(self.transfer.transfer_type, "IMMEDIATE")

    def test_setter_getter_transfer_amount(self):
        # Test setter and getter for 'transfer_amount'
        self.transfer.transfer_amount = 200.00
        self.assertEqual(self.transfer.transfer_amount, 200.00)

    def test_setter_getter_transfer_concept(self):
        # Test setter and getter for 'transfer_concept'
        self.transfer.transfer_concept = "Rent payment"
        self.assertEqual(self.transfer.transfer_concept, "Rent payment")

    def test_setter_getter_transfer_date(self):
        # Test setter and getter for 'transfer_date'
        self.transfer.transfer_date = "2025-03-10"
        self.assertEqual(self.transfer.transfer_date, "2025-03-10")

    def test_setter_getter_time_stamp(self):
        # Test that time_stamp is read-only (you can't set it)
        with self.assertRaises(AttributeError):
            self.transfer.time_stamp = "2025-03-09 10:00:00"

        # Assuming the time_stamp is automatically set during the transfer request
        self.assertIsNotNone(self.transfer.time_stamp)
if __name__ == '__main__':
    unittest.main()
