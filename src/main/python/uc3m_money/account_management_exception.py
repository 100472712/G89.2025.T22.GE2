"""Exception for the order_management module"""

class AccountManagementException(Exception):
    """Personalised exception for Accounts Management"""
    def __init__(self, message):
        self.__message = message
        super().__init__(self.message)

    @property
    def message(self):
        """gets the message value"""
        return self.__message
