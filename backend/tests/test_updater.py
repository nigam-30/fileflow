import pytest
from src.core.updater import parse_version, check_for_updates

def test_parse_version():
    assert parse_version("1.0.3") == (1, 0, 3)
    assert parse_version("v1.0.3") == (1, 0, 3)
    assert parse_version("v1.0.4") > parse_version("1.0.3")
    assert parse_version("2.0.0") > parse_version("1.9.9")
    assert parse_version("1.1.0") > parse_version("1.0.9")
    assert parse_version("1.0.3") == parse_version("1.0.3")

def test_check_for_updates_structure():
    # Calling check_for_updates returns valid dictionary with all keys
    res = check_for_updates(force=False)
    assert isinstance(res, dict)
    assert "update_available" in res
    assert "current_version" in res
    assert "latest_version" in res
    assert "download_url" in res
    assert "release_url" in res
    assert res["current_version"] == "1.0.3"
