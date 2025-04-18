# backend test file

import pytest
import json
from main import app as flask_app  # updated from 'app' to 'main'

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'ok'
