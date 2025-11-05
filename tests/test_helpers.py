"""
Test helper utilities and factory functions.

This module provides utility functions for generating test data,
assertions, and common test operations.
"""

from typing import Dict, Any, List
from app.utils.constants import BUNDESLAENDER


class UnternehmenFactory:
    """Factory for creating test Unternehmen data."""

    @staticmethod
    def build(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build a dictionary with valid Unternehmen data.

        Args:
            overrides: Optional dictionary to override default values

        Returns:
            Dictionary with Unternehmen data
        """
        data = {
            "name": "Test Firma GmbH",
            "bundesland": "Bayern",
            "stadt": "München",
            "plz": "80331",
            "strasse": "Teststraße",
            "hausnummer": "42"
        }
        if overrides:
            data.update(overrides)
        return data

    @staticmethod
    def build_batch(count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Build multiple Unternehmen data dictionaries.

        Args:
            count: Number of companies to create
            **kwargs: Optional overrides for all companies

        Returns:
            List of Unternehmen data dictionaries
        """
        bundeslaender_cycle = BUNDESLAENDER * ((count // len(BUNDESLAENDER)) + 1)
        companies = []

        for i in range(count):
            data = {
                "name": f"Firma {i + 1} GmbH",
                "bundesland": bundeslaender_cycle[i],
                "stadt": f"Stadt{i + 1}",
                "plz": f"{80000 + i:05d}",
                "strasse": f"Straße {i + 1}",
                "hausnummer": f"{i + 1}"
            }
            data.update(kwargs)
            companies.append(data)

        return companies


class PersonFactory:
    """Factory for creating test Person data."""

    @staticmethod
    def build(rolle: str = "Empfehler", overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build a dictionary with valid Person data.

        Args:
            rolle: Role of the person (Empfehler or Ansprechpartner)
            overrides: Optional dictionary to override default values

        Returns:
            Dictionary with Person data
        """
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "max.mustermann@example.com",
            "telefon": "089 12345678",
            "funktion": "Mitarbeiter",
            "rolle": rolle
        }
        if overrides:
            data.update(overrides)
        return data

    @staticmethod
    def build_ansprechpartner(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build data for an Ansprechpartner.

        Args:
            overrides: Optional dictionary to override default values

        Returns:
            Dictionary with Ansprechpartner data
        """
        data = {
            "vorname": "Anna",
            "nachname": "Hauptkontakt",
            "email": "anna.hauptkontakt@example.com",
            "telefon": "089 87654321",
            "funktion": "Mitarbeiter",
            "rolle": "Ansprechpartner"
        }
        if overrides:
            data.update(overrides)
        return data

    @staticmethod
    def build_empfehler(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build data for an Empfehler.

        Args:
            overrides: Optional dictionary to override default values

        Returns:
            Dictionary with Empfehler data
        """
        data = {
            "vorname": "Thomas",
            "nachname": "Empfehlung",
            "email": "thomas.empfehlung@example.com",
            "telefon": "089 11223344",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }
        if overrides:
            data.update(overrides)
        return data


def assert_unternehmen_equal(actual: Dict[str, Any], expected: Dict[str, Any], exclude_fields: List[str] = None):
    """
    Assert that two Unternehmen dictionaries are equal.

    Args:
        actual: Actual Unternehmen data
        expected: Expected Unternehmen data
        exclude_fields: List of field names to exclude from comparison
    """
    exclude = exclude_fields or []
    for key, value in expected.items():
        if key not in exclude:
            assert actual.get(key) == value, f"Field '{key}' mismatch: {actual.get(key)} != {value}"


def assert_person_equal(actual: Dict[str, Any], expected: Dict[str, Any], exclude_fields: List[str] = None):
    """
    Assert that two Person dictionaries are equal.

    Args:
        actual: Actual Person data
        expected: Expected Person data
        exclude_fields: List of field names to exclude from comparison
    """
    exclude = exclude_fields or []
    for key, value in expected.items():
        if key not in exclude:
            assert actual.get(key) == value, f"Field '{key}' mismatch: {actual.get(key)} != {value}"


def assert_response_status(response, expected_status: int, message: str = None):
    """
    Assert that a response has the expected status code.

    Args:
        response: FastAPI response object
        expected_status: Expected HTTP status code
        message: Optional custom error message
    """
    msg = message or f"Expected status {expected_status}, got {response.status_code}"
    if response.status_code != expected_status:
        print(f"Response body: {response.text}")
    assert response.status_code == expected_status, msg


def assert_validation_error(response, field_name: str = None):
    """
    Assert that a response contains a validation error.

    Args:
        response: FastAPI response object
        field_name: Optional field name that should have an error
    """
    assert response.status_code == 422, f"Expected 422 validation error, got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Response should contain 'detail' field"

    if field_name:
        errors = data["detail"]
        field_errors = [e for e in errors if field_name in str(e.get("loc", []))]
        assert len(field_errors) > 0, f"No validation error found for field '{field_name}'"
