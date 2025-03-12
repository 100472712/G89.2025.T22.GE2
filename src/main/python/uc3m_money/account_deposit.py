import json
import os

import hashlib
from datetime import datetime, timezone

class AccountDeposit:
    """Class representing a deposit request."""

    def __init__(self, to_iban: str, deposit_amount):
        # First validate the IBAN format
        if not AccountManager.validate_iban(to_iban):
            raise AccountManagementException("Invalid IBAN format")

        # Then validate the deposit amount format
        try:
            deposit_amount = float(deposit_amount)
        except ValueError:
            raise AccountManagementException("Invalid amount format")

        # Validate the deposit amount range
        if deposit_amount <= 0:
            raise AccountManagementException("Amount must be positive")

        if deposit_amount < 10.00:
            raise AccountManagementException("Amount must be >= 10.00")

        if deposit_amount > 10000.00:
            raise AccountManagementException("Amount must be <= 10000.00")

        # Check for decimal places (limit to 2 decimal places)
        if len(str(deposit_amount).split(".")[1]) > 2:
            raise AccountManagementException("Amount format invalid, must have two decimal places")

        # Setting instance variables
        self.__alg = "SHA-256"
        self.__type = "DEPOSIT"
        self.__to_iban = to_iban
        self.__deposit_amount = deposit_amount

        justnow = datetime.now(timezone.utc)
        self.__deposit_date = datetime.timestamp(justnow)

    def to_json(self):
        """returns the object data in json format"""
        return {
            "alg": self.__alg,
            "type": self.__type,
            "to_iban": self.__to_iban,
            "deposit_amount": self.__deposit_amount,
            "deposit_date": self.__deposit_date,
            "deposit_signature": self.deposit_signature
        }

    def __signature_string(self):
        """Composes the string to be used for generating the key for the date"""
        return "{alg:" + str(self.__alg) +",typ:" + str(self.__type) +",iban:" + \
               str(self.__to_iban) + ",amount:" + str(self.__deposit_amount) + \
               ",deposit_date:" + str(self.__deposit_date) + "}"

    @property
    def deposit_signature(self):
        """Returns the sha256 signature of the deposit details"""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()




from src.main.python.uc3m_money.account_manager import AccountManager
from src.main.python.uc3m_money.account_deposit import AccountDeposit
from src.main.python.uc3m_money.account_management_exception import AccountManagementException

def deposit_into_account(input_file: str) -> str:
    """
    Reads a JSON file, validates the IBAN and amount,
    creates a deposit instance, and saves it.

    Args:
        input_file (str): Path to the input JSON file.

    Returns:
        str: SHA-256 deposit signature.

    Raises:
        AccountManagementException: If any validation fails.
    """

    # Step 1: Check if file exists
    if not os.path.exists(input_file):
        raise AccountManagementException("The data file is not found.")

    # Step 2: Try reading the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise AccountManagementException("The file is not in JSON format.")

    # Step 3: Validate JSON structure
    if not isinstance(data, dict) or "IBAN" not in data or "AMOUNT" not in data:
        raise AccountManagementException("The JSON does not have the expected structure.")

    iban = data["IBAN"]
    amount_str = data["AMOUNT"]

    # Step 4: Validate IBAN
    if not AccountManager.validate_iban(iban):
        raise AccountManagementException("The JSON data does not have valid values (invalid IBAN).")

    # Step 5: Validate Amount
    if not amount_str.startswith("EUR "):
        raise AccountManagementException("Invalid currency format.")

    try:
        amount = float(amount_str.split("EUR ")[1])


    except ValueError:
        raise AccountManagementException("Invalid amount format.")

    if amount > 10000.00:
        raise AccountManagementException("Amount must be <= 10000.00")

    if amount <= 0:
        raise AccountManagementException("Deposit amount must be greater than zero.")

    # Step 6: Create AccountDeposit instance
    deposit = AccountDeposit(to_iban=iban, deposit_amount=amount)

    # Step 7: Save the deposit data to a JSON file
    base_dir = os.path.dirname(__file__)
    deposit_json_path = os.path.join(base_dir, "deposits.json")

    # Load existing deposits
    if os.path.exists(deposit_json_path):
        with open(deposit_json_path, 'r', encoding='utf-8') as f:
            try:
                deposits = json.load(f)
                if not isinstance(deposits, list):
                    deposits = []
            except json.JSONDecodeError:
                deposits = []
    else:
        deposits = []

    # Add the new deposit
    deposits.append(deposit.to_json())

    # Write back to the JSON file
    with open(deposit_json_path, 'w', encoding='utf-8') as f:
        json.dump(deposits, f, indent=4)

    return deposit.deposit_signature

