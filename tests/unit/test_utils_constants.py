"""
Unit tests for utils constants module.

Tests the BUNDESLAENDER constant for correctness and completeness.
"""

import pytest

from app.utils.constants import BUNDESLAENDER


@pytest.mark.unit
class TestBundeslaenderConstant:
    """Test suite for BUNDESLAENDER constant."""

    def test_bundeslaender_is_list(self):
        """
        Test that BUNDESLAENDER is a list.

        Arrange: Import BUNDESLAENDER
        Act: Check type
        Assert: Is a list
        """
        # Arrange & Act & Assert
        assert isinstance(BUNDESLAENDER, list)

    def test_bundeslaender_has_16_states(self):
        """
        Test that BUNDESLAENDER contains exactly 16 German states.

        Arrange: Import BUNDESLAENDER
        Act: Count elements
        Assert: Contains 16 elements
        """
        # Arrange & Act & Assert
        assert len(BUNDESLAENDER) == 16

    def test_bundeslaender_contains_expected_states(self):
        """
        Test that all 16 German federal states are present.

        Arrange: Define expected states
        Act: Check each state is in BUNDESLAENDER
        Assert: All states are present
        """
        # Arrange
        expected_states = [
            'Baden-Württemberg',
            'Bayern',
            'Berlin',
            'Brandenburg',
            'Bremen',
            'Hamburg',
            'Hessen',
            'Mecklenburg-Vorpommern',
            'Niedersachsen',
            'Nordrhein-Westfalen',
            'Rheinland-Pfalz',
            'Saarland',
            'Sachsen',
            'Sachsen-Anhalt',
            'Schleswig-Holstein',
            'Thüringen'
        ]

        # Act & Assert
        for state in expected_states:
            assert state in BUNDESLAENDER, f"{state} is missing from BUNDESLAENDER"

    def test_bundeslaender_no_duplicates(self):
        """
        Test that BUNDESLAENDER contains no duplicate entries.

        Arrange: Import BUNDESLAENDER
        Act: Compare length with set length
        Assert: No duplicates exist
        """
        # Arrange & Act & Assert
        assert len(BUNDESLAENDER) == len(set(BUNDESLAENDER))

    def test_bundeslaender_all_strings(self):
        """
        Test that all entries in BUNDESLAENDER are strings.

        Arrange: Import BUNDESLAENDER
        Act: Check type of each entry
        Assert: All are strings
        """
        # Arrange & Act & Assert
        for state in BUNDESLAENDER:
            assert isinstance(state, str)

    def test_bundeslaender_no_empty_strings(self):
        """
        Test that BUNDESLAENDER contains no empty strings.

        Arrange: Import BUNDESLAENDER
        Act: Check each entry
        Assert: No empty strings
        """
        # Arrange & Act & Assert
        for state in BUNDESLAENDER:
            assert len(state) > 0

    def test_bundeslaender_correct_capitalization(self):
        """
        Test that state names use proper German capitalization.

        Arrange: Import BUNDESLAENDER
        Act: Check capitalization
        Assert: Each state starts with capital letter
        """
        # Arrange & Act & Assert
        for state in BUNDESLAENDER:
            # First letter should be capitalized
            assert state[0].isupper(), f"{state} should start with capital letter"

    def test_specific_state_bayern_exists(self):
        """
        Test that Bayern (Bavaria) is in the list.

        Arrange: Import BUNDESLAENDER
        Act: Check for 'Bayern'
        Assert: Bayern is present
        """
        # Arrange & Act & Assert
        assert 'Bayern' in BUNDESLAENDER

    def test_specific_state_berlin_exists(self):
        """
        Test that Berlin is in the list.

        Arrange: Import BUNDESLAENDER
        Act: Check for 'Berlin'
        Assert: Berlin is present
        """
        # Arrange & Act & Assert
        assert 'Berlin' in BUNDESLAENDER

    def test_specific_state_nordrhein_westfalen_exists(self):
        """
        Test that Nordrhein-Westfalen (with hyphen) is in the list.

        Arrange: Import BUNDESLAENDER
        Act: Check for 'Nordrhein-Westfalen'
        Assert: Nordrhein-Westfalen is present with correct hyphenation
        """
        # Arrange & Act & Assert
        assert 'Nordrhein-Westfalen' in BUNDESLAENDER

    def test_specific_state_baden_wuerttemberg_exists(self):
        """
        Test that Baden-Württemberg (with umlaut) is in the list.

        Arrange: Import BUNDESLAENDER
        Act: Check for 'Baden-Württemberg'
        Assert: Baden-Württemberg is present with correct umlaut
        """
        # Arrange & Act & Assert
        assert 'Baden-Württemberg' in BUNDESLAENDER

    def test_specific_state_thueringen_exists(self):
        """
        Test that Thüringen (with umlaut) is in the list.

        Arrange: Import BUNDESLAENDER
        Act: Check for 'Thüringen'
        Assert: Thüringen is present with correct umlaut
        """
        # Arrange & Act & Assert
        assert 'Thüringen' in BUNDESLAENDER

    def test_bundeslaender_order_preserves_original(self):
        """
        Test that BUNDESLAENDER maintains a consistent order.

        Arrange: Import BUNDESLAENDER
        Act: Check first and last elements
        Assert: Order is as defined
        """
        # Arrange & Act & Assert
        assert BUNDESLAENDER[0] == 'Baden-Württemberg'
        assert BUNDESLAENDER[-1] == 'Thüringen'

    def test_bundeslaender_contains_city_states(self):
        """
        Test that all three city-states are present.

        Arrange: Define city-states
        Act: Check presence
        Assert: Berlin, Bremen, Hamburg are all present
        """
        # Arrange
        city_states = ['Berlin', 'Bremen', 'Hamburg']

        # Act & Assert
        for city_state in city_states:
            assert city_state in BUNDESLAENDER

    def test_bundeslaender_immutable_reference(self):
        """
        Test that BUNDESLAENDER can be used as reference list.

        Arrange: Import BUNDESLAENDER
        Act: Create a copy and compare
        Assert: Original remains unchanged
        """
        # Arrange
        original_length = len(BUNDESLAENDER)
        first_element = BUNDESLAENDER[0]

        # Act
        copy = BUNDESLAENDER.copy()

        # Assert
        assert len(BUNDESLAENDER) == original_length
        assert BUNDESLAENDER[0] == first_element
        assert copy == BUNDESLAENDER
