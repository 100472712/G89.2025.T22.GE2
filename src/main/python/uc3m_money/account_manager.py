class AccountManager:
    @staticmethod
    def validate_iban(iban: str) -> bool:
        """
        Validate IBAN format for Spain (ES).
        - Must start with 'ES'
        - Must be 24 characters long
        - The remaining characters after 'ES' must be digits

        Args:
            iban (str): The IBAN string to be validated.

        Returns:
            bool: Returns True if the IBAN is valid, False otherwise.
        """
        # Check if the IBAN starts with 'ES', is 24 characters long, and contains only digits after 'ES'.
        if iban.startswith("ES") and len(iban) == 24 and iban[2:].isdigit():
            return True
        return False
