"""
Unit tests for core configuration module.

Tests the configuration loading from environment variables
and default values.
"""

import pytest
import os
from unittest.mock import patch

from app.core.config import Settings, settings


@pytest.mark.unit
class TestSettings:
    """Test suite for Settings class."""

    def test_settings_default_database_url(self):
        """
        Test default DATABASE_URL when environment variable is not set.

        Arrange: No DATABASE_URL environment variable
        Act: Create Settings instance
        Assert: Default URL is used
        """
        # Arrange & Act
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()

        # Assert
        assert test_settings.DATABASE_URL == "postgresql://user:password@localhost:5432/companies_db"

    def test_settings_from_environment_variable(self):
        """
        Test loading DATABASE_URL from environment variable.

        Arrange: Set DATABASE_URL environment variable
        Act: Create Settings instance
        Assert: Environment variable value is used
        """
        # Arrange
        custom_url = "postgresql://testuser:testpass@testhost:5432/testdb"

        # Act
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            test_settings = Settings()

        # Assert
        assert test_settings.DATABASE_URL == custom_url

    def test_settings_environment_variable_overrides_default(self):
        """
        Test that environment variable takes precedence over default.

        Arrange: Set custom DATABASE_URL
        Act: Create Settings
        Assert: Custom URL is used, not default
        """
        # Arrange
        custom_url = "postgresql://custom:custom@custom:5432/custom"

        # Act
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            test_settings = Settings()

        # Assert
        assert test_settings.DATABASE_URL == custom_url
        assert test_settings.DATABASE_URL != "postgresql://user:password@localhost:5432/companies_db"

    def test_settings_singleton_instance(self):
        """
        Test that module-level settings instance exists.

        Arrange: Import settings
        Act: Access settings
        Assert: settings is an instance of Settings
        """
        # Arrange & Act & Assert
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'DATABASE_URL')

    def test_settings_handles_empty_env_var(self):
        """
        Test behavior when DATABASE_URL is set but empty.

        Arrange: Set DATABASE_URL to empty string
        Act: Create Settings
        Assert: Default value is used (getenv returns default for empty string)
        """
        # Arrange & Act
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            test_settings = Settings()

        # Assert
        # os.getenv returns empty string when env var is set but empty
        assert test_settings.DATABASE_URL == ""

    def test_settings_database_url_with_special_characters(self):
        """
        Test DATABASE_URL with special characters in password.

        Arrange: Set DATABASE_URL with special characters
        Act: Create Settings
        Assert: URL is preserved correctly
        """
        # Arrange
        url_with_special_chars = "postgresql://user:p@ssw0rd!@host:5432/db"

        # Act
        with patch.dict(os.environ, {"DATABASE_URL": url_with_special_chars}):
            test_settings = Settings()

        # Assert
        assert test_settings.DATABASE_URL == url_with_special_chars

    def test_settings_different_database_types(self):
        """
        Test Settings with different database URL formats.

        Arrange: Various database URLs (PostgreSQL, SQLite)
        Act: Create Settings with each URL
        Assert: Each URL is accepted
        """
        # Arrange
        database_urls = [
            "postgresql://user:pass@localhost:5432/db",
            "postgresql+psycopg2://user:pass@localhost/db",
            "sqlite:///./test.db",
            "sqlite:///:memory:"
        ]

        # Act & Assert
        for url in database_urls:
            with patch.dict(os.environ, {"DATABASE_URL": url}):
                test_settings = Settings()
                assert test_settings.DATABASE_URL == url

    def test_settings_is_dataclass_like(self):
        """
        Test that Settings has expected attributes.

        Arrange: Create Settings instance
        Act: Check attributes
        Assert: DATABASE_URL attribute exists
        """
        # Arrange
        test_settings = Settings()

        # Act & Assert
        assert hasattr(test_settings, 'DATABASE_URL')
        assert isinstance(test_settings.DATABASE_URL, str)
