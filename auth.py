import hashlib
import hmac
import secrets
from getpass import getpass

from database.connection import engine
from sqlalchemy import text

import streamlit as st

ITERACOES_HASH = 600_000

PAGINAS_POR_PERFIL = {
    "coordenacao": {
            "Início",
            "Alunos",
            "Livros",
            "Cadastrar livro",
            "Empréstimos",
            "Auditoria",
            "Gerenciar usuários",
        },
    
    "bibliotecaria": {
        "Início",
        "Alunos",
        "Livros",
        "Cadastrar livro",
        "Empréstimos",
    },
    
    "professor": {
        "Início",
        "Livros",
    }
}

def cadastrar_usuario(nome, email, senha):
    """Cadastra um novo usuário no banco de dados."""
    
    nome = nome.strip()
    email = email.strip().lower()
    
    #  Valida os campos obrigatórios.
    if not nome or not email or not senha:
        return False, "Preencha todos os campos."

    # Verifica o formato básico do e-mail.
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Informe um e-mail válido."

    # Verifica o tamanho mínimo da senha.
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    
    # Gera o hash da senha antes de armazená-la.
    senha_hash = gerar_hash_senha(senha)
    
    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text("""
                     INSERT INTO usuarios (
                         nome,
                         email,
                         senha_hash,
                         perfil,
                         ativo
                     )
                     VALUES (
                         :nome,
                         :email,
                         :senha_hash,
                         :perfil,
                         :ativo
                     )
                     ON CONFLICT (email) DO NOTHING
                     RETURNING id
                     """),
                {
                    "nome": nome,
                    "email": email,
                    "senha_hash": senha_hash,
                    "perfil": "pendente",
                    "ativo": False,
                },
            )
            
            usuario_criado = resultado.fetchone()
            
            if usuario_criado is None:
                return False, "Este e-mail já está cadastrado."
            
        return True, (
            "Conta criada com sucesso! "
            "Aguarde a aprovação da coordenação para acessar o sistema."
        )
        
    except Exception:
        return False, (
            "Não foi possível criar a conta. "
            "Verifique a configuração do sistema ou tente novamente."
        )



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
    """Autentica um usuário cadastrado no PostgreSQL."""

    email = email.strip().lower()

    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text("""
                    SELECT
                        id,
                        nome,
                        email,
                        senha_hash,
                        perfil,
                        ativo
                    FROM usuarios
                    WHERE LOWER(email) = :email
                    LIMIT 1
                """),
                {"email": email},
            )

            usuario = resultado.mappings().first()

        if usuario is None:
            return None

        if not usuario["ativo"]:
            return None

        perfil = str(usuario["perfil"]).strip().lower()

        if perfil not in PAGINAS_POR_PERFIL:
            return None

        if not verificar_senha(senha, usuario["senha_hash"]):
            return None

        return {
            "identificador": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": perfil,
        }

    except Exception:
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
    permissoes = {
        "professor": [
            "Início",
            "Livros",
        ],
        
        "bibliotecaria": [
            "Início",
            "Alunos",
            "Livros",
            "Cadastrar Livro",
            "Empréstimos",
        ],
        
        "coordenacao": [
            "Início",
            "Alunos",
            "Livros",
            "Cadastrar livro",
            "Empréstimos",
            "Auditoria",
            "Gerenciar usuários",
        ],
    }
    
    return permissoes.get(perfil, [])

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


def listar_usuarios_pendentes():
    """Lista as contas que aguardam aprovação do coordenador."""
    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text(
                    """
                    SELECT id, nome, email, criado_em
                    FROM usuarios
                    WHERE ativo = FALSE
                    ORDER BY criado_em ASC
                    """)
            )
            
            return [dict(usuario) for usuario in resultado.mappings()]
        
    except Exception:
        return None
    

def aprovar_usuario(usuario_id, perfil):
    """Aprova um usuário pendente e define seu perfil."""

    # Aceita somente os perfis permitidos.
    perfis_validos = {"bibliotecaria", "professor"}

    if perfil not in perfis_validos:
        return False, "O perfil selecionado não é válido."

    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text("""
                    UPDATE usuarios
                    SET perfil = :perfil,
                        ativo = TRUE
                    WHERE id = :usuario_id
                      AND ativo = FALSE
                      AND perfil = 'pendente'
                    RETURNING id
                """),
                {
                    "usuario_id": usuario_id,
                    "perfil": perfil,
                },
            )

            usuario_aprovado = resultado.fetchone()

            if usuario_aprovado is None:
                return (
                    False,
                    "Usuário não encontrado, já aprovado "
                    "ou não está pendente.",
                )

        return True, "Usuário aprovado com sucesso!"

    except Exception:
        return False, "Não foi possível aprovar o usuário."