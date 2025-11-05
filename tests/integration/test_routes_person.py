"""
Integration tests for Person routes.

Tests all CRUD operations, Ansprechpartner business logic,
and error handling for the /api/personen endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_helpers import (
    PersonFactory,
    assert_response_status,
    assert_validation_error
)


@pytest.mark.integration
class TestCreatePersonEndpoint:
    """Test suite for POST /api/personen/unternehmen/{unternehmen_id} endpoint."""

    def test_create_person_empfehler_success(self, client: TestClient, create_unternehmen):
        """
        Test creating an Empfehler for a company.

        Arrange: Create company and Empfehler data
        Act: POST /api/personen/unternehmen/{id}
        Assert: Empfehler created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_empfehler()

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["id"] is not None
        assert data["firma_id"] == unternehmen.id
        assert data["rolle"] == "Empfehler"
        assert data["vorname"] == person_data["vorname"]

    def test_create_person_ansprechpartner_success(self, client: TestClient, create_unternehmen):
        """
        Test creating an Ansprechpartner for a company.

        Arrange: Create company and Ansprechpartner data
        Act: POST /api/personen/unternehmen/{id}
        Assert: Ansprechpartner created and company updated
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_ansprechpartner()

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["rolle"] == "Ansprechpartner"
        assert data["firma_id"] == unternehmen.id

        # Verify company's ansprechpartner_id is updated
        company_response = client.get("/api/unternehmen/")
        companies = company_response.json()
        company = companies["items"][0]
        assert company["ansprechpartner_id"] == data["id"]

    def test_create_person_for_nonexistent_company_fails(self, client: TestClient):
        """
        Test creating person for non-existent company.

        Arrange: Person data with invalid company ID
        Act: POST /api/personen/unternehmen/99999
        Assert: 404 error
        """
        # Arrange
        person_data = PersonFactory.build_empfehler()

        # Act
        response = client.post(
            "/api/personen/unternehmen/99999",
            json=person_data
        )

        # Assert
        assert response.status_code == 404
        assert "nicht gefunden" in response.json()["detail"]

    def test_create_second_ansprechpartner_fails(self, client: TestClient, create_unternehmen, create_person):
        """
        Test that creating second Ansprechpartner for company fails.

        Arrange: Create company with existing Ansprechpartner
        Act: Try to create another Ansprechpartner
        Assert: 400 error
        """
        # Arrange
        unternehmen = create_unternehmen()
        existing_ap = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner"
        )

        new_ap_data = PersonFactory.build_ansprechpartner(overrides={
            "vorname": "Zweiter",
            "nachname": "Ansprechpartner"
        })

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=new_ap_data
        )

        # Assert
        assert response.status_code == 400
        assert "bereits einen Ansprechpartner" in response.json()["detail"]

    def test_create_multiple_empfehler_success(self, client: TestClient, create_unternehmen):
        """
        Test that company can have multiple Empfehler.

        Arrange: Create company
        Act: Create 3 Empfehler for the company
        Assert: All are created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()

        # Act
        for i in range(3):
            person_data = PersonFactory.build_empfehler(overrides={
                "vorname": f"Empfehler{i}",
                "nachname": f"Person{i}"
            })
            response = client.post(
                f"/api/personen/unternehmen/{unternehmen.id}",
                json=person_data
            )

            # Assert
            assert_response_status(response, 200)

    def test_create_person_invalid_rolle(self, client: TestClient, create_unternehmen):
        """
        Test creating person with invalid rolle.

        Arrange: Person data with invalid rolle
        Act: POST /api/personen/unternehmen/{id}
        Assert: 422 validation error
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_empfehler(overrides={
            "rolle": "InvalidRole"
        })

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_validation_error(response, "rolle")

    def test_create_person_invalid_funktion(self, client: TestClient, create_unternehmen):
        """
        Test creating person with invalid funktion.

        Arrange: Person data with invalid funktion
        Act: POST /api/personen/unternehmen/{id}
        Assert: 422 validation error
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_empfehler(overrides={
            "funktion": "Manager"
        })

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_validation_error(response, "funktion")

    def test_create_person_missing_required_field(self, client: TestClient, create_unternehmen):
        """
        Test creating person without required field.

        Arrange: Person data without vorname
        Act: POST /api/personen/unternehmen/{id}
        Assert: 422 validation error
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_empfehler()
        del person_data["vorname"]

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_validation_error(response, "vorname")

    def test_create_person_without_optional_fields(self, client: TestClient, create_unternehmen):
        """
        Test creating person without optional email and telefon.

        Arrange: Person data without email and telefon
        Act: POST /api/personen/unternehmen/{id}
        Assert: Person created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler"
        }

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["email"] is None
        assert data["telefon"] is None

    def test_create_person_with_special_characters(self, client: TestClient, create_unternehmen):
        """
        Test creating person with special characters in names.

        Arrange: Person data with umlauts and hyphens
        Act: POST /api/personen/unternehmen/{id}
        Assert: Person created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_empfehler(overrides={
            "vorname": "Müller",
            "nachname": "Größmann-Öztürk",
            "email": "müller@test.de"
        })

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["vorname"] == "Müller"
        assert data["nachname"] == "Größmann-Öztürk"

    def test_create_person_azubi_ansprechpartner(self, client: TestClient, create_unternehmen):
        """
        Test creating Ansprechpartner with Azubi funktion.

        Arrange: Ansprechpartner data with Azubi funktion
        Act: POST /api/personen/unternehmen/{id}
        Assert: Person created successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person_data = PersonFactory.build_ansprechpartner(overrides={
            "funktion": "Azubi"
        })

        # Act
        response = client.post(
            f"/api/personen/unternehmen/{unternehmen.id}",
            json=person_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["funktion"] == "Azubi"
        assert data["rolle"] == "Ansprechpartner"


@pytest.mark.integration
class TestUpdatePersonEndpoint:
    """Test suite for PUT /api/personen/{person_id} endpoint."""

    def test_update_person_basic_info(self, client: TestClient, create_unternehmen, create_person):
        """
        Test updating person's basic information.

        Arrange: Create person
        Act: PUT with updated data
        Assert: Person is updated
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            vorname="Original",
            email="original@test.de"
        )

        updated_data = PersonFactory.build_empfehler(overrides={
            "vorname": "Updated",
            "email": "updated@test.de"
        })

        # Act
        response = client.put(
            f"/api/personen/{person.id}",
            json=updated_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["vorname"] == "Updated"
        assert data["email"] == "updated@test.de"

    def test_update_empfehler_to_ansprechpartner(self, client: TestClient, create_unternehmen, create_person):
        """
        Test changing person from Empfehler to Ansprechpartner.

        Arrange: Create Empfehler
        Act: Update rolle to Ansprechpartner
        Assert: Person updated and company ansprechpartner_id set
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Empfehler",
            vorname="Test"
        )

        updated_data = PersonFactory.build_ansprechpartner(overrides={
            "vorname": "Test"
        })

        # Act
        response = client.put(
            f"/api/personen/{person.id}",
            json=updated_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["rolle"] == "Ansprechpartner"

        # Verify company updated
        company_response = client.get("/api/unternehmen/")
        company = company_response.json()["items"][0]
        assert company["ansprechpartner_id"] == person.id

    def test_update_ansprechpartner_to_empfehler(self, client: TestClient, create_unternehmen, create_person):
        """
        Test changing person from Ansprechpartner to Empfehler.

        Arrange: Create Ansprechpartner
        Act: Update rolle to Empfehler
        Assert: Person updated and company ansprechpartner_id cleared
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            vorname="Test"
        )
        unternehmen.ansprechpartner_id = person.id

        updated_data = PersonFactory.build_empfehler(overrides={
            "vorname": "Test"
        })

        # Act
        response = client.put(
            f"/api/personen/{person.id}",
            json=updated_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["rolle"] == "Empfehler"

        # Verify company ansprechpartner_id is cleared
        company_response = client.get("/api/unternehmen/")
        company = company_response.json()["items"][0]
        assert company["ansprechpartner_id"] is None

    def test_update_empfehler_to_ansprechpartner_when_one_exists_fails(self, client: TestClient, create_unternehmen, create_person):
        """
        Test that updating Empfehler to Ansprechpartner fails when one exists.

        Arrange: Create company with Ansprechpartner and Empfehler
        Act: Try to change Empfehler to Ansprechpartner
        Assert: 400 error
        """
        # Arrange
        unternehmen = create_unternehmen()
        existing_ap = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            vorname="Existing"
        )
        empfehler = create_person(
            firma_id=unternehmen.id,
            rolle="Empfehler",
            vorname="Empfehler"
        )

        updated_data = PersonFactory.build_ansprechpartner(overrides={
            "vorname": "Empfehler"
        })

        # Act
        response = client.put(
            f"/api/personen/{empfehler.id}",
            json=updated_data
        )

        # Assert
        assert response.status_code == 400
        assert "bereits einen Ansprechpartner" in response.json()["detail"]

    def test_update_person_nonexistent_fails(self, client: TestClient):
        """
        Test updating non-existent person.

        Arrange: Person data for non-existent ID
        Act: PUT /api/personen/99999
        Assert: 404 error
        """
        # Arrange
        person_data = PersonFactory.build_empfehler()

        # Act
        response = client.put(
            "/api/personen/99999",
            json=person_data
        )

        # Assert
        assert response.status_code == 404
        assert "nicht gefunden" in response.json()["detail"]

    def test_update_person_invalid_rolle(self, client: TestClient, create_unternehmen, create_person):
        """
        Test updating person with invalid rolle.

        Arrange: Create person
        Act: Update with invalid rolle
        Assert: 422 validation error
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(firma_id=unternehmen.id)

        updated_data = PersonFactory.build_empfehler(overrides={
            "rolle": "InvalidRole"
        })

        # Act
        response = client.put(
            f"/api/personen/{person.id}",
            json=updated_data
        )

        # Assert
        assert_validation_error(response, "rolle")

    def test_update_person_funktion(self, client: TestClient, create_unternehmen, create_person):
        """
        Test updating person's funktion.

        Arrange: Create person with Mitarbeiter funktion
        Act: Update to Azubi
        Assert: Funktion updated successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            funktion="Mitarbeiter"
        )

        updated_data = PersonFactory.build_empfehler(overrides={
            "funktion": "Azubi"
        })

        # Act
        response = client.put(
            f"/api/personen/{person.id}",
            json=updated_data
        )

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["funktion"] == "Azubi"


@pytest.mark.integration
class TestDeletePersonEndpoint:
    """Test suite for DELETE /api/personen/{person_id} endpoint."""

    def test_delete_empfehler_success(self, client: TestClient, create_unternehmen, create_person):
        """
        Test deleting an Empfehler.

        Arrange: Create Empfehler
        Act: DELETE /api/personen/{id}
        Assert: Person deleted successfully
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Empfehler"
        )
        person_id = person.id

        # Act
        response = client.delete(f"/api/personen/{person_id}")

        # Assert
        assert_response_status(response, 200)
        assert "gelöscht" in response.json()["message"]

    def test_delete_ansprechpartner_clears_company_reference(self, client: TestClient, create_unternehmen, create_person, test_db):
        """
        Test deleting Ansprechpartner clears company's ansprechpartner_id.

        Arrange: Create company with Ansprechpartner
        Act: DELETE Ansprechpartner
        Assert: Person deleted and company ansprechpartner_id is None
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner"
        )
        unternehmen.ansprechpartner_id = person.id
        test_db.commit()
        person_id = person.id

        # Act
        response = client.delete(f"/api/personen/{person_id}")

        # Assert
        assert_response_status(response, 200)

        # Verify company ansprechpartner_id is cleared
        company_response = client.get("/api/unternehmen/")
        company = company_response.json()["items"][0]
        assert company["ansprechpartner_id"] is None

    def test_delete_person_nonexistent_fails(self, client: TestClient):
        """
        Test deleting non-existent person.

        Arrange: Non-existent person ID
        Act: DELETE /api/personen/99999
        Assert: 404 error
        """
        # Arrange & Act
        response = client.delete("/api/personen/99999")

        # Assert
        assert response.status_code == 404
        assert "nicht gefunden" in response.json()["detail"]

    def test_delete_person_does_not_delete_company(self, client: TestClient, create_unternehmen, create_person):
        """
        Test that deleting person doesn't delete the company.

        Arrange: Create company and person
        Act: Delete person
        Assert: Company still exists
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(firma_id=unternehmen.id)
        company_id = unternehmen.id

        # Act
        response = client.delete(f"/api/personen/{person.id}")

        # Assert
        assert_response_status(response, 200)

        # Verify company still exists
        company_response = client.get("/api/unternehmen/")
        companies = company_response.json()["items"]
        assert len(companies) == 1
        assert companies[0]["id"] == company_id

    def test_delete_all_persons_from_company(self, client: TestClient, unternehmen_with_persons):
        """
        Test deleting all persons from a company.

        Arrange: Create company with multiple persons
        Act: Delete all persons
        Assert: All deleted, company remains
        """
        # Arrange
        data = unternehmen_with_persons
        person_ids = [data["ansprechpartner"].id] + [p.id for p in data["empfehler"]]

        # Act
        for person_id in person_ids:
            response = client.delete(f"/api/personen/{person_id}")
            assert_response_status(response, 200)

        # Assert - company still exists
        company_response = client.get("/api/unternehmen/")
        companies = company_response.json()["items"]
        assert len(companies) == 1
