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
            "Cadastrar livro",
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


def listar_usuarios_cadastrados():
    """Lista usuários ativos para a coordenação administrar."""
    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text("""
                    SELECT id, nome, email, perfil, ativo, criado_em
                    FROM usuarios
                    WHERE ativo = TRUE
                    ORDER BY nome ASC
                """)
            )
            return [dict(usuario) for usuario in resultado.mappings()]
    except Exception:
        return None


def atualizar_perfil_usuario(usuario_id, perfil):
    """Atualiza o perfil de um usuário ativo, sem conceder coordenação."""
    perfis_validos = {"bibliotecaria", "professor"}

    if perfil not in perfis_validos:
        return False, "O perfil selecionado não é válido."

    try:
        with engine.begin() as conn:
            resultado = conn.execute(
                text("""
                    UPDATE usuarios
                    SET perfil = :perfil
                    WHERE id = :usuario_id
                      AND ativo = TRUE
                      AND perfil IN ('bibliotecaria', 'professor')
                    RETURNING id
                """),
                {"usuario_id": usuario_id, "perfil": perfil},
            )

            if resultado.fetchone() is None:
                return False, (
                    "Usuário não encontrado ou perfil não pode ser alterado."
                )

        return True, "Perfil atualizado com sucesso!"
    except Exception:
        return False, "Não foi possível atualizar o perfil do usuário."


def excluir_usuario(usuario_id, identificador_atual):
    """Exclui uma conta, protegendo a própria conta e o último coordenador."""
    if str(usuario_id) == str(identificador_atual):
        return False, "Você não pode excluir a própria conta."

    try:
        with engine.begin() as conn:
            usuario = conn.execute(
                text("""
                    SELECT id, perfil, ativo
                    FROM usuarios
                    WHERE id = :usuario_id
                    FOR UPDATE
                """),
                {"usuario_id": usuario_id},
            ).mappings().first()

            if usuario is None:
                return False, "Usuário não encontrado."

            if usuario["perfil"] == "coordenacao" and usuario["ativo"]:
                total_coordenadores = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM usuarios
                        WHERE perfil = 'coordenacao'
                          AND ativo = TRUE
                    """)
                ).scalar_one()

                if total_coordenadores <= 1:
                    return False, (
                        "Não é possível excluir a última conta ativa "
                        "da coordenação."
                    )

            conn.execute(
                text("DELETE FROM usuarios WHERE id = :usuario_id"),
                {"usuario_id": usuario_id},
            )

        return True, "Usuário excluído com sucesso."
    except Exception:
        return False, (
            "Não foi possível excluir o usuário. "
            "Verifique se há vínculos no banco de dados."
        )

# ============================================================
# SESSÕES PERSISTENTES (30 DIAS)
# ============================================================

DURACAO_SESSAO_DIAS = 30


@st.cache_resource
def _garantir_tabela_sessoes():
    """Garante o esquema de sessões uma vez por processo da aplicação.

    O resultado é compartilhado entre reruns e sessões do Streamlit para
    evitar executar DDL (CREATE TABLE/INDEX) a cada interação do usuário.
    """
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessoes_usuarios (
                token_hash VARCHAR(64) PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expira_em TIMESTAMPTZ NOT NULL,
                ultimo_acesso_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sessoes_usuarios_usuario
            ON sessoes_usuarios (usuario_id)
        """))


def criar_sessao_persistente(usuario_id):
    """Gera token aleatório; somente seu hash fica armazenado no banco."""
    try:
        _garantir_tabela_sessoes()
        token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO sessoes_usuarios
                    (token_hash, usuario_id, expira_em)
                VALUES
                    (:token_hash, :usuario_id,
                     NOW() + (:dias * INTERVAL '1 day'))
            """), {
                "token_hash": token_hash,
                "usuario_id": str(usuario_id),
                "dias": DURACAO_SESSAO_DIAS,
            })

        return token
    except Exception:
        return None


def validar_sessao_persistente(token):
    """Valida token, expiração e situação atual do usuário no banco."""
    if not token or not isinstance(token, str):
        return None

    try:
        _garantir_tabela_sessoes()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        with engine.begin() as conn:
            usuario = conn.execute(text("""
                SELECT u.id, u.nome, u.email, u.perfil, u.ativo
                FROM sessoes_usuarios s
                JOIN usuarios u ON CAST(u.id AS TEXT) = s.usuario_id
                WHERE s.token_hash = :token_hash
                  AND s.expira_em > NOW()
                  AND u.ativo = TRUE
                LIMIT 1
            """), {"token_hash": token_hash}).mappings().first()

            if usuario is None:
                conn.execute(text("""
                    DELETE FROM sessoes_usuarios
                    WHERE token_hash = :token_hash
                """), {"token_hash": token_hash})
                return None

            perfil = str(usuario["perfil"]).strip().lower()
            if perfil not in PAGINAS_POR_PERFIL:
                conn.execute(text("""
                    DELETE FROM sessoes_usuarios
                    WHERE token_hash = :token_hash
                """), {"token_hash": token_hash})
                return None

            conn.execute(text("""
                UPDATE sessoes_usuarios
                SET ultimo_acesso_em = NOW()
                WHERE token_hash = :token_hash
            """), {"token_hash": token_hash})

            return {
                "identificador": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "perfil": perfil,
            }
    except Exception:
        return None


def encerrar_sessao_persistente(token):
    """Invalida no banco uma sessão persistente ao sair da conta."""
    if not token or not isinstance(token, str):
        return

    try:
        _garantir_tabela_sessoes()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM sessoes_usuarios
                WHERE token_hash = :token_hash
            """), {"token_hash": token_hash})
    except Exception:
        pass

def garantir_coordenadora_inicial():
    """
    Cria a conta inicial da coordenação apenas se ainda não existir nenhuma.
    As credenciais iniciais devem ser configuradas em st.secrets/ambiente.
    Nunca substitui e-mail ou senha de uma conta de coordenação já existente.
    """
    try:
        nome = str(st.secrets.get("COORDENADORA_NOME", "Coordenação Biblioteca Saber")).strip()
        email = str(st.secrets["COORDENADORA_EMAIL"]).strip().lower()
        senha = str(st.secrets["COORDENADORA_SENHA"])

        if not email or not senha or len(senha) < 8:
            return False, "As credenciais iniciais da coordenação não estão configuradas corretamente."

        with engine.begin() as conn:
            existe = conn.execute(text("""
                SELECT id
                FROM usuarios
                WHERE perfil = 'coordenacao'
                LIMIT 1
            """)).first()

            if existe:
                return True, "A conta da coordenação já existe."

            senha_hash = gerar_hash_senha(senha)
            conn.execute(text("""
                INSERT INTO usuarios (nome, email, senha_hash, perfil, ativo)
                VALUES (:nome, :email, :senha_hash, 'coordenacao', TRUE)
            """), {
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
            })

        return True, "Conta inicial da coordenação criada."
    except Exception:
        return False, (
            "Não foi possível verificar a conta inicial da coordenação. "
            "Confira as configurações e a conexão com o banco de dados."
        )

