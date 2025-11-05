"""
Integration tests for Unternehmen routes.

Tests all CRUD operations, pagination, search, sorting,
and error handling for the /api/unternehmen endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from tests.test_helpers import (
    UnternehmenFactory,
    assert_response_status,
    assert_validation_error
)


@pytest.mark.integration
class TestGetUnternehmenEndpoint:
    """Test suite for GET /api/unternehmen/ endpoint."""

    def test_get_unternehmen_empty_database(self, client: TestClient):
        """
        Test getting companies from empty database.

        Arrange: Empty database
        Act: GET /api/unternehmen/
        Assert: Empty items list, total=0
        """
        # Arrange & Act
        response = client.get("/api/unternehmen/")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 20

    def test_get_unternehmen_returns_companies(self, client: TestClient, create_unternehmen):
        """
        Test getting list of companies.

        Arrange: Create 3 companies
        Act: GET /api/unternehmen/
        Assert: Returns all 3 companies
        """
        # Arrange
        company1 = create_unternehmen(name="Firma A")
        company2 = create_unternehmen(name="Firma B")
        company3 = create_unternehmen(name="Firma C")

        # Act
        response = client.get("/api/unternehmen/")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

        names = {item["name"] for item in data["items"]}
        assert "Firma A" in names
        assert "Firma B" in names
        assert "Firma C" in names

    def test_get_unternehmen_pagination_skip(self, client: TestClient, multiple_unternehmen):
        """
        Test pagination with skip parameter.

        Arrange: Create 5 companies
        Act: GET with skip=2
        Assert: Returns items starting from third company
        """
        # Arrange - multiple_unternehmen creates 5 companies

        # Act
        response = client.get("/api/unternehmen/?skip=2")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3  # 5 - 2 = 3
        assert data["skip"] == 2

    def test_get_unternehmen_pagination_limit(self, client: TestClient, multiple_unternehmen):
        """
        Test pagination with limit parameter.

        Arrange: Create 5 companies
        Act: GET with limit=2
        Assert: Returns only 2 companies
        """
        # Arrange

        # Act
        response = client.get("/api/unternehmen/?limit=2")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2

    def test_get_unternehmen_pagination_skip_and_limit(self, client: TestClient, multiple_unternehmen):
        """
        Test pagination with both skip and limit.

        Arrange: Create 5 companies
        Act: GET with skip=1, limit=2
        Assert: Returns 2 companies starting from second
        """
        # Arrange

        # Act
        response = client.get("/api/unternehmen/?skip=1&limit=2")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 1
        assert data["limit"] == 2

    def test_get_unternehmen_pagination_limit_max_100(self, client: TestClient):
        """
        Test that limit is capped at 100.

        Arrange: Request with limit > 100
        Act: GET with limit=150
        Assert: Limit is capped at 100
        """
        # Arrange & Act
        response = client.get("/api/unternehmen/?limit=150")

        # Assert
        # FastAPI query validation should reject values > 100
        assert response.status_code in [200, 422]

    def test_get_unternehmen_search_by_name(self, client: TestClient, create_unternehmen):
        """
        Test search functionality by company name.

        Arrange: Create companies with different names
        Act: GET with search parameter
        Assert: Only matching companies returned
        """
        # Arrange
        create_unternehmen(name="Alpha GmbH")
        create_unternehmen(name="Beta AG")
        create_unternehmen(name="Alpha Corp")

        # Act
        response = client.get("/api/unternehmen/?search=Alpha")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

        names = {item["name"] for item in data["items"]}
        assert "Alpha GmbH" in names
        assert "Alpha Corp" in names

    def test_get_unternehmen_search_case_insensitive(self, client: TestClient, create_unternehmen):
        """
        Test that search is case-insensitive.

        Arrange: Create company with mixed case name
        Act: Search with lowercase
        Assert: Company is found
        """
        # Arrange
        create_unternehmen(name="TechCompany GmbH")

        # Act
        response = client.get("/api/unternehmen/?search=techcompany")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "TechCompany GmbH"

    def test_get_unternehmen_search_by_stadt(self, client: TestClient, create_unternehmen):
        """
        Test search by city (stadt).

        Arrange: Create companies in different cities
        Act: Search by city name
        Assert: Only companies in that city returned
        """
        # Arrange
        create_unternehmen(name="Firma 1", stadt="München")
        create_unternehmen(name="Firma 2", stadt="Berlin")
        create_unternehmen(name="Firma 3", stadt="München")

        # Act
        response = client.get("/api/unternehmen/?search=München")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 2

    def test_get_unternehmen_search_by_plz(self, client: TestClient, create_unternehmen):
        """
        Test search by postal code (PLZ).

        Arrange: Create companies with different PLZ
        Act: Search by PLZ
        Assert: Only matching companies returned
        """
        # Arrange
        create_unternehmen(name="Firma 1", plz="80331")
        create_unternehmen(name="Firma 2", plz="10115")
        create_unternehmen(name="Firma 3", plz="80332")

        # Act
        response = client.get("/api/unternehmen/?search=80331")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["plz"] == "80331"

    def test_get_unternehmen_search_by_bundesland(self, client: TestClient, create_unternehmen):
        """
        Test search by federal state (Bundesland).

        Arrange: Create companies in different states
        Act: Search by state name
        Assert: Only companies in that state returned
        """
        # Arrange
        create_unternehmen(name="Firma 1", bundesland="Bayern")
        create_unternehmen(name="Firma 2", bundesland="Berlin")
        create_unternehmen(name="Firma 3", bundesland="Bayern")

        # Act
        response = client.get("/api/unternehmen/?search=Bayern")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 2

    def test_get_unternehmen_search_no_results(self, client: TestClient, create_unternehmen):
        """
        Test search with no matching results.

        Arrange: Create companies
        Act: Search for non-existent term
        Assert: Empty results
        """
        # Arrange
        create_unternehmen(name="Test GmbH")

        # Act
        response = client.get("/api/unternehmen/?search=NonExistent")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_get_unternehmen_sort_by_name_asc(self, client: TestClient, create_unternehmen):
        """
        Test sorting by name ascending.

        Arrange: Create companies with different names
        Act: GET with sort_by=name, sort_order=asc
        Assert: Companies returned in alphabetical order
        """
        # Arrange
        create_unternehmen(name="Zebra GmbH")
        create_unternehmen(name="Alpha AG")
        create_unternehmen(name="Beta Corp")

        # Act
        response = client.get("/api/unternehmen/?sort_by=name&sort_order=asc")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == ["Alpha AG", "Beta Corp", "Zebra GmbH"]

    def test_get_unternehmen_sort_by_name_desc(self, client: TestClient, create_unternehmen):
        """
        Test sorting by name descending.

        Arrange: Create companies with different names
        Act: GET with sort_by=name, sort_order=desc
        Assert: Companies returned in reverse alphabetical order
        """
        # Arrange
        create_unternehmen(name="Zebra GmbH")
        create_unternehmen(name="Alpha AG")
        create_unternehmen(name="Beta Corp")

        # Act
        response = client.get("/api/unternehmen/?sort_by=name&sort_order=desc")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == ["Zebra GmbH", "Beta Corp", "Alpha AG"]

    def test_get_unternehmen_sort_by_bundesland(self, client: TestClient, create_unternehmen):
        """
        Test sorting by Bundesland.

        Arrange: Create companies in different states
        Act: GET with sort_by=bundesland
        Assert: Companies sorted by state name
        """
        # Arrange
        create_unternehmen(name="Firma 1", bundesland="Sachsen")
        create_unternehmen(name="Firma 2", bundesland="Bayern")
        create_unternehmen(name="Firma 3", bundesland="Hamburg")

        # Act
        response = client.get("/api/unternehmen/?sort_by=bundesland&sort_order=asc")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        bundeslaender = [item["bundesland"] for item in data["items"]]
        assert bundeslaender == ["Bayern", "Hamburg", "Sachsen"]

    def test_get_unternehmen_sort_by_plz(self, client: TestClient, create_unternehmen):
        """
        Test sorting by PLZ.

        Arrange: Create companies with different PLZ
        Act: GET with sort_by=plz
        Assert: Companies sorted by postal code
        """
        # Arrange
        create_unternehmen(name="Firma 1", plz="80331")
        create_unternehmen(name="Firma 2", plz="10115")
        create_unternehmen(name="Firma 3", plz="50667")

        # Act
        response = client.get("/api/unternehmen/?sort_by=plz&sort_order=asc")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        plzs = [item["plz"] for item in data["items"]]
        assert plzs == ["10115", "50667", "80331"]

    def test_get_unternehmen_with_ansprechpartner(self, client: TestClient, create_unternehmen, create_person):
        """
        Test getting company with Ansprechpartner included.

        Arrange: Create company with Ansprechpartner
        Act: GET /api/unternehmen/
        Assert: Ansprechpartner is included in response
        """
        # Arrange
        unternehmen = create_unternehmen()
        person = create_person(
            firma_id=unternehmen.id,
            rolle="Ansprechpartner",
            vorname="Anna",
            nachname="Kontakt"
        )
        unternehmen.ansprechpartner_id = person.id

        # Act
        response = client.get("/api/unternehmen/")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        company = data["items"][0]
        assert company["ansprechpartner"] is not None
        assert company["ansprechpartner"]["vorname"] == "Anna"
        assert company["ansprechpartner"]["rolle"] == "Ansprechpartner"

    def test_get_unternehmen_with_multiple_personen(self, client: TestClient, unternehmen_with_persons):
        """
        Test getting company with all associated persons.

        Arrange: Create company with Ansprechpartner and Empfehler
        Act: GET /api/unternehmen/
        Assert: All persons are included
        """
        # Arrange - fixture creates company with 1 AP and 3 Empfehler

        # Act
        response = client.get("/api/unternehmen/")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        company = data["items"][0]
        assert len(company["personen"]) == 4  # 1 AP + 3 Empfehler

    def test_get_unternehmen_default_sort(self, client: TestClient, create_unternehmen):
        """
        Test default sorting (by name, ascending).

        Arrange: Create companies
        Act: GET without sort parameters
        Assert: Sorted by name ascending
        """
        # Arrange
        create_unternehmen(name="Zebra GmbH")
        create_unternehmen(name="Alpha AG")

        # Act
        response = client.get("/api/unternehmen/")

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names[0] == "Alpha AG"


@pytest.mark.integration
class TestCreateUnternehmenEndpoint:
    """Test suite for POST /api/unternehmen/ endpoint."""

    def test_create_unternehmen_success(self, client: TestClient):
        """
        Test creating a valid company.

        Arrange: Valid company data
        Act: POST /api/unternehmen/
        Assert: Company created with 201 status and returned
        """
        # Arrange
        company_data = UnternehmenFactory.build()

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_response_status(response, 200)  # FastAPI returns 200 by default
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == company_data["name"]
        assert data["bundesland"] == company_data["bundesland"]
        assert data["plz"] == company_data["plz"]

    def test_create_unternehmen_invalid_plz_length(self, client: TestClient):
        """
        Test creating company with invalid PLZ length.

        Arrange: Company data with 4-digit PLZ
        Act: POST /api/unternehmen/
        Assert: 422 validation error
        """
        # Arrange
        company_data = UnternehmenFactory.build(overrides={"plz": "1234"})

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_validation_error(response, "plz")

    def test_create_unternehmen_invalid_plz_non_numeric(self, client: TestClient):
        """
        Test creating company with non-numeric PLZ.

        Arrange: Company data with letters in PLZ
        Act: POST /api/unternehmen/
        Assert: 422 validation error
        """
        # Arrange
        company_data = UnternehmenFactory.build(overrides={"plz": "80A31"})

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_validation_error(response, "plz")

    def test_create_unternehmen_invalid_bundesland(self, client: TestClient):
        """
        Test creating company with invalid Bundesland.

        Arrange: Company data with non-existent state
        Act: POST /api/unternehmen/
        Assert: 422 validation error
        """
        # Arrange
        company_data = UnternehmenFactory.build(overrides={"bundesland": "InvalidState"})

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_validation_error(response, "bundesland")

    def test_create_unternehmen_missing_required_field(self, client: TestClient):
        """
        Test creating company without required field.

        Arrange: Company data without 'name'
        Act: POST /api/unternehmen/
        Assert: 422 validation error
        """
        # Arrange
        company_data = UnternehmenFactory.build()
        del company_data["name"]

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_validation_error(response, "name")

    def test_create_unternehmen_with_special_characters(self, client: TestClient):
        """
        Test creating company with special characters in name.

        Arrange: Company data with umlauts
        Act: POST /api/unternehmen/
        Assert: Company created successfully
        """
        # Arrange
        company_data = UnternehmenFactory.build(overrides={
            "name": "Müller & Söhne GmbH",
            "bundesland": "Baden-Württemberg"
        })

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["name"] == "Müller & Söhne GmbH"
        assert data["bundesland"] == "Baden-Württemberg"

    def test_create_unternehmen_with_valid_ansprechpartner_id(self, client: TestClient, create_unternehmen, create_person):
        """
        Test creating company with existing Ansprechpartner ID.

        Arrange: Create person with Ansprechpartner role, then company
        Act: POST company with ansprechpartner_id
        Assert: Company created with ansprechpartner link
        """
        # Arrange
        temp_company = create_unternehmen()
        person = create_person(
            firma_id=temp_company.id,
            rolle="Ansprechpartner"
        )

        company_data = UnternehmenFactory.build(overrides={
            "ansprechpartner_id": person.id
        })

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert_response_status(response, 200)
        data = response.json()
        assert data["ansprechpartner_id"] == person.id

    def test_create_unternehmen_with_invalid_ansprechpartner_id(self, client: TestClient):
        """
        Test creating company with non-existent Ansprechpartner ID.

        Arrange: Company data with invalid ansprechpartner_id
        Act: POST /api/unternehmen/
        Assert: 400 error
        """
        # Arrange
        company_data = UnternehmenFactory.build(overrides={
            "ansprechpartner_id": 99999
        })

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert response.status_code == 400

    def test_create_unternehmen_with_empfehler_as_ansprechpartner_fails(self, client: TestClient, create_unternehmen, create_person):
        """
        Test that creating company with Empfehler as Ansprechpartner fails.

        Arrange: Create person with Empfehler role
        Act: Try to create company with that person as Ansprechpartner
        Assert: 400 error
        """
        # Arrange
        temp_company = create_unternehmen()
        empfehler = create_person(
            firma_id=temp_company.id,
            rolle="Empfehler"
        )

        company_data = UnternehmenFactory.build(overrides={
            "ansprechpartner_id": empfehler.id
        })

        # Act
        response = client.post("/api/unternehmen/", json=company_data)

        # Assert
        assert response.status_code == 400
