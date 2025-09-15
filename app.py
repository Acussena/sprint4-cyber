from flask import Flask, request, make_response
import sqlite3
import hashlib

app = Flask(__name__)

# VULNERABILIDADE 1: EXPOSIÇÃO DE DADOS SENSÍVEIS
# Uma chave de API ou senha nunca deve estar diretamente no código.
# Ferramentas SAST são excelentes em encontrar esse tipo de segredo "hardcoded".
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
    # A query SQL está sendo montada com concatenação de strings.
    # Um atacante pode inserir código SQL malicioso nos campos de usuário e senha.
    # Ex: username = ' OR 1=1; --
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
    # MD5 é um algoritmo de hash considerado quebrado e inseguro para senhas.
    # Ferramentas SAST alertam sobre o uso de funções criptográficas fracas.
    user_id_hash = hashlib.md5(user_id.encode()).hexdigest()

    return f"Hash MD5 do ID do usuário: {user_id_hash}"


@app.route('/welcome')
def welcome():
    # VULNERABILIDADE 4: CROSS-SITE SCRIPTING (XSS) REFLETIDO
    # O nome do usuário, vindo diretamente da URL, é renderizado na página
    # sem qualquer tipo de validação ou "escape". Um atacante pode injetar
    # scripts maliciosos na URL. Ex: /welcome?name=<script>alert('XSS')</script>
    name = request.args.get('name', 'Visitante')
    html_response = f"<h1>Bem-vindo, {name}!</h1>"
    response = make_response(html_response, 200)

    # Prática insegura que ferramentas DAST (próxima tarefa) pegariam, mas algumas regras SAST também podem sinalizar.
    response.headers['X-XSS-Protection'] = '0' 
    return response

if __name__ == '__main__':
    # O modo de debug NUNCA deve ser usado em produção. Ferramentas SAST alertam sobre isso.
    app.run(debug=True)