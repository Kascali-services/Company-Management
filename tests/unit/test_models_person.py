"""
Unit tests for Person SQLAlchemy model.

Tests the database model behavior, relationships, and constraints
for the Person entity, including Ansprechpartner and Empfehler roles.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.person import Person
from app.models.unternehmen import Unternehmen


@pytest.mark.unit
class TestPersonModel:
    """Test suite for the Person model."""

    def test_create_person_success(self, test_db: Session, create_unternehmen, sample_person_data):
        """
        Test creating a valid Person instance.

        Arrange: Valid person data with firma_id
        Act: Create and persist Person
        Assert: Person is saved with correct attributes
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {**sample_person_data, "firma_id": unternehmen.id}

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.id is not None
        assert person.vorname == sample_person_data["vorname"]
        assert person.nachname == sample_person_data["nachname"]
        assert person.email == sample_person_data["email"]
        assert person.telefon == sample_person_data["telefon"]
        assert person.funktion == sample_person_data["funktion"]
        assert person.rolle == sample_person_data["rolle"]
        assert person.firma_id == unternehmen.id

    def test_create_person_with_empfehler_role(self, test_db: Session, create_unternehmen):
        """
        Test creating a Person with Empfehler role.

        Arrange: Person data with rolle="Empfehler"
        Act: Create Person
        Assert: Person is created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Thomas",
            "nachname": "Empfehler",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.rolle == "Empfehler"

    def test_create_person_with_ansprechpartner_role(self, test_db: Session, create_unternehmen):
        """
        Test creating a Person with Ansprechpartner role.

        Arrange: Person data with rolle="Ansprechpartner"
        Act: Create Person
        Assert: Person is created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Anna",
            "nachname": "Hauptkontakt",
            "funktion": "Mitarbeiter",
            "rolle": "Ansprechpartner",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.rolle == "Ansprechpartner"

    def test_create_person_missing_required_field_raises_error(self, test_db: Session, create_unternehmen):
        """
        Test that creating Person without required field raises error.

        Arrange: Person data missing required field (vorname)
        Act: Attempt to create Person
        Assert: TypeError is raised
        """
        # Arrange
        unternehmen = create_unternehmen()
        invalid_data = {
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
            # Missing 'vorname'
        }

        # Act & Assert
        with pytest.raises(TypeError):
            person = Person(**invalid_data)

    def test_create_person_without_firma_id_raises_error(self, test_db: Session):
        """
        Test that Person requires firma_id (foreign key constraint).

        Arrange: Person data without firma_id
        Act: Attempt to create and commit Person
        Assert: IntegrityError is raised
        """
        # Arrange
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
            # Missing firma_id
        }

        # Act & Assert
        with pytest.raises(TypeError):
            person = Person(**person_data)

    def test_create_person_with_invalid_firma_id_raises_error(self, test_db: Session):
        """
        Test that Person with non-existent firma_id raises error.

        Arrange: Person data with invalid firma_id
        Act: Attempt to create and commit Person
        Assert: IntegrityError is raised due to foreign key constraint
        """
        # Arrange
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": 99999  # Non-existent ID
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)

        # Assert
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_person_firma_relationship(self, test_db: Session, create_unternehmen, create_person):
        """
        Test the firma relationship navigation.

        Arrange: Create person linked to company
        Act: Access firma via relationship
        Assert: Relationship returns correct Unternehmen instance
        """
        # Arrange
        unternehmen = create_unternehmen(name="Test Firma GmbH")
        person = create_person(firma_id=unternehmen.id)

        test_db.refresh(person)

        # Act
        firma = person.firma

        # Assert
        assert firma is not None
        assert firma.id == unternehmen.id
        assert firma.name == "Test Firma GmbH"

    def test_person_email_nullable(self, test_db: Session, create_unternehmen):
        """
        Test that email field is optional.

        Arrange: Person data without email
        Act: Create Person
        Assert: Person is saved with email as None
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": None,
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.email is None

    def test_person_telefon_nullable(self, test_db: Session, create_unternehmen):
        """
        Test that telefon field is optional.

        Arrange: Person data without telefon
        Act: Create Person
        Assert: Person is saved with telefon as None
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "telefon": None,
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.telefon is None

    def test_person_with_mitarbeiter_funktion(self, test_db: Session, create_unternehmen):
        """
        Test creating Person with Mitarbeiter function.

        Arrange: Person data with funktion="Mitarbeiter"
        Act: Create Person
        Assert: Funktion is stored correctly
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.funktion == "Mitarbeiter"

    def test_person_with_azubi_funktion(self, test_db: Session, create_unternehmen):
        """
        Test creating Person with Azubi function.

        Arrange: Person data with funktion="Azubi"
        Act: Create Person
        Assert: Funktion is stored correctly
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Azubi",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.funktion == "Azubi"

    def test_multiple_persons_same_company(self, test_db: Session, create_unternehmen, create_person):
        """
        Test that a company can have multiple persons.

        Arrange: Create company and multiple persons
        Act: Link all persons to same company
        Assert: All persons are created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()

        # Act
        person1 = create_person(firma_id=unternehmen.id, vorname="Person1")
        person2 = create_person(firma_id=unternehmen.id, vorname="Person2")
        person3 = create_person(firma_id=unternehmen.id, vorname="Person3")

        # Assert
        assert person1.firma_id == unternehmen.id
        assert person2.firma_id == unternehmen.id
        assert person3.firma_id == unternehmen.id

        persons = test_db.query(Person).filter(Person.firma_id == unternehmen.id).all()
        assert len(persons) == 3

    def test_multiple_empfehler_same_company_allowed(self, test_db: Session, create_unternehmen, create_person):
        """
        Test that a company can have multiple Empfehler.

        Arrange: Create company
        Act: Create multiple Empfehler for the company
        Assert: All Empfehler are created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()

        # Act
        emp1 = create_person(firma_id=unternehmen.id, rolle="Empfehler", vorname="Emp1")
        emp2 = create_person(firma_id=unternehmen.id, rolle="Empfehler", vorname="Emp2")
        emp3 = create_person(firma_id=unternehmen.id, rolle="Empfehler", vorname="Emp3")

        # Assert
        empfehler = test_db.query(Person).filter(
            Person.firma_id == unternehmen.id,
            Person.rolle == "Empfehler"
        ).all()
        assert len(empfehler) == 3

    def test_person_string_fields_accept_special_characters(self, test_db: Session, create_unternehmen):
        """
        Test that string fields accept special characters (umlauts, etc.).

        Arrange: Person data with special characters
        Act: Create Person
        Assert: Data is stored correctly
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Müller",
            "nachname": "Größmann-Öztürk",
            "email": "müller@example.de",
            "telefon": "+49 (0)89 123-456",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": unternehmen.id
        }

        # Act
        person = Person(**person_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.vorname == "Müller"
        assert person.nachname == "Größmann-Öztürk"
        assert person.email == "müller@example.de"
        assert person.telefon == "+49 (0)89 123-456"

    def test_person_back_populates_relationship(self, test_db: Session, create_unternehmen, create_person):
        """
        Test bidirectional relationship between Person and Unternehmen.

        Arrange: Create company and person
        Act: Access relationship from both directions
        Assert: Both directions work correctly
        """
        # Arrange
        unternehmen = create_unternehmen(name="Bidirectional Test GmbH")
        person = create_person(firma_id=unternehmen.id, vorname="Test")

        test_db.refresh(unternehmen)
        test_db.refresh(person)

        # Act & Assert
        # Person -> Unternehmen
        assert person.firma.id == unternehmen.id
        assert person.firma.name == "Bidirectional Test GmbH"

        # Unternehmen -> Person
        assert len(unternehmen.personen) > 0
        assert person.id in [p.id for p in unternehmen.personen]

    def test_person_delete_does_not_affect_company(self, test_db: Session, create_unternehmen, create_person):
        """
        Test that deleting a person doesn't delete the company.

        Arrange: Create company and person
        Act: Delete person
        Assert: Company still exists
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(firma_id=unternehmen.id)
        person_id = person.id
        unternehmen_id = unternehmen.id

        # Act
        test_db.delete(person)
        test_db.commit()

        # Assert
        deleted_person = test_db.query(Person).filter(Person.id == person_id).first()
        assert deleted_person is None

        existing_company = test_db.query(Unternehmen).filter(Unternehmen.id == unternehmen_id).first()
        assert existing_company is not None

    def test_person_update_attributes(self, test_db: Session, create_unternehmen, create_person):
        """
        Test updating Person attributes.

        Arrange: Create person
        Act: Update multiple attributes
        Assert: Changes are persisted correctly
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            vorname="Original",
            email="original@test.de",
            rolle="Empfehler"
        )

        # Act
        person.vorname = "Updated"
        person.email = "updated@test.de"
        person.rolle = "Ansprechpartner"
        test_db.commit()
        test_db.refresh(person)

        # Assert
        assert person.vorname == "Updated"
        assert person.email == "updated@test.de"
        assert person.rolle == "Ansprechpartner"

    def test_query_persons_by_rolle(self, test_db: Session, create_unternehmen, create_person):
        """
        Test filtering persons by rolle.

        Arrange: Create persons with different roles
        Act: Query by rolle
        Assert: Correct persons are returned
        """
        # Arrange
        unternehmen = create_unternehmen()
        ansprechpartner = create_person(firma_id=unternehmen.id, rolle="Ansprechpartner", vorname="AP")
        empfehler1 = create_person(firma_id=unternehmen.id, rolle="Empfehler", vorname="E1")
        empfehler2 = create_person(firma_id=unternehmen.id, rolle="Empfehler", vorname="E2")

        # Act
        ansprechpartner_list = test_db.query(Person).filter(
            Person.rolle == "Ansprechpartner"
        ).all()
        empfehler_list = test_db.query(Person).filter(
            Person.rolle == "Empfehler"
        ).all()

        # Assert
        assert len(ansprechpartner_list) == 1
        assert ansprechpartner_list[0].id == ansprechpartner.id

        assert len(empfehler_list) == 2
        empfehler_ids = {e.id for e in empfehler_list}
        assert empfehler1.id in empfehler_ids
        assert empfehler2.id in empfehler_ids
