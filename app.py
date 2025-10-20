from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
import os
import pytest
import io

API_SECRET_KEY = "super-secret-and-unsafe-key-12345"

app = Flask(__name__)
DB_PATH = "database.db"

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
    # Inserir usuário admin de teste
    cursor = db.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone() is None:
        password = "senha_segura_123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", password_hash))
    db.commit()
    db.close()

# Inicializa banco
init_db()

# ---------------- Função para rodar testes ----------------
def run_tests():
    print("🔹 Iniciando testes unitários...")

    # Executa o pytest e captura o resultado via código de saída
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

    if not user:
        db.close()
        return jsonify({"message": "Usuário não encontrado"}), 404

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user["password_hash"]:
        db.close()
        return jsonify({"message": "Senha incorreta"}), 401

    # Registrar consentimento LGPD
    if consent == "true" or consent == "on":
        db.execute("INSERT INTO user_consent (user_id, consent_type) VALUES (?, ?)", (user["id"], "geral"))
        db.commit()

    db.close()

    # Criar token JWT
    token = jwt.encode(
        {"username": username, "role": "user", "exp": datetime.utcnow() + timedelta(minutes=30)},
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
        
        # Permitir apenas admin no dashboard
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

        return render_template("dashboard.html", reports=report_files, username=payload["username"])
    except jwt.ExpiredSignatureError:
        return "Token expirado", 401
    except jwt.InvalidTokenError:
        return "Token inválido", 401

@app.route("/welcome")
def welcome():
    name = request.args.get("name", "Visitante")
    # Proteção simples contra XSS
    safe_name = name.replace("<", "&lt;").replace(">", "&gt;")
    return f"Bem-vindo(a), {safe_name}!"

@app.route("/user_info")
def user_info():
    user_id = request.args.get("id", "")
    db = get_db_connection()
    cursor = db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    db.close()

    if user:
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "password_hash": user["password_hash"]
        })
    else:
        return "Usuário não encontrado", 404

# ---------------- Main ----------------
if __name__ == "__main__":
    # Rodar testes antes de iniciar o servidor
    run_tests()
    app.run(debug=True)
