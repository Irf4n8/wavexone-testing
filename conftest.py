"""
Pytest configuration and session fixtures for WavexOne QA.
"""
import pytest
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger


@pytest.fixture(scope="session")
def ct_master():
    cfg = WavexSettings.MASTERS["copy_trading"]
    sess = WavexUserSession(cfg["email"], cfg["password"], cfg["name"])
    assert sess.authenticate(), f"Failed to authenticate {cfg['name']}"
    yield sess


@pytest.fixture(scope="session")
def mam_master():
    cfg = WavexSettings.MASTERS["mam"]
    sess = WavexUserSession(cfg["email"], cfg["password"], cfg["name"])
    assert sess.authenticate(), f"Failed to authenticate {cfg['name']}"
    yield sess


@pytest.fixture(scope="session")
def pamm_master():
    cfg = WavexSettings.MASTERS["pamm"]
    sess = WavexUserSession(cfg["email"], cfg["password"], cfg["name"])
    assert sess.authenticate(), f"Failed to authenticate {cfg['name']}"
    yield sess

