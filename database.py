import sqlite3
import datetime
import os

# Configurações básicas
DB_NAME = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def check_limit_and_status(email):
    """Retorna sempre Premium e sem limites para o dono."""
    return True, False, ""

def get_user_status(email):
    """A função que faltava: retorna sempre premium para evitar o erro de atributo."""
    return "premium"

def add_user(email, status='premium', order_id=None):
    """Sempre aceita a adição de novos usuários como premium."""
    return True

def increment_usage(email):
    """Ignora a contagem de uso."""
    return True

def get_user(email):
    """Retorna um dicionário de usuário fictício se o sistema pedir."""
    return {"email": email, "status": "premium"}

def initialize_db():
    """Garante que o banco de dados seja reconhecido se o código chamar no início."""
    pass