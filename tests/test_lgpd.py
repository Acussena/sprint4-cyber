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

def test_user_deletion(client):
    # Cria usuário de teste
    username = "lgpd_delete_test"
    password = "senha_teste"
    db = get_db_connection()
    if not db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        db.commit()
    db.close()
    
    response = client.post('/login', data={"username": username, "password": password})
    token = jwt.decode(response.json['token'], API_SECRET_KEY, algorithms=["HS256"])['username']
    
    res_delete = client.delete('/delete_account', headers={'Authorization': f'Bearer {response.json["token"]}'})
    assert res_delete.status_code == 200
    
    db = get_db_connection()
    user_check = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    db.close()
    assert user_check is None
