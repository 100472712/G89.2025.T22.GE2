"""MODULE: transfer_request. Contains the transfer request class and processing function."""
import hashlib
import json
import os
from datetime import datetime, timezone

class AccountManagementException(Exception):
    """Exception to be raised for account management errors."""


class TransferRequest:
    """Class representing a transfer request."""
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=too-many-arguments
    def __init__(self,
                 from_iban: str,
                 transfer_type: str,
                 to_iban: str,
                 transfer_concept: str,
                 transfer_date: str,
                 transfer_amount: float):
        self.__from_iban = from_iban
        self.__to_iban = to_iban
        self.__transfer_type = transfer_type
        self.__transfer_concept = transfer_concept
        self.__transfer_date = transfer_date
        self.__transfer_amount = transfer_amount
        justnow = datetime.now(timezone.utc)
        self.__time_stamp = datetime.timestamp(justnow)

    def __str__(self):
        return "Transfer:" + json.dumps(self.__dict__)

    def to_json(self):
        """Returns the object information in JSON format."""
        return {
            "from_iban": self.__from_iban,
            "to_iban": self.__to_iban,
            "transfer_type": self.__transfer_type,
            "transfer_amount": self.__transfer_amount,
            "transfer_concept": self.__transfer_concept,
            "transfer_date": self.__transfer_date,
            "time_stamp": self.__time_stamp,
            "transfer_code": self.transfer_code
        }

    @property
    def from_iban(self):
        """Sender's IBAN"""
        return self.__from_iban

    @from_iban.setter
    def from_iban(self, value):
        self.__from_iban = value

    @property
    def to_iban(self):
        """Receiver's IBAN"""
        return self.__to_iban

    @to_iban.setter
    def to_iban(self, value):
        self.__to_iban = value

    @property
    def transfer_type(self):
        """Transfer type: ORDINARY, URGENT or IMMEDIATE"""
        return self.__transfer_type

    @transfer_type.setter
    def transfer_type(self, value):
        self.__transfer_type = value

    @property
    def transfer_amount(self):
        """Transfer amount"""
        return self.__transfer_amount

    @transfer_amount.setter
    def transfer_amount(self, value):
        self.__transfer_amount = value

    @property
    def transfer_concept(self):
        """Transfer concept"""
        return self.__transfer_concept

    @transfer_concept.setter
    def transfer_concept(self, value):
        self.__transfer_concept = value

    @property
    def transfer_date(self):
        """Transfer date"""
        return self.__transfer_date

    @transfer_date.setter
    def transfer_date(self, value):
        self.__transfer_date = value

    @property
    def time_stamp(self):
        """Timestamp of the request (read-only)"""
        return self.__time_stamp

    @property
    def transfer_code(self):
        """Returns the MD5 signature (transfer code)"""
        return hashlib.md5(str(self).encode()).hexdigest()

def valid_iban(iban: str, check_spanish: bool = True) -> bool:
    """
    Validate IBAN format.
    When check_spanish is True, enforce Spanish IBAN rules:
      - Must start with 'ES'
      - Must be exactly 24 characters long
      - Characters after 'ES' must be all digits
    When False, a generic IBAN is expected:
      - At least 15 characters and at most 34
      - Must be alphanumeric
    """
    if check_spanish:
        return iban.startswith("ES") and (len(iban) == 24) and iban[2:].isdigit()
    return 15 <= len(iban) <= 34 and iban.isalnum()

# pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-positional-arguments, too-many-statements
def process_transfer(from_iban: str, to_iban: str, concept: str,
                     transfer_type: str, date: str, amount: str) -> str:
    """
    Process a transfer request after validating the inputs.

    Validates:
      - IBANs: spanish and valid
      - Transfer type: must be one of {"ORDINARY", "URGENT", "IMMEDIATE"}.
      - Date: must be in DD/MM/YYYY format, be a valid date,
      have DD between 01 and 31, MM between 01 and 12,
        and year between 2025 and 2050, and not be before the current date.
      - Amount: must be a numeric value (allowing commas as thousand separators)
       with exactly 2 decimals,
                and between 10.00 and 10,000.00 (inclusive).
      - The transfer must not be a duplicate (based on its transfer code) in the stored JSON file.

    On success, the transfer is saved and a string containing the transfer code is returned.
    """
    # Validate sender IBAN (always require Spanish IBAN format)
    if not valid_iban(from_iban, check_spanish=True):
        raise AccountManagementException("Not valid IBANS")

    # Validate receiver IBAN:
    # For IMMEDIATE transfers, allow any non-empty string.
    # Otherwise, enforce Spanish IBAN format.
    if transfer_type != "IMMEDIATE":
        if not valid_iban(to_iban, check_spanish=True):
            raise AccountManagementException("Not valid IBANS")
    else:
        if not isinstance(to_iban, str) or not to_iban.strip():
            raise AccountManagementException("Not valid IBANS")

    # Validate concept:
    # Must contain at least two words and be between 10 and 30 characters.
    words = concept.split()
    if len(words) < 2 or not (10 <= len(concept) <= 30):
        raise AccountManagementException("Concept is not valid")

    # Validate transfer type:
    allowed_types = {"ORDINARY", "URGENT", "IMMEDIATE"}
    if transfer_type not in allowed_types:
        raise AccountManagementException("Transfer type is not valid")

    # Validate date:
    try:
        date_obj = datetime.strptime(date, "%d/%m/%Y")
    except ValueError as exc:
        raise AccountManagementException("Transfer date is not valid") from exc
    day, month, year = int(date[:2]), int(date[3:5]), int(date[6:])
    if not (1 <= day <= 31 and 1 <= month <= 12 and 2025 <= year <= 2051):
        raise AccountManagementException("Transfer date is not valid")
    if date_obj.date() < datetime.now().date():
        raise AccountManagementException("Transfer date is not valid")

    # Validate amount:
    # Normalize the amount if it's a float
    # Validate amount:
    if isinstance(amount, float):
        # Ensure the amount has exactly two decimal places
        normalized_amount = f"{amount:.2f}"
    else:
        # If amount is a string, normalize it (remove commas if any)
        normalized_amount = amount.replace(",", "")

    # Ensure the amount has exactly one decimal point
    if normalized_amount.count('.') != 1:
        raise AccountManagementException("Amount is not valid")

    # Split the amount into integer and decimal parts
    integer_part, decimal_part = normalized_amount.split('.')

    # Validate that both parts are digits and the decimal part has exactly 2 digits
    if not (integer_part.isdigit() and decimal_part.isdigit() and len(decimal_part) == 2):
        raise AccountManagementException("Amount is not valid")

    # Convert the normalized amount to float and check its validity
    try:
        float_amount = float(normalized_amount)
    except ValueError:
        raise AccountManagementException("Amount is not valid")

    # Check that the amount is within the valid range (10.00 to 10000.00
    if not (10.00 <= float_amount <= 10000.00):
        raise AccountManagementException("Amount is not valid")

    transfer = TransferRequest(from_iban, transfer_type, to_iban, concept, date, float_amount)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    json_path = os.path.join(base_dir, "stored_transactions.json")

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                transactions = json.load(f)
                if not isinstance(transactions, list):
                    transactions = []
            except json.JSONDecodeError:
                transactions = []
    else:
        transactions = []

    for t in transactions:
        if t.get("transfer_code") == transfer.transfer_code:
            raise AccountManagementException("Output JSON file already has that transfer")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(transactions + [transfer.to_json()], f, indent=4)  # type: ignore
    return f"Transfer Code: {transfer.transfer_code}"
