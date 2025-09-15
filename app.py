from flask import Flask, request, make_response
import sqlite3
import hashlib

app = Flask(__name__)

# VULNERABILIDADE 1: EXPOSIÇÃO DE DADOS SENSÍVEIS
API_SECRET_KEY = "super-secret-and-unsafe-key-12345"

@app.route('/')
def home():
    return "Bem-vindo à aplicação de teste de segurança!"

@app.route('/login', methods=['POST'])
def login():
    """
    Esta função de login é intencionalmente vulnerável a Injeção de SQL.
    """
    username = request.form.get('username')
    password = request.form.get('password')

    # VULNERABILIDADE 2: INJEÇÃO DE SQL (SQL INJECTION)
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        if user:
            return "Login bem-sucedido!", 200
        else:
            return "Credenciais inválidas.", 401
    except Exception as e:
        return str(e), 500

@app.route('/user_info')
def user_info():
    user_id = request.args.get('id')

    # VULNERABILIDADE 3: USO INSEGURO DE FUNÇÕES (HASH FRACO)
    user_id_hash = hashlib.md5(user_id.encode()).hexdigest()

    return f"Hash MD5 do ID do usuário: {user_id_hash}"


@app.route('/welcome')
def welcome():
    # VULNERABILIDADE 4: CROSS-SITE SCRIPTING (XSS) REFLETIDO
    name = request.args.get('name', 'Visitante')
    html_response = f"<h1>Bem-vindo, {name}!</h1>"
    response = make_response(html_response, 200)

    response.headers['X-XSS-Protection'] = '0' 
    return response

if __name__ == '__main__':
    app.run(debug=True)