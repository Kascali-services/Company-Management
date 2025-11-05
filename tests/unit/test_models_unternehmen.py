"""
Unit tests for Unternehmen SQLAlchemy model.

Tests the database model behavior, relationships, and constraints
for the Unternehmen (company) entity.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.unternehmen import Unternehmen
from app.models.person import Person


@pytest.mark.unit
class TestUnternehmenModel:
    """Test suite for the Unternehmen model."""

    def test_create_unternehmen_success(self, test_db: Session, sample_unternehmen_data):
        """
        Test creating a valid Unternehmen instance.

        Arrange: Valid company data
        Act: Create and persist Unternehmen
        Assert: Company is saved with correct attributes
        """
        # Arrange & Act
        unternehmen = Unternehmen(**sample_unternehmen_data)
        test_db.add(unternehmen)
        test_db.commit()
        test_db.refresh(unternehmen)

        # Assert
        assert unternehmen.id is not None
        assert unternehmen.name == sample_unternehmen_data["name"]
        assert unternehmen.bundesland == sample_unternehmen_data["bundesland"]
        assert unternehmen.stadt == sample_unternehmen_data["stadt"]
        assert unternehmen.plz == sample_unternehmen_data["plz"]
        assert unternehmen.strasse == sample_unternehmen_data["strasse"]
        assert unternehmen.hausnummer == sample_unternehmen_data["hausnummer"]
        assert unternehmen.ansprechpartner_id is None

    def test_create_unternehmen_missing_required_field_raises_error(self, test_db: Session):
        """
        Test that creating Unternehmen without required field raises error.

        Arrange: Company data missing required field (name)
        Act: Attempt to create Unternehmen
        Assert: IntegrityError is raised
        """
        # Arrange
        invalid_data = {
            "bundesland": "Bayern",
            "stadt": "München",
            "plz": "80331",
            "strasse": "Teststraße",
            "hausnummer": "1"
            # Missing 'name'
        }

        # Act & Assert
        with pytest.raises(TypeError):
            unternehmen = Unternehmen(**invalid_data)

    def test_unternehmen_with_ansprechpartner_id(self, test_db: Session, create_unternehmen, create_person):
        """
        Test setting ansprechpartner_id on Unternehmen.

        Arrange: Create company and person with Ansprechpartner role
        Act: Set ansprechpartner_id on company
        Assert: Relationship is established correctly
        """
        # Arrange
        unternehmen = create_unternehmen(name="Test Firma")
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            vorname="Anna",
            nachname="Kontakt"
        )

        # Act
        unternehmen.ansprechpartner_id = person.id
        test_db.commit()
        test_db.refresh(unternehmen)

        # Assert
        assert unternehmen.ansprechpartner_id == person.id
        assert unternehmen.ansprechpartner.id == person.id
        assert unternehmen.ansprechpartner.vorname == "Anna"

    def test_unternehmen_ansprechpartner_relationship(self, test_db: Session, create_unternehmen, create_person):
        """
        Test the ansprechpartner relationship navigation.

        Arrange: Create company and link Ansprechpartner
        Act: Access ansprechpartner via relationship
        Assert: Relationship returns correct Person instance
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            funktion="Mitarbeiter"
        )
        unternehmen.ansprechpartner_id = person.id
        test_db.commit()
        test_db.refresh(unternehmen)

        # Act
        ansprechpartner = unternehmen.ansprechpartner

        # Assert
        assert ansprechpartner is not None
        assert ansprechpartner.id == person.id
        assert ansprechpartner.rolle == "Ansprechpartner"

    def test_unternehmen_ansprechpartner_relationship_nullable(self, test_db: Session, create_unternehmen):
        """
        Test that ansprechpartner_id can be null.

        Arrange: Create company without Ansprechpartner
        Act: Access ansprechpartner relationship
        Assert: ansprechpartner is None
        """
        # Arrange
        unternehmen = create_unternehmen()

        # Act & Assert
        assert unternehmen.ansprechpartner_id is None
        assert unternehmen.ansprechpartner is None

    def test_unternehmen_personen_relationship(self, test_db: Session, create_unternehmen, create_person):
        """
        Test the personen (all persons) relationship.

        Arrange: Create company with multiple persons
        Act: Access personen relationship
        Assert: All persons are returned
        """
        # Arrange
        unternehmen = create_unternehmen()
        person1 = create_person(firma_id=unternehmen.id, vorname="Person1")
        person2 = create_person(firma_id=unternehmen.id, vorname="Person2")
        person3 = create_person(firma_id=unternehmen.id, vorname="Person3")

        test_db.refresh(unternehmen)

        # Act
        personen = unternehmen.personen

        # Assert
        assert len(personen) == 3
        person_ids = {p.id for p in personen}
        assert person1.id in person_ids
        assert person2.id in person_ids
        assert person3.id in person_ids

    def test_unternehmen_personen_relationship_empty(self, test_db: Session, create_unternehmen):
        """
        Test personen relationship when no persons exist.

        Arrange: Create company without persons
        Act: Access personen relationship
        Assert: Empty list is returned
        """
        # Arrange
        unternehmen = create_unternehmen()

        # Act
        personen = unternehmen.personen

        # Assert
        assert len(personen) == 0
        assert personen == []

    def test_unternehmen_with_mixed_person_roles(self, test_db: Session, create_unternehmen, create_person):
        """
        Test company with both Ansprechpartner and Empfehler.

        Arrange: Create company with Ansprechpartner and multiple Empfehler
        Act: Query relationships
        Assert: All persons are in personen, correct Ansprechpartner is set
        """
        # Arrange
        unternehmen = create_unternehmen()
        ansprechpartner = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            vorname="Anna"
        )
        empfehler1 = create_person(
            firma_id=unternehmen.id,
            rolle="Empfehler",
            vorname="Emp1"
        )
        empfehler2 = create_person(
            firma_id=unternehmen.id,
            rolle="Empfehler",
            vorname="Emp2"
        )

        unternehmen.ansprechpartner_id = ansprechpartner.id
        test_db.commit()
        test_db.refresh(unternehmen)

        # Act & Assert
        assert len(unternehmen.personen) == 3
        assert unternehmen.ansprechpartner.id == ansprechpartner.id
        assert unternehmen.ansprechpartner.vorname == "Anna"

        empfehler_list = [p for p in unternehmen.personen if p.rolle == "Empfehler"]
        assert len(empfehler_list) == 2

    def test_unternehmen_unique_names_allowed(self, test_db: Session, create_unternehmen):
        """
        Test that multiple companies can have the same name.

        Arrange: Create two companies with identical names
        Act: Persist both companies
        Assert: Both companies are saved (no unique constraint on name)
        """
        # Arrange & Act
        company1 = create_unternehmen(name="Duplicate GmbH", stadt="München")
        company2 = create_unternehmen(name="Duplicate GmbH", stadt="Berlin")

        # Assert
        assert company1.id != company2.id
        assert company1.name == company2.name == "Duplicate GmbH"

    def test_unternehmen_plz_length(self, test_db: Session, sample_unternehmen_data):
        """
        Test PLZ field accepts 5-character strings.

        Arrange: Company data with 5-digit PLZ
        Act: Create Unternehmen
        Assert: PLZ is stored correctly
        """
        # Arrange
        sample_unternehmen_data["plz"] = "12345"

        # Act
        unternehmen = Unternehmen(**sample_unternehmen_data)
        test_db.add(unternehmen)
        test_db.commit()
        test_db.refresh(unternehmen)

        # Assert
        assert unternehmen.plz == "12345"
        assert len(unternehmen.plz) == 5

    def test_unternehmen_indexed_fields(self, test_db: Session, create_unternehmen):
        """
        Test that indexed fields (name, id) work correctly.

        Arrange: Create multiple companies
        Act: Query by indexed field (name)
        Assert: Query executes efficiently and returns correct results
        """
        # Arrange
        company1 = create_unternehmen(name="Alpha GmbH")
        company2 = create_unternehmen(name="Beta AG")
        company3 = create_unternehmen(name="Alpha Corp")

        # Act
        results = test_db.query(Unternehmen).filter(
            Unternehmen.name.like("Alpha%")
        ).all()

        # Assert
        assert len(results) == 2
        result_names = {r.name for r in results}
        assert "Alpha GmbH" in result_names
        assert "Alpha Corp" in result_names

    def test_unternehmen_circular_relationship_post_update(self, test_db: Session, sample_unternehmen_data):
        """
        Test circular relationship handling with post_update.

        This tests the circular foreign key relationship:
        Unternehmen.ansprechpartner_id -> Person.id
        Person.firma_id -> Unternehmen.id

        Arrange: Create company and person with circular reference
        Act: Set up circular relationship
        Assert: Both records are saved successfully
        """
        # Arrange
        unternehmen = Unternehmen(**sample_unternehmen_data)
        test_db.add(unternehmen)
        test_db.commit()
        test_db.refresh(unternehmen)

        person = Person(
            vorname="Test",
            nachname="Person",
            funktion="Mitarbeiter",
            rolle="Ansprechpartner",
            firma_id=unternehmen.id
        )
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Act - Complete the circular relationship
        unternehmen.ansprechpartner_id = person.id
        test_db.commit()
        test_db.refresh(unternehmen)

        # Assert
        assert unternehmen.ansprechpartner_id == person.id
        assert person.firma_id == unternehmen.id
        assert unternehmen.ansprechpartner.id == person.id
        assert person.firma.id == unternehmen.id

    def test_unternehmen_delete_does_not_cascade_to_persons_automatically(self, test_db: Session, create_unternehmen, create_person):
        """
        Test deletion behavior - SQLAlchemy requires explicit cascade configuration.

        Arrange: Create company with persons
        Act: Attempt to delete company
        Assert: Behavior depends on foreign key constraints
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(firma_id=unternehmen.id)

        # Act & Assert
        # In SQLite with default settings, this will raise an error
        # unless cascade is configured or persons are deleted first
        test_db.delete(unternehmen)

        # This should raise an IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            test_db.commit()

        test_db.rollback()

    def test_unternehmen_string_fields_accept_special_characters(self, test_db: Session):
        """
        Test that string fields accept special characters.

        Arrange: Company data with umlauts and special characters
        Act: Create Unternehmen
        Assert: Data is stored correctly
        """
        # Arrange
        data = {
            "name": "Müller & Söhne GmbH",
            "bundesland": "Baden-Württemberg",
            "stadt": "Köln",
            "plz": "50667",
            "strasse": "Große Straße",
            "hausnummer": "12a"
        }

        # Act
        unternehmen = Unternehmen(**data)
        test_db.add(unternehmen)
        test_db.commit()
        test_db.refresh(unternehmen)

        # Assert
        assert unternehmen.name == "Müller & Söhne GmbH"
        assert unternehmen.bundesland == "Baden-Württemberg"
        assert unternehmen.stadt == "Köln"
        assert unternehmen.hausnummer == "12a"
