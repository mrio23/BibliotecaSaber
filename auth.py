import hashlib
import hmac
import secrets
from getpass import getpass

import streamlit as st

ITERACOES_HASH = 600_000

PAGINAS_POR_PERFIL = {
    "bibliotecaria": {
        "Início",
        "Alunos",
        "Livros",
        "Cadastrar livro",
        "Empréstimos",
    },
    "coordenacao": {
        "Início",
        "Alunos",
        "Livros",
        "Cadastrar livro",
        "Empréstimos",
        "Auditoria",
    },
}

def gerar_hash_senha(senha):
    """Gera um hash PBKDF2 com salt aleatório."""
    
    salt = secrets.token_hex(16)
    
    hash_senha = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        ITERACOES_HASH,
    ).hex()
    
    return f"{salt}${hash_senha}"

def verificar_senha(senha, senha_hash):
    """Confere a senha usando o hash armazenado."""
    try:
        salt, hash_armazenado = senha_hash.split("$",1)
        
        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt.encode("utf-8"),
            ITERACOES_HASH,
        ).hex()
        
        return hmac.compare_digest(hash_calculado, hash_armazenado)
    
    except (ValueError, AttributeError):
        return False


def autenticar_usuario(email, senha):
    try:
        usuarios = st.secrets["usuarios"]
    except Exception as erro:
        print(f"ERRO AO LER USUARIOS: {type(erro).__name__}")
        return None

    email_digitado = email.strip().lower()

    print("=== DIAGNÓSTICO DE LOGIN ===")
    print(f"E-mail digitado: {email_digitado}")
    print(f"Contas configuradas: {list(usuarios.keys())}")

    for identificador, dados in usuarios.items():
        email_configurado = str(
            dados.get("email", "")
        ).strip().lower()

        perfil = str(
            dados.get("perfil", "")
        ).strip().lower()

        senha_hash = str(dados.get("senha_hash", ""))

        print(
            f"Conta: {identificador} | "
            f"E-mail confere: {email_digitado == email_configurado} | "
            f"Perfil: {perfil} | "
            f"Hash presente: {bool(senha_hash)}"
        )

        if (
            email_digitado == email_configurado
            and perfil in PAGINAS_POR_PERFIL
            and verificar_senha(senha, senha_hash)
        ):
            print("Resultado: autenticação válida.")
            return {
                "identificador": identificador,
                "email": email_configurado,
                "perfil": perfil,
            }

    print("Resultado: nenhuma conta correspondeu.")
    return None

# def autenticar_usuario(email, senha):
#     """Retorna os dados dos usuários se as credenciais forem válidas."""
    
#     try:
#         usuarios = st.secrets["usuarios"]
#     except (KeyError, FileNotFoundError):
#         return None
    
#     email = email.strip().lower()
    
#     for identificador, dados in usuarios.items():
#         email_configurado = str(dados.get("email", "")).strip().lower()
#         senha_hash = str(dados.get("senha_hash", ""))
#         perfil = str(dados.get("perfil", "")).strip().lower()
        
#         if (
#             email == email_configurado
#             and perfil in PAGINAS_POR_PERFIL
#             and verificar_senha(senha, senha_hash)
#         ):
#             return {
#                 "identificador": identificador,
#                 "email": email_configurado,
#                 "perfil": perfil,
#             }
            
#         return None

def paginas_permitidas(perfil):
    return PAGINAS_POR_PERFIL.get(perfil, set())

if __name__ == "__main__":
    
    senha = getpass("Digite a senha que deseja cadastrar: ")
    confirmacao = getpass("Confirme a senha: ")
    
    if not senha:
        print("A senha não pode ficar vazia.")
    elif senha != confirmacao:
        print("As senhas não coincidem.")
    else:
        print("\nHash para colocar nos Secrets:\n")
        print(gerar_hash_senha(senha))