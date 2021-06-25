import pytest
from src.app import app
from src.drivers import Driver

# test data files
DATA_PATH = 'test_data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'

@pytest.fixture
def client():
    """Client used for testing"""
    return app.test_client()


@pytest.fixture
def build_report():
    """Build report for rendering pages with content before testing"""
    Driver.build_report(data_path=DATA_PATH)