import pytest
from src.drivers import Driver
from src.app import app, api
from src.api import DriverApi, DriversListApi, ReportApi


# test data files
DATA_PATH = 'test_data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'


@pytest.fixture
def client():
    """Client used for testing"""
    app.testing = True
    return app.test_client()


@pytest.fixture
def build_report():
    """Build report for rendering pages and APIs before testing"""
    Driver.build_report(data_path=DATA_PATH)


# @pytest.fixture
# def api_add_resources():
#     """Adding api resources to the app"""
#     api.add_resource(DriversListApi, '/api/v1/drivers/')
#     api.add_resource(DriverApi, '/api/v1/drivers/<driver_id>/')
#     api.add_resource(ReportApi, '/api/v1/report/')