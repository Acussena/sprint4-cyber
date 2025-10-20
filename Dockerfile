# Usar Python 3.9 como base
FROM python:3.9-slim

# Setar diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY requirements.txt .
COPY app.py .
COPY tests/ ./tests

# Instalar dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest pytest-cov PyJWT

# Expõe a porta 5000
EXPOSE 5000

# Comando para rodar o Flask
CMD ["python", "app.py"]
