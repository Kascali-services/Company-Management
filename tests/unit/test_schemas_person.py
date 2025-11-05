"""
Unit tests for Person Pydantic schemas.

Tests validation rules for Person schemas including
rolle and funktion validation.
"""

import pytest
from pydantic import ValidationError

from app.schemas.person import PersonCreate, PersonResponse


@pytest.mark.unit
class TestPersonCreateSchema:
    """Test suite for PersonCreate schema."""

    def test_valid_person_create(self, sample_person_data):
        """
        Test creating schema with valid data.

        Arrange: Valid person data
        Act: Create PersonCreate schema
        Assert: Schema is created successfully
        """
        # Arrange & Act
        schema = PersonCreate(**sample_person_data)

        # Assert
        assert schema.vorname == sample_person_data["vorname"]
        assert schema.nachname == sample_person_data["nachname"]
        assert schema.email == sample_person_data["email"]
        assert schema.telefon == sample_person_data["telefon"]
        assert schema.funktion == sample_person_data["funktion"]
        assert schema.rolle == sample_person_data["rolle"]

    def test_person_create_with_empfehler_rolle(self):
        """
        Test creating person with Empfehler rolle.

        Arrange: Person data with rolle="Empfehler"
        Act: Create schema
        Assert: Rolle is accepted
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.rolle == "Empfehler"

    def test_person_create_with_ansprechpartner_rolle(self):
        """
        Test creating person with Ansprechpartner rolle.

        Arrange: Person data with rolle="Ansprechpartner"
        Act: Create schema
        Assert: Rolle is accepted
        """
        # Arrange
        data = {
            "vorname": "Anna",
            "nachname": "Hauptkontakt",
            "funktion": "Mitarbeiter",
            "rolle": "Ansprechpartner"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.rolle == "Ansprechpartner"

    def test_invalid_rolle_raises_validation_error(self, sample_person_data):
        """
        Test that invalid rolle fails validation.

        Arrange: Person data with invalid rolle
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_person_data["rolle"] = "InvalidRole"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**sample_person_data)

        error_dict = exc_info.value.errors()[0]
        assert error_dict["loc"] == ("rolle",)
        assert "Rolle muss Empfehler oder Ansprechpartner sein" in error_dict["msg"]

    def test_rolle_case_sensitive(self, sample_person_data):
        """
        Test that rolle validation is case-sensitive.

        Arrange: Person data with lowercase rolle
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_person_data["rolle"] = "empfehler"  # lowercase

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**sample_person_data)

        assert "Rolle muss Empfehler oder Ansprechpartner sein" in str(exc_info.value)

    def test_person_create_with_mitarbeiter_funktion(self):
        """
        Test creating person with Mitarbeiter funktion.

        Arrange: Person data with funktion="Mitarbeiter"
        Act: Create schema
        Assert: Funktion is accepted
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.funktion == "Mitarbeiter"

    def test_person_create_with_azubi_funktion(self):
        """
        Test creating person with Azubi funktion.

        Arrange: Person data with funktion="Azubi"
        Act: Create schema
        Assert: Funktion is accepted
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Azubi",
            "rolle": "Empfehler"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.funktion == "Azubi"

    def test_invalid_funktion_raises_validation_error(self, sample_person_data):
        """
        Test that invalid funktion fails validation.

        Arrange: Person data with invalid funktion
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_person_data["funktion"] = "Manager"  # Not Mitarbeiter or Azubi

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**sample_person_data)

        error_dict = exc_info.value.errors()[0]
        assert error_dict["loc"] == ("funktion",)
        assert "Funktion muss Mitarbeiter oder Azubi sein" in error_dict["msg"]

    def test_funktion_case_sensitive(self, sample_person_data):
        """
        Test that funktion validation is case-sensitive.

        Arrange: Person data with lowercase funktion
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_person_data["funktion"] = "mitarbeiter"  # lowercase

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**sample_person_data)

        assert "Funktion muss Mitarbeiter oder Azubi sein" in str(exc_info.value)

    def test_email_optional(self, sample_person_data):
        """
        Test that email field is optional.

        Arrange: Person data without email
        Act: Create schema
        Assert: Schema is created with email as None
        """
        # Arrange
        del sample_person_data["email"]

        # Act
        schema = PersonCreate(**sample_person_data)

        # Assert
        assert schema.email is None

    def test_telefon_optional(self, sample_person_data):
        """
        Test that telefon field is optional.

        Arrange: Person data without telefon
        Act: Create schema
        Assert: Schema is created with telefon as None
        """
        # Arrange
        del sample_person_data["telefon"]

        # Act
        schema = PersonCreate(**sample_person_data)

        # Assert
        assert schema.telefon is None

    def test_email_and_telefon_both_optional(self):
        """
        Test that both email and telefon can be omitted.

        Arrange: Person data without email and telefon
        Act: Create schema
        Assert: Schema is created successfully
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.email is None
        assert schema.telefon is None

    def test_missing_required_field_vorname_raises_error(self):
        """
        Test that missing vorname raises ValidationError.

        Arrange: Person data without vorname
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        data = {
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**data)

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "vorname" in field_names

    def test_missing_required_field_nachname_raises_error(self):
        """
        Test that missing nachname raises ValidationError.

        Arrange: Person data without nachname
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        data = {
            "vorname": "Max",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**data)

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "nachname" in field_names

    def test_missing_required_field_funktion_raises_error(self):
        """
        Test that missing funktion raises ValidationError.

        Arrange: Person data without funktion
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "rolle": "Empfehler"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**data)

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "funktion" in field_names

    def test_missing_required_field_rolle_raises_error(self):
        """
        Test that missing rolle raises ValidationError.

        Arrange: Person data without rolle
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(**data)

        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "rolle" in field_names

    def test_empty_string_vorname_raises_error(self, sample_person_data):
        """
        Test that empty string for vorname is rejected.

        Arrange: Person data with empty vorname
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        sample_person_data["vorname"] = ""

        # Act & Assert
        with pytest.raises(ValidationError):
            PersonCreate(**sample_person_data)

    def test_special_characters_in_names(self):
        """
        Test that special characters (umlauts, hyphens) are accepted.

        Arrange: Person data with special characters
        Act: Create schema
        Assert: Data is preserved correctly
        """
        # Arrange
        data = {
            "vorname": "Müller",
            "nachname": "Größmann-Öztürk",
            "email": "müller@example.de",
            "telefon": "+49 (0)89 123-456",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.vorname == "Müller"
        assert schema.nachname == "Größmann-Öztürk"
        assert schema.email == "müller@example.de"
        assert schema.telefon == "+49 (0)89 123-456"

    def test_combination_ansprechpartner_azubi(self):
        """
        Test creating Ansprechpartner with Azubi funktion.

        Arrange: Person data with Ansprechpartner rolle and Azubi funktion
        Act: Create schema
        Assert: Schema is created successfully
        """
        # Arrange
        data = {
            "vorname": "Young",
            "nachname": "Trainee",
            "funktion": "Azubi",
            "rolle": "Ansprechpartner"
        }

        # Act
        schema = PersonCreate(**data)

        # Assert
        assert schema.funktion == "Azubi"
        assert schema.rolle == "Ansprechpartner"


@pytest.mark.unit
class TestPersonResponseSchema:
    """Test suite for PersonResponse schema."""

    def test_person_response_includes_id_and_firma_id(self, sample_person_data):
        """
        Test that response schema includes id and firma_id.

        Arrange: Person data with id and firma_id
        Act: Create PersonResponse
        Assert: Both fields are included
        """
        # Arrange
        data_with_ids = {**sample_person_data, "id": 1, "firma_id": 42}

        # Act
        schema = PersonResponse(**data_with_ids)

        # Assert
        assert schema.id == 1
        assert schema.firma_id == 42
        assert schema.vorname == sample_person_data["vorname"]

    def test_person_response_from_attributes(self, create_unternehmen, create_person, test_db):
        """
        Test creating response schema from ORM model.

        Arrange: Create Person ORM instance
        Act: Create schema from ORM model
        Assert: Schema contains correct data
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            vorname="ORM",
            nachname="Test"
        )

        # Act
        schema = PersonResponse.model_validate(person)

        # Assert
        assert schema.id == person.id
        assert schema.firma_id == unternehmen.id
        assert schema.vorname == "ORM"
        assert schema.nachname == "Test"

    def test_person_response_inherits_validation(self):
        """
        Test that PersonResponse inherits validation from PersonCreate.

        Arrange: Invalid person data (bad rolle)
        Act: Attempt to create schema
        Assert: ValidationError is raised
        """
        # Arrange
        invalid_data = {
            "id": 1,
            "firma_id": 1,
            "vorname": "Test",
            "nachname": "Person",
            "funktion": "Mitarbeiter",
            "rolle": "InvalidRole"  # Invalid
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            PersonResponse(**invalid_data)
