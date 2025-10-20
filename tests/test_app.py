import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_welcome_sanitization(client):
    malicious_input = "<script>alert(1)</script>"
    response = client.get(f'/welcome?name={malicious_input}')
    assert b"<script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data

def test_login_success(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'senha_segura_123'})
    assert response.status_code == 200
    assert b'token' in response.data

def test_login_fail(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'senha_errada'})
    assert response.status_code == 401
