from datetime import datetime, timedelta
import pytest
from app import app, get_db_connection, API_SECRET_KEY, hashlib, jwt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_user_consent(client):
    response = client.post('/login', data={"username": "admin", "password": "senha_segura_123", "consent": "on"})
    assert response.status_code == 200
    db = get_db_connection()
    cursor = db.execute("SELECT * FROM user_consent WHERE user_id=1")
    assert cursor.fetchone() is not None

def test_rbac_dashboard(client):
    token = jwt.encode({"username": "user", "role": "user", "exp": datetime.utcnow() + timedelta(minutes=30)}, API_SECRET_KEY, algorithm="HS256")
    response = client.get(f'/dashboard?token={token}')
    assert response.status_code == 403  # Acesso negado
