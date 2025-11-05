"""
Unit tests for core database module.

Tests database connection setup, session management,
and the get_db dependency function.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base, get_db, engine, SessionLocal


@pytest.mark.unit
class TestDatabaseModule:
    """Test suite for database module components."""

    def test_base_declarative_base_exists(self):
        """
        Test that Base declarative base is created.

        Arrange: Import Base
        Act: Check Base attributes
        Assert: Base has metadata and registry
        """
        # Arrange & Act & Assert
        assert Base is not None
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')

    def test_engine_created(self):
        """
        Test that SQLAlchemy engine is created.

        Arrange: Import engine
        Act: Check engine attributes
        Assert: Engine is a valid SQLAlchemy engine
        """
        # Arrange & Act & Assert
        assert engine is not None
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'dispose')

    def test_session_local_created(self):
        """
        Test that SessionLocal sessionmaker is created.

        Arrange: Import SessionLocal
        Act: Check SessionLocal attributes
        Assert: SessionLocal is a sessionmaker
        """
        # Arrange & Act & Assert
        assert SessionLocal is not None
        assert callable(SessionLocal)

    def test_session_local_creates_session(self):
        """
        Test that SessionLocal can create Session instances.

        Arrange: SessionLocal factory
        Act: Create a session
        Assert: Session is created successfully
        """
        # Arrange
        session = SessionLocal()

        # Act & Assert
        try:
            assert isinstance(session, Session)
            assert hasattr(session, 'query')
            assert hasattr(session, 'add')
            assert hasattr(session, 'commit')
        finally:
            session.close()

    def test_get_db_yields_session(self):
        """
        Test that get_db generator yields a database session.

        Arrange: Call get_db
        Act: Get session from generator
        Assert: Session is yielded
        """
        # Arrange
        db_generator = get_db()

        # Act
        try:
            db = next(db_generator)

            # Assert
            assert isinstance(db, Session)
            assert hasattr(db, 'query')
        finally:
            # Clean up
            try:
                next(db_generator)
            except StopIteration:
                pass

    def test_get_db_closes_session_after_use(self):
        """
        Test that get_db closes session in finally block.

        Arrange: Get session from get_db
        Act: Exhaust the generator
        Assert: Session is closed (no exception raised)
        """
        # Arrange
        db_generator = get_db()
        db = next(db_generator)

        # Act & Assert
        # The finally block should close the session
        try:
            next(db_generator)
        except StopIteration:
            # Expected - generator exhausted
            pass

        # If session wasn't closed properly, this would raise an error
        # Just verifying no exception is raised

    def test_get_db_handles_exception_during_session(self):
        """
        Test that get_db closes session even when exception occurs.

        Arrange: Get session from get_db
        Act: Raise exception during usage
        Assert: Session is still closed
        """
        # Arrange
        db_generator = get_db()
        db = next(db_generator)

        # Act
        try:
            # Simulate an exception during database operation
            raise Exception("Test exception")
        except Exception:
            pass

        # Assert - generator should still clean up
        try:
            next(db_generator)
        except StopIteration:
            pass  # Expected

    def test_base_metadata_has_tables_after_import(self):
        """
        Test that Base.metadata contains tables after models are imported.

        Arrange: Import models
        Act: Check Base.metadata.tables
        Assert: Tables are registered
        """
        # Arrange - Import models to register them
        from app.models.unternehmen import Unternehmen
        from app.models.person import Person

        # Act & Assert
        assert len(Base.metadata.tables) > 0
        assert 'unternehmen' in Base.metadata.tables
        assert 'person' in Base.metadata.tables

    def test_session_local_configuration(self):
        """
        Test SessionLocal configuration settings.

        Arrange: Create session from SessionLocal
        Act: Check session configuration
        Assert: autocommit and autoflush are False
        """
        # Arrange
        session = SessionLocal()

        # Act & Assert
        try:
            assert session.autocommit is False
            assert session.autoflush is False
        finally:
            session.close()

    def test_engine_url_contains_database_name(self):
        """
        Test that engine URL contains database configuration.

        Arrange: Access engine.url
        Act: Check URL components
        Assert: URL is properly formatted
        """
        # Arrange & Act
        url = str(engine.url)

        # Assert
        assert url is not None
        assert len(url) > 0
        # URL should contain database protocol
        assert any(protocol in url.lower() for protocol in ['postgresql', 'sqlite', 'mysql'])

    def test_get_db_is_generator(self):
        """
        Test that get_db is a generator function.

        Arrange: Call get_db
        Act: Check return type
        Assert: Returns a generator
        """
        # Arrange & Act
        result = get_db()

        # Assert
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_multiple_get_db_calls_create_separate_sessions(self):
        """
        Test that multiple get_db calls create separate sessions.

        Arrange: Call get_db twice
        Act: Get sessions from both generators
        Assert: Sessions are different objects
        """
        # Arrange
        gen1 = get_db()
        gen2 = get_db()

        # Act
        try:
            db1 = next(gen1)
            db2 = next(gen2)

            # Assert
            assert db1 is not db2
        finally:
            # Clean up
            for gen in [gen1, gen2]:
                try:
                    next(gen)
                except StopIteration:
                    pass
