import streamlit as st
from datetime import date

from main import (
    cadastrar_livro,
    listar_livros,
    livro_possui_emprestimos,
    excluir_livro,
    cadastrar_aluno,
    listar_alunos,
    aluno_possui_emprestimos,
    excluir_aluno,
    listar_auditoria,
    registrar_emprestimo,
    listar_emprestimos,
    registrar_devolucao,
    contar_livros,
    contar_alunos,
    contar_emprestimos_ativos,
    contar_emprestimos_atrasados,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Biblioteca Saber",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="auto",
)


# ============================================================
# CSS
# ============================================================

def carregar_css():
    with open("style.css", "r", encoding="utf-8") as arquivo:
        st.markdown(
            f"<style>{arquivo.read()}</style>",
            unsafe_allow_html=True,
        )


carregar_css()


# ============================================================
# COMPONENTES VISUAIS
# ============================================================

def cabecalho_pagina(titulo, descricao, icone="📚"):
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-icon">{icone}</div>
            <div>
                <div class="page-kicker">BIBLIOTECA SABER</div>
                <h1>{titulo}</h1>
                <p>{descricao}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def secao(titulo, descricao=None, icone=""):
    descricao_html = f'<p>{descricao}</p>' if descricao else ""
    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <h2>{icone} {titulo}</h2>
                {descricao_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mensagem_vazia(icone, titulo, descricao):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-icon">{icone}</div>
            <h3>{titulo}</h3>
            <p>{descricao}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_status(status, data_devolucao=None):
    hoje = date.today()

    if status == "DEVOLVIDO":
        return '<span class="status-badge status-returned">● DEVOLVIDO</span>'

    if status == "ATRASADO":
        return '<span class="status-badge status-late">● ATRASADO</span>'

    if status == "ATIVO":
        if data_devolucao is not None and data_devolucao < hoje:
            return '<span class="status-badge status-late">● ATRASADO</span>'
        return '<span class="status-badge status-active">● ATIVO</span>'

    if status == "CANCELADO":
        return '<span class="status-badge status-cancelled">● CANCELADO</span>'

    return f'<span class="status-badge status-neutral">● {status}</span>'


# ============================================================
# SIDEBAR
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"

st.sidebar.markdown(
    """
    <div class="brand-block">
        <div class="brand-logo">📚</div>
        <div class="brand-name">BIBLIOTECA <span>SABER</span></div>
        <div class="brand-description">Sistema de Gestão da Biblioteca Escolar</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-label">NAVEGAÇÃO</div>', unsafe_allow_html=True)

opcoes_menu = {
    "Início": "🏠  Início",
    "Alunos": "👥  Alunos",
    "Livros": "📚  Livros",
    "Cadastrar livro": "＋  Cadastrar livro",
    "Empréstimos": "📖  Empréstimos",
    "Auditoria": "📋  Auditoria",
}

for chave, nome_exibicao in opcoes_menu.items():
    classe = "menu-active" if st.session_state.pagina == chave else ""

    st.sidebar.markdown(
        f'<div class="menu-state {classe}"></div>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        nome_exibicao,
        key=f"menu_{chave}",
        use_container_width=True,
    ):
        st.session_state.pagina = chave
        st.rerun()

st.sidebar.markdown(
    """
    <div class="sidebar-bottom">
        <div class="sidebar-school">AMBIENTE ESCOLAR</div>
        <div class="sidebar-year">Biblioteca Saber • 2026</div>
    </div>
    """,
    unsafe_allow_html=True,
)

opcao = st.session_state.pagina


# ============================================================
# INÍCIO
# ============================================================

if opcao == "Início":
    cabecalho_pagina(
        "Olá! Seja bem-vindo.",
        "Acompanhe o acervo e as principais movimentações da biblioteca.",
        "🏫",
    )

    try:
        quantidade_livros = contar_livros()
        quantidade_alunos = contar_alunos()
        emprestimos_ativos = contar_emprestimos_ativos()
        emprestimos_atrasados = contar_emprestimos_atrasados()
        erro_indicadores = False
    except Exception:
        quantidade_livros = 0
        quantidade_alunos = 0
        emprestimos_ativos = 0
        emprestimos_atrasados = 0
        erro_indicadores = True

    if erro_indicadores:
        st.warning(
            "Não foi possível atualizar os indicadores no momento. "
            "Tente novamente mais tarde."
        )

    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)

    indicadores = [
        ("📚", "Livros", quantidade_livros, "Total cadastrados", "blue"),
        ("👥", "Alunos", quantidade_alunos, "Total cadastrados", "navy"),
        ("📖", "Empréstimos ativos", emprestimos_ativos, "Atualmente emprestados", "blue"),
        ("⚠", "Atrasados", emprestimos_atrasados, "Precisam de atenção", "red"),
    ]

    cols = st.columns(4)
    for coluna, (icone, titulo, valor, descricao, classe) in zip(cols, indicadores):
        with coluna:
            st.markdown(
                f"""
                <div class="metric-card metric-{classe}">
                    <div class="metric-top">
                        <div class="metric-icon">{icone}</div>
                        <div class="metric-dot"></div>
                    </div>
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value">{valor}</div>
                    <div class="metric-description">{descricao}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="home-spacer"></div>', unsafe_allow_html=True)

    secao("Acesso rápido", "Encontre rapidamente uma área do sistema.", "⚡")

    atalhos = [
        ("📚", "Consultar acervo", "Visualize os livros cadastrados.", "Livros"),
        ("👥", "Alunos", "Consulte os usuários da biblioteca.", "Alunos"),
        ("📖", "Empréstimos", "Registre e acompanhe empréstimos.", "Empréstimos"),
    ]

    cols = st.columns(3)
    for coluna, (icone, titulo, descricao, destino) in zip(cols, atalhos):
        with coluna:
            st.markdown(
                f"""
                <div class="quick-card">
                    <div class="quick-icon">{icone}</div>
                    <div>
                        <h3>{titulo}</h3>
                        <p>{descricao}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Acessar {titulo.lower()}",
                key=f"atalho_{destino}",
                use_container_width=True,
            ):
                st.session_state.pagina = destino
                st.rerun()


# ============================================================
# ALUNOS
# ============================================================

elif opcao == "Alunos":
    cabecalho_pagina(
        "Alunos",
        "Cadastre e consulte os usuários da biblioteca escolar.",
        "👥",
    )

    secao("Cadastrar aluno", "Adicione um novo aluno ao sistema.", "＋")

    form_col1, form_col2 = st.columns([2, 1])
    with form_col1:
        nome = st.text_input("Nome do aluno", placeholder="Digite o nome completo")
    with form_col2:
        matricula = st.text_input("Matrícula", placeholder="Digite a matrícula")

    if st.button("Cadastrar aluno", use_container_width=True, key="cadastrar_aluno"):
        if not nome or not matricula:
            st.warning("Preencha os campos Nome e matrícula.")
        else:
            try:
                cadastrar_aluno(nome, matricula)
                st.success("Aluno cadastrado com sucesso!")
                st.rerun()
            except Exception:
                st.error(
                    "Não foi possível cadastrar o aluno no momento. "
                    "Tente novamente mais tarde."
                )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    secao("Alunos cadastrados", "Lista dos usuários registrados no sistema.", "👥")

    try:
        alunos = listar_alunos()
        if alunos:
            for aluno in alunos:
                aluno_id, nome_aluno, matricula_aluno = aluno[0], aluno[1], aluno[2]

                col_card, col_action = st.columns([6, 1])
                with col_card:
                    st.markdown(
                        f"""
                        <div class="entity-card">
                            <div class="entity-icon blue-icon">👤</div>
                            <div class="entity-main">
                                <div class="entity-label">ALUNO</div>
                                <h3>{nome_aluno}</h3>
                                <div class="entity-meta">
                                    <span>Matrícula</span>
                                    <strong>{matricula_aluno}</strong>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_action:
                    st.markdown('<div class="action-spacer"></div>', unsafe_allow_html=True)
                    if st.button("🗑️ Excluir", key=f"excluir_aluno_{aluno_id}", use_container_width=True):
                        try:
                            if aluno_possui_emprestimos(aluno_id):
                                st.warning(
                                    f"⚠️ Não é possível excluir o aluno **{nome_aluno}**, "
                                    "pois ele possui um empréstimo ativo."
                                )
                            else:
                                excluir_aluno(aluno_id)
                                st.success(f"Aluno **{nome_aluno}** excluído com sucesso!")
                                st.rerun()
                        except Exception:
                            st.error("Não foi possível excluir o aluno no momento.")
        else:
            mensagem_vazia("👥", "Nenhum aluno cadastrado", "Cadastre o primeiro aluno para começar.")
    except Exception:
        st.error("Não foi possível carregar os alunos no momento. Tente novamente mais tarde.")


# ============================================================
# LIVROS
# ============================================================

elif opcao == "Livros":
    cabecalho_pagina(
        "Acervo de livros",
        "Consulte os títulos disponíveis na biblioteca escolar.",
        "📚",
    )

    secao("Livros cadastrados", "Catálogo atualizado do acervo.", "📖")

    try:
        livros = listar_livros()
        if livros:
            for livro in livros:
                livro_id, titulo, autor, ano_publicacao, quantidade = (
                    livro[0], livro[1], livro[2], livro[3], livro[4]
                )
                disponivel = quantidade > 0
                disponibilidade = "Disponível" if disponivel else "Indisponível"
                status_classe = "available" if disponivel else "unavailable"

                col_card, col_action = st.columns([6, 1])
                with col_card:
                    st.markdown(
                        f"""
                        <div class="book-card">
                            <div class="book-cover">📚</div>
                            <div class="book-main">
                                <div class="entity-label">LIVRO DO ACERVO</div>
                                <h3>{titulo}</h3>
                                <p class="book-author">{autor}</p>
                                <div class="book-details">
                                    <div><span>Ano</span><strong>{ano_publicacao}</strong></div>
                                    <div><span>Exemplares</span><strong>{quantidade}</strong></div>
                                    <div><span>Status</span><strong class="book-status {status_classe}">● {disponibilidade}</strong></div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_action:
                    st.markdown('<div class="action-spacer"></div>', unsafe_allow_html=True)
                    if st.button("🗑️ Excluir", key=f"excluir_livro_{livro_id}", use_container_width=True):
                        try:
                            if livro_possui_emprestimos(livro_id):
                                st.warning(
                                    f"⚠️ Não é possível excluir o livro **{titulo}**, "
                                    "pois ele possui registros de empréstimos."
                                )
                            else:
                                excluir_livro(livro_id)
                                st.success(f"Livro **{titulo}** excluído com sucesso!")
                                st.rerun()
                        except ValueError as erro:
                            st.warning(str(erro))
                        except Exception:
                            st.error("Não foi possível excluir o livro no momento. Tente novamente mais tarde.")
        else:
            mensagem_vazia("📚", "Nenhum livro cadastrado", "Cadastre um livro para começar a formar o acervo.")
    except Exception:
        st.error("Não foi possível consultar os livros no momento. Tente novamente mais tarde.")


# ============================================================
# CADASTRAR LIVRO
# ============================================================

elif opcao == "Cadastrar livro":
    cabecalho_pagina(
        "Cadastrar livro",
        "Adicione uma nova obra ao acervo da biblioteca.",
        "＋",
    )

    secao("Informações do livro", "Preencha os dados básicos da obra.", "📚")

    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título do livro", placeholder="Ex.: Dom Casmurro")
    with col2:
        autor = st.text_input("Autor", placeholder="Ex.: Machado de Assis")

    col3, col4 = st.columns(2)
    with col3:
        ano_publicacao = st.number_input("Ano de publicação", min_value=0, step=1)
    with col4:
        quantidade = st.number_input("Quantidade", min_value=1, step=1)

    if st.button("Cadastrar livro", use_container_width=True, key="cadastrar_livro"):
        if not titulo or not autor:
            st.warning("Preencha o título e o autor.")
        else:
            try:
                cadastrar_livro(titulo, autor, ano_publicacao, quantidade)
                st.success("Livro cadastrado com sucesso!")
            except Exception:
                st.error(
                    "Não foi possível cadastrar o livro no momento. "
                    "Tente novamente mais tarde."
                )


# ============================================================
# EMPRÉSTIMOS
# ============================================================

elif opcao == "Empréstimos":
    cabecalho_pagina(
        "Empréstimos",
        "Registre retiradas, acompanhe prazos e controle devoluções.",
        "📖",
    )

    secao("Registrar empréstimo", "Informe o livro, o aluno e o prazo de devolução.", "＋")

    col1, col2 = st.columns(2)
    with col1:
        nome_livro = st.text_input("Nome do livro", placeholder="Digite o título do livro")
    with col2:
        nome_aluno = st.text_input("Nome do aluno", placeholder="Digite o nome do aluno")

    col3, col4 = st.columns(2)
    with col3:
        data_emprestimo = st.date_input("Data do empréstimo")
    with col4:
        data_devolucao = st.date_input("Data prevista para devolução")

    if st.button("Registrar empréstimo", use_container_width=True, key="registrar_emprestimo"):
        if not nome_livro or not nome_aluno:
            st.warning("Informe o nome do livro e o nome do aluno.")
        else:
            try:
                registrar_emprestimo(
                    nome_livro,
                    nome_aluno,
                    data_emprestimo,
                    data_devolucao,
                )
                st.success("Empréstimo registrado com sucesso!")
                st.rerun()
            except ValueError as erro:
                st.warning(str(erro))
            except Exception:
                st.error(
                    "Não foi possível registrar o empréstimo no momento. "
                    "Tente novamente mais tarde."
                )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    secao("Histórico de empréstimos", "Acompanhe todos os registros da biblioteca.", "📋")

    try:
        emprestimos = listar_emprestimos()
        if emprestimos:
            for emprestimo in emprestimos:
                (
                    emprestimo_id,
                    livro,
                    aluno,
                    data_emprestimo,
                    data_devolucao,
                    status,
                ) = emprestimo

                badge = badge_status(status, data_devolucao)

                col_card, col_action = st.columns([6, 1])
                with col_card:
                    st.markdown(
                        f"""
                        <div class="loan-card">
                            <div class="loan-top">
                                <div>
                                    <div class="entity-label">EMPRÉSTIMO #{emprestimo_id}</div>
                                    <h3>📚 {livro}</h3>
                                </div>
                                {badge}
                            </div>
                            <div class="loan-info-grid">
                                <div><span>Aluno</span><strong>👤 {aluno}</strong></div>
                                <div><span>Data do empréstimo</span><strong>📅 {data_emprestimo}</strong></div>
                                <div><span>Data de devolução</span><strong>📆 {data_devolucao}</strong></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_action:
                    st.markdown('<div class="action-spacer"></div>', unsafe_allow_html=True)
                    if status in ("ATIVO", "ATRASADO"):
                        if st.button(
                            "Registrar devolução",
                            key=f"devolver_{emprestimo_id}",
                            use_container_width=True,
                        ):
                            try:
                                registrar_devolucao(emprestimo_id)
                                st.success("Livro devolvido com sucesso!")
                                st.rerun()
                            except Exception:
                                st.error(
                                    "Não foi possível registrar a devolução no momento. "
                                    "Tente novamente mais tarde."
                                )
                    elif status == "DEVOLVIDO":
                        st.markdown('<div class="returned-action">✓ Devolvido</div>', unsafe_allow_html=True)
                    elif status == "CANCELADO":
                        st.markdown('<div class="cancelled-action">— Cancelado</div>', unsafe_allow_html=True)
                    else:
                        st.write(status)
        else:
            mensagem_vazia("📖", "Nenhum empréstimo registrado", "Os empréstimos realizados aparecerão aqui.")
    except Exception as erro:
        st.error(f"Erro ao consultar empréstimos: {erro}")


# ============================================================
# AUDITORIA
# ============================================================

elif opcao == "Auditoria":
    cabecalho_pagina(
        "Auditoria",
        "Consulte o histórico de operações realizadas no sistema.",
        "📋",
    )

    secao("Histórico de operações", "Registros gerados pelas movimentações da biblioteca.", "🔎")

    try:
        auditoria = listar_auditoria()

        if auditoria:
            for registro in auditoria:
                (
                    auditoria_id,
                    acao,
                    entidade,
                    entidade_id,
                    dados,
                    data_hora,
                ) = registro

                st.markdown(
                    f"""
                    <div class="audit-card">
                        <div class="audit-icon">↻</div>
                        <div class="audit-main">
                            <div class="audit-topline">
                                <span class="audit-action">{acao}</span>
                                <span class="audit-date">📅 {data_hora}</span>
                            </div>
                            <div class="audit-details">
                                <span><strong>Entidade:</strong> {entidade}</span>
                                <span><strong>ID:</strong> {entidade_id}</span>
                            </div>
                            <div class="audit-data">{dados}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            mensagem_vazia("📋", "Nenhum registro de auditoria", "As operações do sistema aparecerão nesta área.")
    except Exception as erro:
        st.error(f"Não foi possível carregar os registros de auditoria: {erro}")


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="footer">
        <div class="footer-line"></div>
        <div class="footer-brand">BIBLIOTECA SABER</div>
        <div>© 2026 Projeto realizado por Mário Fernando Santos Campos e Ana Beatriz Moura Carvalho.</div>
        <div>Todos os direitos reservados.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# import streamlit as st
# from datetime import date


# from main import (
#     cadastrar_livro,
#     listar_livros,
#     livro_possui_emprestimos,
#     excluir_livro,
#     cadastrar_aluno,
#     listar_alunos,
#     aluno_possui_emprestimos,
#     excluir_aluno,
#     listar_auditoria,
#     registrar_emprestimo,
#     listar_emprestimos,
#     registrar_devolucao,
#     contar_livros,
#     contar_alunos,
#     contar_emprestimos_ativos,
#     contar_emprestimos_atrasados
# )


# # ============================================================
# # CONFIGURAÇÃO
# # ============================================================

# st.set_page_config(
#     page_title="Biblioteca Virtual Saber",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="auto"
# )


# # ============================================================
# # CARREGAR CSS
# # ============================================================

# def carregar_css():

#     with open(
#         "style.css",
#         "r",
#         encoding="utf-8"
#     ) as arquivo:

#         css = arquivo.read()

#     st.markdown(
#         f"<style>{css}</style>",
#         unsafe_allow_html=True
#     )


# carregar_css()


# # ============================================================
# # CABEÇALHO
# # ============================================================

# st.title("📚 Biblioteca Virtual Saber")

# st.subheader(
#     "Sistema de gerenciamento de biblioteca."
# )


# # ============================================================
# # MENU
# # ============================================================

# st.sidebar.markdown(
#     """
#     <div class="sidebar-menu-title">
#         Menu Principal
#     </div>
#     """,
#     unsafe_allow_html=True
# )


# opcoes_menu = {
#     "Início": "🏠 Início",
#     "Alunos": "👥 Alunos",
#     "Livros": "📚 Livros",
#     "Cadastrar livro": "➕ Cadastrar livro",
#     "Empréstimos": "📖 Empréstimos",
#     "Auditoria": "📋 Auditoria"
# }


# # ============================================================
# # PÁGINA ATUAL
# # ============================================================

# if "pagina" not in st.session_state:
#     st.session_state.pagina = "Início"


# # ============================================================
# # BOTÕES DO MENU
# # ============================================================

# for chave, nome_exibicao in opcoes_menu.items():

#     if st.sidebar.button(
#         nome_exibicao,
#         key=f"menu_{chave}",
#         use_container_width=True
#     ):

#         st.session_state.pagina = chave
#         st.rerun()


# opcao = st.session_state.pagina


# # ============================================================
# # INÍCIO
# # ============================================================

# if opcao == "Início":

#     st.header("Início")

#     st.write(
#         "Bem-vindo ao sistema Biblioteca Virtual Saber."
#     )

#     st.markdown(
#         "<br>",
#         unsafe_allow_html=True
#     )


#     # ========================================================
#     # BUSCAR INDICADORES
#     # ========================================================

#     try:

#         quantidade_livros = contar_livros()

#         quantidade_alunos = contar_alunos()

#         emprestimos_ativos = contar_emprestimos_ativos()

#         emprestimos_atrasados = contar_emprestimos_atrasados()

#         erro_indicadores = False

#     except Exception:

#         quantidade_livros = 0

#         quantidade_alunos = 0

#         emprestimos_ativos = 0

#         emprestimos_atrasados = 0

#         erro_indicadores = True


#     # ========================================================
#     # AVISO
#     # ========================================================

#     if erro_indicadores:

#         st.warning(
#             "Não foi possível atualizar os indicadores no momento. "
#             "Tente novamente mais tarde."
#         )


#     # ========================================================
#     # INDICADORES
#     # ========================================================

#     col1, col2, col3, col4 = st.columns(4)


#     # ========================================================
#     # LIVROS
#     # ========================================================

#     with col1:

#         st.html(
#             f"""
#             <div class="dashboard-card">

#                 <div class="dashboard-icon">
#                     📚
#                 </div>

#                 <div class="dashboard-title">
#                     Livros
#                 </div>

#                 <div class="dashboard-value">
#                     {quantidade_livros}
#                 </div>

#                 <div class="dashboard-description">
#                     Total cadastrados
#                 </div>

#             </div>
#             """
#         )


#     # ========================================================
#     # ALUNOS
#     # ========================================================

#     with col2:

#         st.html(
#             f"""
#             <div class="dashboard-card">

#                 <div class="dashboard-icon">
#                     👥
#                 </div>

#                 <div class="dashboard-title">
#                     Alunos
#                 </div>

#                 <div class="dashboard-value">
#                     {quantidade_alunos}
#                 </div>

#                 <div class="dashboard-description">
#                     Total cadastrados
#                 </div>

#             </div>
#             """
#         )


#     # ========================================================
#     # EMPRÉSTIMOS ATIVOS
#     # ========================================================

#     with col3:

#         st.html(
#             f"""
#             <div class="dashboard-card">

#                 <div class="dashboard-icon">
#                     📖
#                 </div>

#                 <div class="dashboard-title">
#                     Empréstimos ativos
#                 </div>

#                 <div class="dashboard-value">
#                     {emprestimos_ativos}
#                 </div>

#                 <div class="dashboard-description">
#                     Atualmente emprestados
#                 </div>

#             </div>
#             """
#         )


#     # ========================================================
#     # ATRASADOS
#     # ========================================================

#     with col4:

#         st.html(
#             f"""
#             <div class="dashboard-card">

#                 <div class="dashboard-icon">
#                     🔴
#                 </div>

#                 <div class="dashboard-title">
#                     Atrasados
#                 </div>

#                 <div class="dashboard-value">
#                     {emprestimos_atrasados}
#                 </div>

#                 <div class="dashboard-description">
#                     Precisam de atenção
#                 </div>

#             </div>
#             """
#         )


# # ============================================================
# # ALUNOS
# # ============================================================

# elif opcao == "Alunos":

#     st.header("👥 Alunos")


#     # ========================================================
#     # CADASTRAR ALUNO
#     # ========================================================

#     st.subheader("➕ Cadastrar aluno")

#     nome = st.text_input(
#         "Nome do aluno"
#     )

#     matricula = st.text_input(
#         "Matrícula"
#     )


#     if st.button(
#         "Cadastrar aluno",
#         use_container_width=True
#     ):

#         if not nome or not matricula:

#             st.warning(
#                 "Preencha os campos Nome e matrícula."
#             )

#         else:

#             try:

#                 cadastrar_aluno(
#                     nome,
#                     matricula
#                 )

#                 st.success(
#                     "Aluno cadastrado com sucesso!"
#                 )

#                 st.rerun()

#             except Exception:

#                 st.error(
#                     "Não foi possível cadastrar o aluno no momento. "
#                     "Tente novamente mais tarde."
#                 )


#     st.divider()


#     # ========================================================
#     # LISTAGEM
#     # ========================================================

#     st.subheader("📓 Alunos cadastrados")

#     try:

#         alunos = listar_alunos()

#         if alunos:

#             for aluno in alunos:

#                 aluno_id = aluno[0]

#                 nome_aluno = aluno[1]

#                 matricula_aluno = aluno[2]


#                 # ============================================
#                 # CARD
#                 # ============================================

#                 st.html(
#                     f"""
#                     <div class="library-card">

#                         <div class="card-header">

#                             <div>

#                                 <div class="card-title">
#                                     👤 {nome_aluno}
#                                 </div>

#                                 <div class="card-subtitle">
#                                     Aluno cadastrado
#                                 </div>

#                             </div>

#                         </div>

#                         <div class="card-divider"></div>

#                         <div class="card-info">

#                             <div class="card-info-item">

#                                 <div class="card-info-label">
#                                     Matrícula
#                                 </div>

#                                 <div class="card-info-value">
#                                     {matricula_aluno}
#                                 </div>

#                             </div>

#                         </div>

#                     </div>
#                     """
#                 )


#                 # ============================================
#                 # BOTÃO EXCLUIR
#                 # ============================================

#                 col1, col2 = st.columns(
#                     [5, 1]
#                 )

#                 with col2:

#                     if st.button(
#                         "🗑️ Excluir",
#                         key=f"excluir_aluno_{aluno_id}",
#                         use_container_width=True
#                     ):

#                         try:

#                             if aluno_possui_emprestimos(
#                                 aluno_id
#                             ):

#                                 st.warning(
#                                     f"⚠️ Não é possível excluir "
#                                     f"o aluno **{nome_aluno}**, "
#                                     "pois ele possui um "
#                                     "empréstimo ativo."
#                                 )

#                             else:

#                                 excluir_aluno(
#                                     aluno_id
#                                 )

#                                 st.success(
#                                     f"Aluno **{nome_aluno}** "
#                                     "excluído com sucesso!"
#                                 )

#                                 st.rerun()

#                         except Exception:

#                             st.error(
#                                 "Não foi possível excluir o aluno "
#                                 "no momento."
#                             )


#                 st.markdown(
#                     "<div style='height: 8px'></div>",
#                     unsafe_allow_html=True
#                 )

#         else:

#             st.info(
#                 "Nenhum aluno foi encontrado."
#             )

#     except Exception:

#         st.error(
#             "Não foi possível carregar os alunos no momento. "
#             "Tente novamente mais tarde."
#         )


# # ============================================================
# # LIVROS
# # ============================================================

# elif opcao == "Livros":

#     st.header("📚 Livros cadastrados")

#     try:

#         livros = listar_livros()

#         if livros:

#             for livro in livros:

#                 livro_id = livro[0]

#                 titulo = livro[1]

#                 autor = livro[2]

#                 ano_publicacao = livro[3]

#                 quantidade = livro[4]


#                 # ====================================================
#                 # DISPONIBILIDADE
#                 # ====================================================

#                 if quantidade > 0:

#                     disponibilidade = "🟢 Disponível"

#                 else:

#                     disponibilidade = "🔴 Indisponível"


#                 # ====================================================
#                 # CARD DO LIVRO
#                 # ====================================================

#                 st.html(
#                     f"""
#                     <div class="library-card">

#                         <div class="card-header">

#                             <div>

#                                 <div class="card-title">
#                                     📚 {titulo}
#                                 </div>

#                                 <div class="card-subtitle">
#                                     {autor}
#                                 </div>

#                             </div>

#                         </div>

#                         <div class="card-divider"></div>

#                         <div class="card-info">

#                             <div class="card-info-item">

#                                 <div class="card-info-label">
#                                     Autor
#                                 </div>

#                                 <div class="card-info-value">
#                                     {autor}
#                                 </div>

#                             </div>

#                             <div class="card-info-item">

#                                 <div class="card-info-label">
#                                     Ano de publicação
#                                 </div>

#                                 <div class="card-info-value">
#                                     {ano_publicacao}
#                                 </div>

#                             </div>

#                             <div class="card-info-item">

#                                 <div class="card-info-label">
#                                     Exemplares
#                                 </div>

#                                 <div class="card-info-value">
#                                     {quantidade}
#                                 </div>

#                             </div>

#                             <div class="card-info-item">

#                                 <div class="card-info-label">
#                                     Disponibilidade
#                                 </div>

#                                 <div class="card-info-value">
#                                     {disponibilidade}
#                                 </div>

#                             </div>

#                         </div>

#                     </div>
#                     """
#                 )


#                 # ====================================================
#                 # BOTÃO EXCLUIR
#                 # ====================================================

#                 col1, col2 = st.columns(
#                     [5, 1]
#                 )

#                 with col2:

#                     if st.button(
#                         "🗑️ Excluir",
#                         key=f"excluir_livro_{livro_id}",
#                         use_container_width=True
#                     ):

#                         try:

#                             if livro_possui_emprestimos(
#                                 livro_id
#                             ):

#                                 st.warning(
#                                     f"⚠️ Não é possível excluir o livro "
#                                     f"**{titulo}**, pois ele possui "
#                                     f"registros de empréstimos."
#                                 )

#                             else:

#                                 excluir_livro(
#                                     livro_id
#                                 )

#                                 st.success(
#                                     f"Livro **{titulo}** excluído com sucesso!"
#                                 )

#                                 st.rerun()

#                         except ValueError as erro:

#                             st.warning(
#                                 str(erro)
#                             )

#                         except Exception:

#                             st.error(
#                                 "Não foi possível excluir o livro no momento. "
#                                 "Tente novamente mais tarde."
#                             )


#                 # ====================================================
#                 # ESPAÇAMENTO
#                 # ====================================================

#                 st.markdown(
#                     "<div style='height: 8px'></div>",
#                     unsafe_allow_html=True
#                 )

#         else:

#             st.info(
#                 "Nenhum livro cadastrado."
#             )

#     except Exception:

#         st.error(
#             "Não foi possível consultar os livros no momento. "
#             "Tente novamente mais tarde."
#         )


# # ============================================================
# # CADASTRAR LIVRO
# # ============================================================

# elif opcao == "Cadastrar livro":

#     st.header("➕ Cadastrar livro")


#     titulo = st.text_input(
#         "Título do livro"
#     )


#     autor = st.text_input(
#         "Autor"
#     )


#     ano_publicacao = st.number_input(
#         "Ano de publicação",
#         min_value=0,
#         step=1
#     )


#     quantidade = st.number_input(
#         "Quantidade",
#         min_value=1,
#         step=1
#     )


#     if st.button(
#         "Cadastrar livro"
#     ):

#         if not titulo or not autor:

#             st.warning(
#                 "Preencha o título e o autor."
#             )

#         else:

#             try:

#                 cadastrar_livro(
#                     titulo,
#                     autor,
#                     ano_publicacao,
#                     quantidade
#                 )

#                 st.success(
#                     "Livro cadastrado com sucesso!"
#                 )

#             except Exception:

#                 st.error(
#                     "Não foi possível cadastrar o livro no momento. "
#                     "Tente novamente mais tarde."
#                 )


# # ============================================================
# # EMPRÉSTIMOS
# # ============================================================

# elif opcao == "Empréstimos":

#     st.header("📖 Empréstimos")


#     # ========================================================
#     # REGISTRAR NOVO EMPRÉSTIMO
#     # ========================================================

#     st.subheader("➕ Registrar empréstimo")


#     nome_livro = st.text_input(
#         "Nome do livro"
#     )


#     nome_aluno = st.text_input(
#         "Nome do aluno"
#     )


#     data_emprestimo = st.date_input(
#         "Data do empréstimo"
#     )


#     data_devolucao = st.date_input(
#         "Data prevista para devolução"
#     )


#     if st.button(
#         "Registrar empréstimo"
#     ):

#         if not nome_livro or not nome_aluno:

#             st.warning(
#                 "Informe o nome do livro e o nome do aluno."
#             )

#         else:

#             try:

#                 registrar_emprestimo(
#                     nome_livro,
#                     nome_aluno,
#                     data_emprestimo,
#                     data_devolucao
#                 )

#                 st.success(
#                     "Empréstimo registrado com sucesso!"
#                 )

#                 st.rerun()

#             except ValueError as erro:

#                 st.warning(
#                     str(erro)
#                 )

#             except Exception:

#                 st.error(
#                     "Não foi possível registrar o empréstimo no momento. "
#                     "Tente novamente mais tarde."
#                 )


#     st.divider()


#     # ========================================================
#     # LISTA DOS EMPRÉSTIMOS
#     # ========================================================

#     st.subheader("📋 Histórico de empréstimos")


#     try:

#         emprestimos = listar_emprestimos()

#         if emprestimos:

#             for emprestimo in emprestimos:

#                 (
#                     emprestimo_id,
#                     livro,
#                     aluno,
#                     data_emprestimo,
#                     data_devolucao,
#                     status
#                 ) = emprestimo


#                 # ====================================================
#                 # ORGANIZAÇÃO DAS COLUNAS
#                 # ====================================================

#                 col1, col2, col3, col4, col5, col6 = st.columns(
#                     [2, 2, 1.5, 1.5, 1.5, 1.8]
#                 )


#                 # ====================================================
#                 # LIVRO
#                 # ====================================================

#                 with col1:

#                     st.write(
#                         f"📚 **{livro}**"
#                     )


#                 # ====================================================
#                 # ALUNO
#                 # ====================================================

#                 with col2:

#                     st.write(
#                         f"👤 {aluno}"
#                     )


#                 # ====================================================
#                 # DATA DO EMPRÉSTIMO
#                 # ====================================================

#                 with col3:

#                     st.write(
#                         f"📅 {data_emprestimo}"
#                     )


#                 # ====================================================
#                 # DATA DA DEVOLUÇÃO
#                 # ====================================================

#                 with col4:

#                     st.write(
#                         f"📆 {data_devolucao}"
#                     )


#                 # ====================================================
#                 # STATUS
#                 # ====================================================

#                 with col5:

#                     hoje = date.today()


#                     if status == "DEVOLVIDO":

#                         st.success(
#                             "🟢 DEVOLVIDO"
#                         )


#                     elif status == "ATRASADO":

#                         st.error(
#                             "🔴 ATRASADO"
#                         )


#                     elif status == "ATIVO":

#                         if (
#                             data_devolucao is not None
#                             and data_devolucao < hoje
#                         ):

#                             st.error(
#                                 "🔴 ATRASADO"
#                             )

#                         else:

#                             st.warning(
#                                 "🟠 ATIVO"
#                             )


#                     elif status == "CANCELADO":

#                         st.write(
#                             "⚪ CANCELADO"
#                         )


#                     else:

#                         st.write(
#                             status
#                         )


#                 # ====================================================
#                 # BOTÃO DE DEVOLUÇÃO
#                 # ====================================================

#                 with col6:

#                     if status in (
#                         "ATIVO",
#                         "ATRASADO"
#                     ):

#                         if st.button(
#                             "Registrar devolução",
#                             key=f"devolver_{emprestimo_id}"
#                         ):

#                             try:

#                                 registrar_devolucao(
#                                     emprestimo_id
#                                 )

#                                 st.success(
#                                     "Livro devolvido com sucesso!"
#                                 )

#                                 st.rerun()

#                             except Exception:

#                                 st.error(
#                                     "Não foi possível registrar a devolução "
#                                     "no momento. Tente novamente mais tarde."
#                                 )


#                     elif status == "DEVOLVIDO":

#                         st.write(
#                             "✓ Devolvido"
#                         )


#                     elif status == "CANCELADO":

#                         st.write(
#                             "- Cancelado"
#                         )


#                     else:

#                         st.write(
#                             status
#                         )


#                 st.divider()


#         else:

#             st.info(
#                 "Nenhum empréstimo foi registrado."
#             )


#     except Exception as erro:

#         st.error(
#             f"Erro ao consultar empréstimos: {erro}"
#         )


# # ============================================================
# # AUDITORIA
# # ============================================================

# elif opcao == "Auditoria":

#     st.header("📋 Auditoria")


#     st.write(
#         "Histórico de operações."
#     )


#     try:

#         auditoria = listar_auditoria()


#         if auditoria:

#             for registro in auditoria:

#                 (
#                     auditoria_id,
#                     acao,
#                     entidade,
#                     entidade_id,
#                     dados,
#                     data_hora
#                 ) = registro


#                 col1, col2, col3, col4 = st.columns(
#                     [2, 2, 2, 3]
#                 )


#                 with col1:

#                     st.write(
#                         f"📅 {data_hora}"
#                     )


#                 with col2:

#                     st.write(
#                         f"🔹 **{acao}**"
#                     )


#                 with col3:

#                     st.write(
#                         f"📂 {entidade}"
#                     )


#                 with col4:

#                     st.write(
#                         f"📝 {dados}"
#                     )


#                 st.divider()


#         else:

#             st.info(
#                 "Nenhum registro de auditoria foi encontrado."
#             )


#     except Exception as erro:

#         st.error(
#             f"Não foi possível carregar os registros de auditoria: {erro}"
#         )


# # ============================================================
# # RODAPÉ
# # ============================================================

# st.markdown(
#     """
#     <div class="footer">
#         © 2026 Projeto realizado por Mário Fernando Santos Campos
#         e Ana Beatriz Moura Carvalho. Todos os direitos reservados.
#     </div>
#     """,
#     unsafe_allow_html=True
# )