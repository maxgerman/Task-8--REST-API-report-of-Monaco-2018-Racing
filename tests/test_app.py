from flask import session, request, g
from src.app import app


def test_base_template(client):
    """Test that base template is rendered"""
    response = client.get('/', follow_redirects=True)
    assert b'Monaco' in response.data


def test_report_render(build_report, client):
    """Test that data file are parsed and report is rendered"""
    response = client.get('/report')
    assert b'Pierre Gasly' in response.data and b'SCUDERIA TORO ROSSO HONDA' in response.data


def test_list_drivers(build_report, client):
    """Test that data file are parsed and driver list is rendered"""
    response = client.get('/drivers')
    assert b'Lewis Hamilton' in response.data
    assert b'Fernando Alonso' in response.data
    assert b'KRF' in response.data


def test_common_report_ascending(build_report, client):
    """Test that sorting in the report is by the best lap time in the ascending order (faster first)"""
    response = client.get('/report')
    pos1 = response.data.find(b'Vettel')
    pos2 = response.data.find(b'Bottas')
    assert pos1 < pos2


def test_common_report_descending(build_report, client):
    """Test that sorting in the report is by the best lap time in the descending order (slower first)"""
    response = client.get('/report?order=desc')
    pos1 = response.data.find(b'Vettel')
    pos2 = response.data.find(b'Bottas')
    assert pos1 > pos2


def test_session_report_order_switch(build_report, client):
    """Test that session key is stored for current state of report order switch (asc/desc)"""
    with client as c:
        response = c.get('/report?order=desc')
        assert session['report_desc_switch'] is True


def test_list_drivers_ascending(build_report, client):
    """Test default alphabetical sorting in the driver list (ascending)"""
    response = client.get('/drivers')
    pos1 = response.data.find(b'Brendon')
    pos2 = response.data.find(b'Valtteri')
    assert pos1 < pos2


def test_list_drivers_descending(build_report, client):
    """Test the descending alphabetical sorting in the driver list"""
    response = client.get('/drivers?order=desc')
    pos1 = response.data.find(b'Brendon')
    pos2 = response.data.find(b'Valtteri')
    assert pos1 > pos2


def test_session_drivers_order_switch(build_report, client):
    """Test that session key is stored for current state of drivers order switch"""
    with client as c:
        response = c.get('/drivers?order=desc')
        assert session['driver_desc_switch'] is True
