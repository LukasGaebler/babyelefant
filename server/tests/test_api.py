import os
import tempfile
import json

import pytest
from sqlalchemy.sql import text

from main import create_app
from flask import session

@pytest.fixture(name="app")
def fixture_app():
    _,app = create_app(test=True)
    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
     
@pytest.fixture(name="session")
def test_login(client):
    response = client.post("/api/auth/login",  json={
        "username":"admin",
        "password":"1234"
    })
    assert response.status_code == 200
    yield response.json.get('token')

def test_events(client,session):
    request = client.get('/api/events/', headers={"Authorization": 'Bearer ' + session})
    assert request.status_code == 200
    assert request.json is not None
    data = request.json.get('data')
    assert len(data) == 1

def test_user(client,session):
    request = client.get('/api/users/', headers={"Authorization": 'Bearer ' + session})
    assert request.status_code == 200
    assert request.json is not None
    data = request.json.get('data')
    assert len(data) == 1
    assert data[0].get('u_name') == 'admin'

def test_cameras(client,session):
    request = client.get('/api/cameras/1', headers={"Authorization": 'Bearer ' + session})
    assert request.status_code == 200
    assert request.json is not None
    data = request.json.get('cameras')
    assert len(data) == 1
    assert data[0].get('c_id') == 1

def test_image(client,session):
    request = client.get('/api/video_feed/1', headers={"Authorization": 'Bearer ' + session})

    assert request.status_code == 200
    assert request.mimetype == 'image/png'

