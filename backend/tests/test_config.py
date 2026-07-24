import pytest
from pydantic_settings import SettingsConfigDict

from app.core.config import Settings


class LocalSettings(Settings):
    """Settings variant that never reads the local .env file during tests."""

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )


def test_default_settings() -> None:
    settings = LocalSettings()

    assert settings.app_name == "Market Intel API"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.database_url == "sqlite:///./market_intel.db"
    assert settings.alpaca_api_key is None


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "Market Intel Test API")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "true")

    settings = LocalSettings()

    assert settings.app_name == "Market Intel Test API"
    assert settings.environment == "testing"
    assert settings.debug is True
