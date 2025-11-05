"""
Test configuration and fixtures for the Unternehmen Management System.

This module provides shared fixtures for database setup, test client,
and common test data factories used across all test modules.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator

# Set test database URL before importing anything that uses settings
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.core.database import Base, get_db
from app.models.unternehmen import Unternehmen
from app.models.person import Person


# Test database configuration using SQLite in-memory for fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """
    Create a SQLite in-memory engine for testing.

    Uses StaticPool to ensure the same connection is reused
    across all queries in a test, preventing database resets.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.

    This fixture provides a clean database session for each test.
    All changes are rolled back after the test completes.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with database dependency override.

    This fixture provides a test client that uses the test database
    instead of the production database.
    """
    # Import app here to avoid triggering database creation on import
    from main import app

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_unternehmen_data():
    """
    Provide sample company data for testing.

    Returns a dictionary with valid company data that can be used
    to create test Unternehmen instances.
    """
    return {
        "name": "Test GmbH",
        "bundesland": "Bayern",
        "stadt": "München",
        "plz": "80331",
        "strasse": "Maximilianstraße",
        "hausnummer": "1"
    }


@pytest.fixture
def sample_person_data():
    """
    Provide sample person data for testing.

    Returns a dictionary with valid person data that can be used
    to create test Person instances.
    """
    return {
        "vorname": "Max",
        "nachname": "Mustermann",
        "email": "max.mustermann@test.de",
        "telefon": "089 123456",
        "funktion": "Mitarbeiter",
        "rolle": "Empfehler"
    }


@pytest.fixture
def create_unternehmen(test_db: Session):
    """
    Factory fixture for creating test Unternehmen instances.

    Returns a function that creates and persists a company in the test database.
    Accepts optional overrides for default company data.
    """
    def _create_unternehmen(**kwargs):
        default_data = {
            "name": "Test GmbH",
            "bundesland": "Bayern",
            "stadt": "München",
            "plz": "80331",
            "strasse": "Maximilianstraße",
            "hausnummer": "1"
        }
        default_data.update(kwargs)
        unternehmen = Unternehmen(**default_data)
        test_db.add(unternehmen)
        test_db.commit()
        test_db.refresh(unternehmen)
        return unternehmen
    return _create_unternehmen


@pytest.fixture
def create_person(test_db: Session):
    """
    Factory fixture for creating test Person instances.

    Returns a function that creates and persists a person in the test database.
    Requires firma_id to be provided. Accepts optional overrides for default person data.
    """
    def _create_person(firma_id: int, **kwargs):
        default_data = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "max.mustermann@test.de",
            "telefon": "089 123456",
            "funktion": "Mitarbeiter",
            "rolle": "Empfehler",
            "firma_id": firma_id
        }
        default_data.update(kwargs)
        person = Person(**default_data)
        test_db.add(person)
        test_db.commit()
        test_db.refresh(person)
        return person
    return _create_person


@pytest.fixture
def unternehmen_with_persons(test_db: Session, create_unternehmen, create_person):
    """
    Create a complete test scenario with a company and multiple persons.

    Returns a dictionary containing:
    - unternehmen: The company instance
    - ansprechpartner: The main contact person
    - empfehler: List of referrer persons
    """
    # Create company
    unternehmen = create_unternehmen(name="Complete Test GmbH")

    # Create Ansprechpartner
    ansprechpartner = create_person(
        firma_id=unternehmen.id,
        vorname="Anna",
        nachname="Hauptkontakt",
        rolle="Ansprechpartner",
        funktion="Mitarbeiter"
    )

    # Update company with ansprechpartner_id
    unternehmen.ansprechpartner_id = ansprechpartner.id
    test_db.commit()
    test_db.refresh(unternehmen)

    # Create multiple Empfehler
    empfehler = []
    for i in range(3):
        emp = create_person(
            firma_id=unternehmen.id,
            vorname=f"Empfehler{i}",
            nachname=f"Person{i}",
            rolle="Empfehler",
            funktion="Mitarbeiter"
        )
        empfehler.append(emp)

    return {
        "unternehmen": unternehmen,
        "ansprechpartner": ansprechpartner,
        "empfehler": empfehler
    }


@pytest.fixture
def multiple_unternehmen(test_db: Session, create_unternehmen):
    """
    Create multiple companies for testing pagination and search.

    Returns a list of company instances with varying data across
    different German states.
    """
    companies = []
    bundeslaender = ["Bayern", "Berlin", "Hamburg", "Sachsen", "Hessen"]
    cities = ["München", "Berlin", "Hamburg", "Dresden", "Frankfurt"]

    for i, (bundesland, stadt) in enumerate(zip(bundeslaender, cities), start=1):
        company = create_unternehmen(
            name=f"Firma {i} GmbH",
            bundesland=bundesland,
            stadt=stadt,
            plz=f"{80000 + i:05d}",
            strasse=f"Straße {i}",
            hausnummer=str(i)
        )
        companies.append(company)

    return companies
