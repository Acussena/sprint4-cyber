from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
import os
import pytest
import io

# ---------------- Configurações ----------------
API_SECRET_KEY = "super-secret-and-unsafe-key-12345"
DB_PATH = "database.db"

app = Flask(__name__)

# ---------------- Banco de Dados ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db_connection()
    # Tabela de usuários
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # Tabela de consentimento LGPD
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_consent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consent_type TEXT NOT NULL,
            consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Inserir usuário admin se não existir
    cursor = db.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone() is None:
        password = "senha_segura_123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", password_hash))
    db.commit()
    db.close()

# Inicializa o banco
init_db()

# ---------------- Testes automáticos ----------------
def run_tests():
    print("🔹 Iniciando testes unitários...")
    result = pytest.main(["-v", "--maxfail=1", "--disable-warnings", "tests/"])
    if result == 0:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")
    return result

# ---------------- Rotas ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    consent = request.form.get("consent")

    if not username or not password:
        return jsonify({"message": "Username ou senha não fornecidos"}), 400

    db = get_db_connection()
    cursor = db.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if not user or password_hash != user["password_hash"]:
        db.close()
        return jsonify({"message": "Usuário ou senha incorretos"}), 401

    # Registrar consentimento LGPD
    if consent == "true" or consent == "on":
        db.execute("INSERT INTO user_consent (user_id, consent_type) VALUES (?, ?)", (user["id"], "geral"))
        db.commit()

    db.close()

    # Define role
    role = "admin" if username == "admin" else "user"

    # Cria token JWT
    token = jwt.encode(
        {"username": username, "role": role, "exp": datetime.utcnow() + timedelta(minutes=30)},
        API_SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"message": f"Login bem-sucedido para {username}", "token": token})

@app.route("/dashboard")
def dashboard():
    token = request.args.get("token")
    if not token:
        return "Token não fornecido", 401
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=["HS256"])

        # Apenas admin pode acessar
        if payload.get("role") != "admin":
            return "Acesso negado", 403

        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        reports = {
            "pytest": os.path.join(reports_dir, "pytest.log"),
            "snyk": os.path.join(reports_dir, "snyk_report.html"),
            "codeql": os.path.join(reports_dir, "codeql_report.html"),
            "dast": os.path.join(reports_dir, "zap_report.html")
        }

        report_files = {k: v for k, v in reports.items() if os.path.exists(v)}

        return render_template("dashboard.html", reports=report_files, username=payload["username"], token=token)
    except jwt.ExpiredSignatureError:
        return "Token expirado", 401
    except jwt.InvalidTokenError:
        return "Token inválido", 401

# ---------------- Exclusão de conta ----------------
@app.route("/delete_account", methods=["DELETE"])
def delete_account():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Token não fornecido."}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        if not username:
            return jsonify({"message": "Token inválido: nome de usuário ausente."}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expirado. Faça login novamente."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido."}), 401

    db = get_db_connection()
    db.execute("DELETE FROM users WHERE username = ?", (username,))
    db.commit()
    db.close()

    return jsonify({"message": f"Conta de '{username}' excluída com sucesso."}), 200

@app.route("/welcome")
def welcome():
    name = request.args.get("name", "Visitante")
    safe_name = name.replace("<", "&lt;").replace(">", "&gt;")
    return f"Bem-vindo(a), {safe_name}!"

@app.route("/user_info")
def user_info():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"message": "Parâmetro 'username' é obrigatório"}), 400

    db = get_db_connection()
    cursor = db.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "password_hash": user["password_hash"]
        })
    else:
        return jsonify({"message": "Usuario nao encontrado"}), 404

# ---------------- Main ----------------
if __name__ == "__main__":
    run_tests()
    app.run(debug=True)
