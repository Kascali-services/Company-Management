"""
Centralized error messages and codes for the application.

This module provides a single source of truth for all error messages,
making it easier to maintain consistency and support internationalization.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for application errors."""

    # Validation Errors
    INVALID_BUNDESLAND = "INVALID_BUNDESLAND"
    INVALID_FUNKTION = "INVALID_FUNKTION"
    INVALID_ROLLE = "INVALID_ROLLE"
    INVALID_PLZ = "INVALID_PLZ"

    # Not Found Errors
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"

    # Business Logic Errors
    INVALID_CONTACT_PERSON = "INVALID_CONTACT_PERSON"
    CONTACT_PERSON_EXISTS = "CONTACT_PERSON_EXISTS"
    CONTACT_PERSON_REQUIRED_ROLE = "CONTACT_PERSON_REQUIRED_ROLE"


class ErrorMessage:
    """Centralized error messages for the application."""

    # Validation error messages
    INVALID_BUNDESLAND = "Invalid federal state: must be one of the 16 German states"
    INVALID_FUNKTION = "Function must be either Mitarbeiter (employee) or Azubi (trainee)"
    INVALID_ROLLE = "Role must be either Empfehler (referrer) or Ansprechpartner (contact person)"
    INVALID_PLZ = "Postal code must be exactly 5 digits"

    # Not found error messages
    COMPANY_NOT_FOUND = "Company not found"
    PERSON_NOT_FOUND = "Person not found"

    # Business logic error messages
    INVALID_CONTACT_PERSON = "Invalid contact person: must have Ansprechpartner role"
    CONTACT_PERSON_EXISTS = "Company already has a contact person"
    CONTACT_PERSON_REQUIRED_ROLE = "Contact person must have Ansprechpartner role"

    # Success messages
    PERSON_DELETED = "Person deleted successfully"


# HTTP Status codes mapping
ERROR_STATUS_CODES = {
    ErrorCode.COMPANY_NOT_FOUND: 404,
    ErrorCode.PERSON_NOT_FOUND: 404,
    ErrorCode.INVALID_CONTACT_PERSON: 400,
    ErrorCode.CONTACT_PERSON_EXISTS: 400,
    ErrorCode.CONTACT_PERSON_REQUIRED_ROLE: 400,
}


def get_error_message(error_code: ErrorCode) -> str:
    """
    Get the error message for a given error code.

    Args:
        error_code: The error code enum

    Returns:
        The corresponding error message

    Raises:
        ValueError: If error code is not recognized
    """
    try:
        return getattr(ErrorMessage, error_code.name)
    except AttributeError:
        raise ValueError(f"Unknown error code: {error_code}")


def get_status_code(error_code: ErrorCode, default: int = 400) -> int:
    """
    Get the HTTP status code for a given error code.

    Args:
        error_code: The error code enum
        default: Default status code if not found (default: 400)

    Returns:
        The corresponding HTTP status code
    """
    return ERROR_STATUS_CODES.get(error_code, default)
