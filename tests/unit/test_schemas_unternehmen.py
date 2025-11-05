"""
Unit tests for Unternehmen Pydantic schemas.

Tests validation rules, field constraints, and schema transformations
for the Unternehmen schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.unternehmen import UnternehmenCreate, UnternehmenResponse, UnternehmenWithPersons
from app.schemas.person import PersonResponse
from app.utils.constants import BUNDESLAENDER


@pytest.mark.unit
class TestUnternehmenCreateSchema:
    """Test suite for UnternehmenCreate schema."""

    def test_valid_unternehmen_create(self, sample_unternehmen_data):
        """
        Test creating schema with valid data.

        Arrange: Valid company data
        Act: Create UnternehmenCreate schema
        Assert: Schema is created successfully with all fields
        """
        # Arrange & Act
        schema = UnternehmenCreate(**sample_unternehmen_data)

        # Assert
        assert schema.name == sample_unternehmen_data["name"]
        assert schema.bundesland == sample_unternehmen_data["bundesland"]
        assert schema.stadt == sample_unternehmen_data["stadt"]
        assert schema.plz == sample_unternehmen_data["plz"]
        assert schema.strasse == sample_unternehmen_data["strasse"]
        assert schema.hausnummer == sample_unternehmen_data["hausnummer"]
        assert schema.ansprechpartner_id is None

    def test_unternehmen_create_with_ansprechpartner_id(self, sample_unternehmen_data):
        """
        Test creating schema with ansprechpartner_id.

        Arrange: Company data with ansprechpartner_id
        Act: Create schema
        Assert: ansprechpartner_id is set correctly
        """
        # Arrange
        sample_unternehmen_data["ansprechpartner_id"] = 123

        # Act
        schema = UnternehmenCreate(**sample_unternehmen_data)

        # Assert
        assert schema.ansprechpartner_id == 123

    def test_invalid_plz_wrong_length_raises_validation_error(self, sample_unternehmen_data):
        """
        Test that PLZ with wrong length fails validation.

        Arrange: Company data with 4-digit PLZ
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["plz"] = "1234"  # Too short

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**sample_unternehmen_data)

        assert "plz" in str(exc_info.value)

    def test_invalid_plz_with_letters_raises_validation_error(self, sample_unternehmen_data):
        """
        Test that PLZ with letters fails validation.

        Arrange: Company data with non-numeric PLZ
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["plz"] = "80A31"  # Contains letter

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**sample_unternehmen_data)

        assert "plz" in str(exc_info.value)

    def test_invalid_plz_too_long_raises_validation_error(self, sample_unternehmen_data):
        """
        Test that PLZ with more than 5 digits fails validation.

        Arrange: Company data with 6-digit PLZ
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["plz"] = "803310"  # Too long

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**sample_unternehmen_data)

        assert "plz" in str(exc_info.value)

    def test_valid_plz_formats(self, sample_unternehmen_data):
        """
        Test various valid 5-digit PLZ formats.

        Arrange: Company data with different valid PLZs
        Act: Create schemas
        Assert: All are accepted
        """
        # Arrange
        valid_plzs = ["00000", "12345", "99999", "80331"]

        # Act & Assert
        for plz in valid_plzs:
            sample_unternehmen_data["plz"] = plz
            schema = UnternehmenCreate(**sample_unternehmen_data)
            assert schema.plz == plz

    def test_invalid_bundesland_raises_validation_error(self, sample_unternehmen_data):
        """
        Test that invalid Bundesland fails validation.

        Arrange: Company data with non-existent Bundesland
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["bundesland"] = "InvalidState"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**sample_unternehmen_data)

        error_dict = exc_info.value.errors()[0]
        assert error_dict["loc"] == ("bundesland",)
        assert "Ungültiges Bundesland" in error_dict["msg"]

    def test_all_valid_bundeslaender_accepted(self, sample_unternehmen_data):
        """
        Test that all 16 German Bundesländer are accepted.

        Arrange: Company data with each Bundesland
        Act: Create schemas
        Assert: All Bundesländer are accepted
        """
        # Arrange & Act & Assert
        for bundesland in BUNDESLAENDER:
            sample_unternehmen_data["bundesland"] = bundesland
            schema = UnternehmenCreate(**sample_unternehmen_data)
            assert schema.bundesland == bundesland

    def test_bundesland_case_sensitive(self, sample_unternehmen_data):
        """
        Test that Bundesland validation is case-sensitive.

        Arrange: Company data with lowercase Bundesland
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["bundesland"] = "bayern"  # lowercase

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**sample_unternehmen_data)

        assert "Ungültiges Bundesland" in str(exc_info.value)

    def test_missing_required_field_raises_validation_error(self):
        """
        Test that missing required field raises ValidationError.

        Arrange: Company data without 'name' field
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        incomplete_data = {
            "bundesland": "Bayern",
            "stadt": "München",
            "plz": "80331",
            "strasse": "Teststraße",
            "hausnummer": "1"
            # Missing 'name'
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UnternehmenCreate(**incomplete_data)

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "name" in field_names

    def test_empty_string_name_raises_validation_error(self, sample_unternehmen_data):
        """
        Test that empty string for name is rejected.

        Arrange: Company data with empty name
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_unternehmen_data["name"] = ""

        # Act & Assert
        with pytest.raises(ValidationError):
            UnternehmenCreate(**sample_unternehmen_data)

    def test_special_characters_in_fields(self, sample_unternehmen_data):
        """
        Test that special characters are accepted in string fields.

        Arrange: Company data with umlauts and special characters
        Act: Create schema
        Assert: Data is preserved correctly
        """
        # Arrange
        sample_unternehmen_data["name"] = "Müller & Söhne GmbH"
        sample_unternehmen_data["bundesland"] = "Baden-Württemberg"
        sample_unternehmen_data["stadt"] = "Köln"
        sample_unternehmen_data["strasse"] = "Große Straße"

        # Act
        schema = UnternehmenCreate(**sample_unternehmen_data)

        # Assert
        assert schema.name == "Müller & Söhne GmbH"
        assert schema.bundesland == "Baden-Württemberg"
        assert schema.stadt == "Köln"
        assert schema.strasse == "Große Straße"


@pytest.mark.unit
class TestUnternehmenResponseSchema:
    """Test suite for UnternehmenResponse schema."""

    def test_unternehmen_response_includes_id(self, sample_unternehmen_data):
        """
        Test that response schema includes id field.

        Arrange: Company data with id
        Act: Create UnternehmenResponse
        Assert: id is included
        """
        # Arrange
        data_with_id = {**sample_unternehmen_data, "id": 1}

        # Act
        schema = UnternehmenResponse(**data_with_id)

        # Assert
        assert schema.id == 1
        assert schema.name == sample_unternehmen_data["name"]

    def test_unternehmen_response_from_attributes(self, create_unternehmen, test_db):
        """
        Test creating response schema from ORM model.

        Arrange: Create Unternehmen ORM instance
        Act: Create schema from ORM model
        Assert: Schema contains correct data
        """
        # Arrange
        unternehmen = create_unternehmen(name="ORM Test GmbH")

        # Act
        schema = UnternehmenResponse.model_validate(unternehmen)

        # Assert
        assert schema.id == unternehmen.id
        assert schema.name == "ORM Test GmbH"
        assert schema.bundesland == unternehmen.bundesland


@pytest.mark.unit
class TestUnternehmenWithPersonsSchema:
    """Test suite for UnternehmenWithPersons schema."""

    def test_unternehmen_with_persons_empty_lists(self, sample_unternehmen_data):
        """
        Test schema with empty person lists.

        Arrange: Company data without persons
        Act: Create UnternehmenWithPersons schema
        Assert: Person lists are empty
        """
        # Arrange
        data = {**sample_unternehmen_data, "id": 1}

        # Act
        schema = UnternehmenWithPersons(**data)

        # Assert
        assert schema.personen == []
        assert schema.ansprechpartner is None

    def test_unternehmen_with_ansprechpartner(self, sample_unternehmen_data):
        """
        Test schema with Ansprechpartner.

        Arrange: Company data with Ansprechpartner
        Act: Create schema
        Assert: Ansprechpartner is included
        """
        # Arrange
        ansprechpartner_data = {
            "id": 1,
            "vorname": "Anna",
            "nachname": "Hauptkontakt",
            "email": "anna@test.de",
            "telefon": "123456",
            "funktion": "Mitarbeiter",
            "rolle": "Ansprechpartner",
            "firma_id": 1
        }
        data = {
            **sample_unternehmen_data,
            "id": 1,
            "ansprechpartner": ansprechpartner_data
        }

        # Act
        schema = UnternehmenWithPersons(**data)

        # Assert
        assert schema.ansprechpartner is not None
        assert schema.ansprechpartner.vorname == "Anna"
        assert schema.ansprechpartner.rolle == "Ansprechpartner"

    def test_unternehmen_with_multiple_personen(self, sample_unternehmen_data):
        """
        Test schema with multiple persons.

        Arrange: Company data with person list
        Act: Create schema
        Assert: All persons are included
        """
        # Arrange
        personen_data = [
            {
                "id": 1,
                "vorname": "Person1",
                "nachname": "Test",
                "funktion": "Mitarbeiter",
                "rolle": "Empfehler",
                "firma_id": 1
            },
            {
                "id": 2,
                "vorname": "Person2",
                "nachname": "Test",
                "funktion": "Mitarbeiter",
                "rolle": "Empfehler",
                "firma_id": 1
            }
        ]
        data = {
            **sample_unternehmen_data,
            "id": 1,
            "personen": personen_data
        }

        # Act
        schema = UnternehmenWithPersons(**data)

        # Assert
        assert len(schema.personen) == 2
        assert schema.personen[0].vorname == "Person1"
        assert schema.personen[1].vorname == "Person2"

    def test_unternehmen_with_persons_inherits_validation(self):
        """
        Test that UnternehmenWithPersons inherits validation from base schema.

        Arrange: Invalid company data (bad PLZ)
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        invalid_data = {
            "id": 1,
            "name": "Test GmbH",
            "bundesland": "Bayern",
            "stadt": "München",
            "plz": "123",  # Invalid
            "strasse": "Test",
            "hausnummer": "1"
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            UnternehmenWithPersons(**invalid_data)
