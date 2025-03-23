"""Module for function 3 where we receive an incoming json file with transactions, and
we must verify the validity of IBAN, if we have it and then create the new balance."""

import json
import os
from datetime import date
from transfer_request import valid_iban


# Steps to take:

# 1. Validate input data
#    1.1 We will use the already created function.
#    1.2 If not then error
# 2. Search for the incoming iban in json file.
# 3. If exists we aggregate associated movements.
#    3.1 if not found error.
# 4. If no error has been raised save date (IBAN + date + balance)
#    to a file account_balances.json as said in statement.




class AccountManagementException(Exception):
    """Exceptions raised in case there is an error."""

class IncomingTransactions:
    """Class representing a transfer being processed."""
    def __init__(self, iban: str, amount: str):
        """Initializer for our class attributes."""
        self.__iban = iban
        self.__amount = amount

    def __str__(self):
        """Method to return our whole transfer"""
        return "Transfer:" + json.dumps(self.__dict__)

    def to_json(self):
        """Returns our class object into json format"""
        return {
            "iban": self.__iban,
            "amount":  self.__amount,
        }

def in_json_file_check(iban:str) -> bool:
    """Here we check the json file of all_transactions.json and check this transaction is there."""
    #First we have to load or json file, knowing it is just one directory away
    path = "../../all_transactions.json"
    if os.path.exists(path) is not True:
        raise AccountManagementException("AllTransactions file not found")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

# We iterate through our file to check if there is
# at least an instance of the iban
    for key in data:
        if key.iban == iban:
            return True
    return False


def correct_iban(iban: str) -> bool:
    """Here we do steps 1 and 2."""
    if valid_iban(iban, check_spanish=True) is not True:
        raise AccountManagementException("Not a valid IBAN")
    if in_json_file_check(iban): #Our json file is all_transactions.json
        raise AccountManagementException("Transaction not stored")
    return True


def aggregate_movements(iban: str) -> float:
    """Here we do step 3."""

    if correct_iban(iban) is not True:
        raise AccountManagementException("The IBAN is not valid")

    path = "../../all_transactions.json"
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

# We iterate through our file to check if it is
# our iban, and we add the balance
    amount = 0
    for key in data:
        if key.iban == iban:
            amount = amount + key.amount
    return amount

def store_new_balance(iban: str) -> bool:
    """Here we do step 4."""
    balance = aggregate_movements(iban)
    path = "../../account_balances.json"

#   We create our new json instance with:
#        1. The IBAN
#        2. The total amount(balance)
#        3. Current date stamp

    if os.path.exists(path) is not True:
        raise AccountManagementException("JsonFile to store balances doesn't exist")

    new_account_balance = {
        "iban": iban,
        "amount": balance,
        "date": date.today().isoformat()
    }

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data.append(new_account_balance)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4) #type: ignore

    return True
