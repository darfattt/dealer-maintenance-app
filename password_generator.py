"""
Password Generator for Dealer Management System

A standalone password generator that creates secure passwords meeting
the authentication requirements of the dealer management system.

Requirements based on auth_controller.py and user schemas:
- Minimum 8 characters, maximum 100 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Compatible with bcrypt hashing
"""

import secrets
import string
import re
import sys
import os
import argparse
from typing import Optional, List, Tuple


# Try to import auth utilities, fallback to bcrypt directly
AUTH_AVAILABLE = False
hash_password_func = None

# First try to import from the microservices utils
try:
    utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend-microservices', 'utils'))
    if utils_path not in sys.path:
        sys.path.append(utils_path)

    # Import required modules for auth.py
    import bcrypt
    from passlib.context import CryptContext

    # Create a simplified version of the auth functionality
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password_func(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    AUTH_AVAILABLE = True

except ImportError:
    # Fallback to direct bcrypt usage
    try:
        import bcrypt

        def hash_password_func(password: str) -> str:
            """Hash password using bcrypt directly"""
            # Generate salt and hash the password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')

        AUTH_AVAILABLE = True

    except ImportError:
        AUTH_AVAILABLE = False


class PasswordGenerator:
    """Generates secure passwords meeting system requirements"""

    def __init__(
        self,
        length: int = 12,
        include_special: bool = True,
        exclude_ambiguous: bool = True
    ):
        """
        Initialize password generator

        Args:
            length: Password length (8-100, default 12)
            include_special: Include special characters (!@#$%^&*)
            exclude_ambiguous: Exclude similar characters (0O, 1lI, etc.)
        """
        if length < 8 or length > 100:
            raise ValueError("Password length must be between 8 and 100 characters")

        self.length = length
        self.include_special = include_special
        self.exclude_ambiguous = exclude_ambiguous

        # Define character sets
        self.uppercase = string.ascii_uppercase
        self.lowercase = string.ascii_lowercase
        self.digits = string.digits
        self.special_chars = "!@#$%^&*"

        # Remove ambiguous characters if requested
        if exclude_ambiguous:
            # Remove: 0 (zero), O (capital o), 1 (one), l (lowercase L), I (capital i)
            self.uppercase = self.uppercase.replace('O', '').replace('I', '')
            self.lowercase = self.lowercase.replace('l', '')
            self.digits = self.digits.replace('0', '').replace('1', '')

    def generate(self) -> str:
        """
        Generate a secure password

        Returns:
            String password meeting all requirements
        """
        # Ensure we have at least one character from each required category
        password_chars = [
            secrets.choice(self.uppercase),  # At least one uppercase
            secrets.choice(self.lowercase),  # At least one lowercase
            secrets.choice(self.digits),     # At least one digit
        ]

        # Build the character pool for remaining positions
        char_pool = self.uppercase + self.lowercase + self.digits
        if self.include_special:
            char_pool += self.special_chars
            # Add a special character to guarantee inclusion if enabled
            password_chars.append(secrets.choice(self.special_chars))

        # Fill remaining positions
        remaining_length = self.length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(char_pool))

        # Shuffle the password to randomize position of required characters
        secrets.SystemRandom().shuffle(password_chars)

        password = ''.join(password_chars)

        # Validate the generated password
        if not self.validate_password(password):
            # If validation fails, try again (recursive with max attempts)
            return self.generate()

        return password

    def generate_multiple(self, count: int) -> List[str]:
        """
        Generate multiple passwords

        Args:
            count: Number of passwords to generate

        Returns:
            List of generated passwords
        """
        return [self.generate() for _ in range(count)]

    def generate_with_hash(self) -> Tuple[str, str]:
        """
        Generate password and its bcrypt hash

        Note: This method requires passlib to be installed.
        For standalone use without dependencies, use generate() only.

        Returns:
            Tuple of (plain_password, hashed_password)
        """
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            password = self.generate()
            hashed = pwd_context.hash(password)
            return password, hashed
        except ImportError:
            print("Warning: passlib not installed. Returning plain password only.")
            password = self.generate()
            return password, f"[HASH_UNAVAILABLE] {password}"

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate password against system requirements

        Args:
            password: Password to validate

        Returns:
            True if password meets all requirements
        """
        if len(password) < 8 or len(password) > 100:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def test_password_strength(self, password: str) -> dict:
        """
        Test and analyze password strength

        Args:
            password: Password to analyze

        Returns:
            Dictionary with strength analysis
        """
        analysis = {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            'meets_requirements': self.validate_password(password)
        }

        # Calculate strength score
        score = 0
        score += min(password.__len__() // 2, 10)  # Length bonus (max 10)
        score += 5 if analysis['has_uppercase'] else 0
        score += 5 if analysis['has_lowercase'] else 0
        score += 5 if analysis['has_digit'] else 0
        score += 10 if analysis['has_special'] else 0

        analysis['strength_score'] = score
        analysis['strength_level'] = (
            'Very Strong' if score >= 30 else
            'Strong' if score >= 25 else
            'Medium' if score >= 20 else
            'Weak'
        )

        return analysis

    def hash_input_password(self, password: str) -> Tuple[str, str, bool]:
        """
        Hash an input password using the system's auth utilities

        Args:
            password: Password to hash

        Returns:
            Tuple of (password, hashed_password, is_valid)
        """
        is_valid = self.validate_password(password)

        if not AUTH_AVAILABLE:
            return password, "[AUTH_UNAVAILABLE] Cannot hash without auth utilities", is_valid

        try:
            hashed = hash_password_func(password)
            return password, hashed, is_valid
        except Exception as e:
            return password, f"[HASH_ERROR] {str(e)}", is_valid

    @staticmethod
    def hash_single_password(password: str) -> None:
        """
        Static method to hash a single password and print results

        Args:
            password: Password to hash
        """
        generator = PasswordGenerator()
        plain, hashed, is_valid = generator.hash_input_password(password)

        print(hashed)


def main():
    """Main function for standalone usage"""
    parser = argparse.ArgumentParser(
        description='Password Generator for Dealer Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python password_generator.py                    # Generate sample passwords
  python password_generator.py -hp -p "Admin123!"  # Hash a specific password
  python password_generator.py --hash-password --password "MyPassword123"
        """
    )

    parser.add_argument(
        '-hp', '--hash-password',
        action='store_true',
        help='Hash a provided password using the auth system'
    )

    parser.add_argument(
        '-p', '--password',
        type=str,
        help='Password to hash (use with --hash-password)'
    )

    args = parser.parse_args()

    # Handle password hashing mode
    if args.hash_password:
        if not args.password:
            print("Error: --password is required when using --hash-password")
            print("Example: python password_generator.py -hp -p \"Admin123!\"")
            return

        PasswordGenerator.hash_single_password(args.password)
        return

    # Default mode: generate sample passwords
    # print("=== Password Generator for Dealer Management System ===\n")

    # # Create different generator configurations
    # generators = {
    #     'Standard (12 chars, special chars)': PasswordGenerator(12, True, True),
    #     'Simple (8 chars, no special)': PasswordGenerator(8, False, True),
    #     'Strong (16 chars, special chars)': PasswordGenerator(16, True, True),
    #     'No ambiguous chars': PasswordGenerator(12, True, True),
    # }

    # for name, generator in generators.items():
    #     print(f"--- {name} ---")
    #     password = generator.generate()
    #     analysis = generator.test_password_strength(password)

    #     print(f"Generated: {password}")
    #     print(f"Length: {analysis['length']}")
    #     print(f"Uppercase: {'✓' if analysis['has_uppercase'] else '✗'}")
    #     print(f"Lowercase: {'✓' if analysis['has_lowercase'] else '✗'}")
    #     print(f"Digit: {'✓' if analysis['has_digit'] else '✗'}")
    #     print(f"Special: {'✓' if analysis['has_special'] else '✗'}")
    #     print(f"Meets Requirements: {'✓' if analysis['meets_requirements'] else '✗'}")
    #     print(f"Strength: {analysis['strength_level']} ({analysis['strength_score']}/35)")
    #     print()

    # # Generate multiple passwords
    # print("--- Multiple Password Generation ---")
    # standard_gen = PasswordGenerator()
    # passwords = standard_gen.generate_multiple(5)
    # for i, pwd in enumerate(passwords, 1):
    #     print(f"{i}. {pwd}")

    # print("\n--- Testing Custom Password ---")
    # test_passwords = [
    #     "password123",      # Should fail (no uppercase)
    #     "Password123",      # Should pass
    #     "Pass123!",         # Should pass
    #     "abc",              # Should fail (too short)
    #     "Admin123!",     # Should pass
    # ]

    # for test_pwd in test_passwords:
    #     valid = PasswordGenerator.validate_password(test_pwd)
    #     print(f"'{test_pwd}' -> {'Valid' if valid else 'Invalid'}")


if __name__ == "__main__":
    main()