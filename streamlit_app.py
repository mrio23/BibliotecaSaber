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
    contar_emprestimos_atrasados
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Biblioteca Virtual Saber",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# CARREGAR CSS
# ============================================================

def carregar_css():
    with open("style.css", "r", encoding="utf-8") as arquivo:
        css = arquivo.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


# Chama o CSS somente depois da função existir
carregar_css()


# ============================================================
# CABEÇALHO
# ============================================================

st.title("📚 Biblioteca Virtual Saber")
st.subheader("Sistema de gerenciamento de biblioteca.")


# ============================================================
# MENU
# ============================================================

st.sidebar.markdown(
    "<div class='sideebar-menu-title'> Menu Principal</div><br></br>",
    unsafe_allow_html=True
)

opcoes_menu = {
    "Início": "🏠 Início",
    "Alunos": "👥 Alunos",
    "Livros": "📚 Livros",
    "Cadastrar Livro": "➕ Cadastrar Livro",
    "Empréstimos": "📖 Empréstimos",
    "Auditoria": "📋 Auditoria"
}

if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"

for chave, nome_exibicao in opcoes_menu.items():
    
    if st.sidebar.button(
        nome_exibicao,
        key=f"menu_{chave}",
        use_container_width=True
    ):
        st.session_state.pagina = chave
        st.rerun()
        
opcao = st.session_state.pagina

# ============================================================
# INÍCIO
# ============================================================

if opcao == "Início":

    st.header("Início")

    st.write(
        "Bem-vindo ao sistema Biblioteca Virtual Saber."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # BUSCAR INDICADORES
    # ========================================================

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

    # ========================================================
    # AVISO
    # ========================================================

    if erro_indicadores:

        st.warning(
            "Não foi possível atualizar os indicadores no momento. "
            "Tente novamente mais tarde."
        )

    # ========================================================
    # INDICADORES
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    # ========================================================
    # LIVROS
    # ========================================================

    with col1:

        st.html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-icon">
                    📚
                </div>

                <div class="dashboard-title">
                    Livros
                </div>

                <div class="dashboard-value">
                    {quantidade_livros}
                </div>

                <div class="dashboard-description">
                    Total cadastrados
                </div>

            </div>
            """
        )

    # ========================================================
    # ALUNOS
    # ========================================================

    with col2:

        st.html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-icon">
                    👥
                </div>

                <div class="dashboard-title">
                    Alunos
                </div>

                <div class="dashboard-value">
                    {quantidade_alunos}
                </div>

                <div class="dashboard-description">
                    Total cadastrados
                </div>

            </div>
            """
        )

    # ========================================================
    # EMPRÉSTIMOS ATIVOS
    # ========================================================

    with col3:

        st.html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-icon">
                    📖
                </div>

                <div class="dashboard-title">
                    Empréstimos ativos
                </div>

                <div class="dashboard-value">
                    {emprestimos_ativos}
                </div>

                <div class="dashboard-description">
                    Atualmente emprestados
                </div>

            </div>
            """
        )

    # ========================================================
    # ATRASADOS
    # ========================================================

    with col4:

        st.html(
            f"""
            <div class="dashboard-card">

                <div class="dashboard-icon">
                    🔴
                </div>

                <div class="dashboard-title">
                    Atrasados
                </div>

                <div class="dashboard-value">
                    {emprestimos_atrasados}
                </div>

                <div class="dashboard-description">
                    Precisam de atenção
                </div>

            </div>
            """
        )


# ============================================================
# ALUNOS
# ============================================================

elif opcao == "Alunos":

    st.header("👥 Alunos")

    # ========================================================
    # CADASTRAR ALUNO
    # ========================================================

    st.subheader("➕ Cadastrar aluno")

    nome = st.text_input(
        "Nome do aluno"
    )

    matricula = st.text_input(
        "Matrícula"
    )

    if st.button(
        "Cadastrar aluno",
        use_container_width=True
    ):

        if not nome or not matricula:

            st.warning(
                "Preencha os campos Nome e matrícula."
            )

        else:

            try:

                cadastrar_aluno(
                    nome,
                    matricula
                )

                st.success(
                    "Aluno cadastrado com sucesso!"
                )

                st.rerun()

            except Exception:

                st.error(
                    "Não foi possível cadastrar o aluno no momento. "
                    "Tente novamente mais tarde."
                )

    st.divider()

    # ========================================================
    # LISTAGEM
    # ========================================================

    st.subheader("📓 Alunos cadastrados")

    try:

        alunos = listar_alunos()

        if alunos:

            for aluno in alunos:

                aluno_id = aluno[0]
                nome_aluno = aluno[1]
                matricula_aluno = aluno[2]

                # ============================================
                # CARD
                # ============================================

                st.html(
    f"""
    <div class="library-card">

        <div class="card-header">

            <div>

                <div class="card-title">
                    👤 {nome_aluno}
                </div>

                <div class="card-subtitle">
                    Aluno cadastrado
                </div>

            </div>

        </div>

        <div class="card-divider"></div>

        <div class="card-info">

            <div class="card-info-item">

                <div class="card-info-label">
                    Matrícula
                </div>

                <div class="card-info-value">
                    {matricula_aluno}
                </div>

            </div>

        </div>

    </div>
    """
)

                # ============================================
                # BOTÃO EXCLUIR
                # ============================================

                col1, col2 = st.columns(
                    [5, 1]
                )

                with col2:

                    if st.button(
                        "🗑️ Excluir",
                        key=f"excluir_aluno_{aluno_id}",
                        use_container_width=True
                    ):

                        try:

                            if aluno_possui_emprestimos(aluno_id):

                                st.warning(
                                    f"⚠️ Não é possível excluir "
                                    f"o aluno **{nome_aluno}**, "
                                    "pois ele possui um "
                                    "empréstimo ativo."
                                )

                            else:

                                excluir_aluno(aluno_id)

                                st.success(
                                    f"Aluno **{nome_aluno}** "
                                    "excluído com sucesso!"
                                )

                                st.rerun()

                        except Exception:

                            st.error(
                                "Não foi possível excluir o aluno "
                                "no momento."
                            )

                st.markdown(
                    "<div style='height: 8px'></div>",
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "Nenhum aluno foi encontrado."
            )

    except Exception:

        st.error(
            "Não foi possível carregar os alunos no momento. "
            "Tente novamente mais tarde."
        )
    
# ============================================================
# LIVROS
# ============================================================

elif opcao == "Livros":

    st.header("📚 Livros cadastrados")

    try:

        livros = listar_livros()

        if livros:

            for livro in livros:

                livro_id = livro[0]
                titulo = livro[1]
                autor = livro[2]
                ano_publicacao = livro[3]
                quantidade = livro[4]

                # ====================================================
                # DISPONIBILIDADE
                # ====================================================

                if quantidade > 0:

                    disponibilidade = "🟢 Disponível"

                else:

                    disponibilidade = "🔴 Indisponível"

                # ====================================================
                # CARD DO LIVRO
                # ====================================================

                st.html(
                    f"""
                    <div class="library-card">

                        <div class="card-header">

                            <div>

                                <div class="card-title">
                                    📚 {titulo}
                                </div>

                                <div class="card-subtitle">
                                    {autor}
                                </div>

                            </div>

                        </div>

                        <div class="card-divider"></div>

                        <div class="card-info">

                            <div class="card-info-item">

                                <div class="card-info-label">
                                    Autor
                                </div>

                                <div class="card-info-value">
                                    {autor}
                                </div>

                            </div>

                            <div class="card-info-item">

                                <div class="card-info-label">
                                    Ano de publicação
                                </div>

                                <div class="card-info-value">
                                    {ano_publicacao}
                                </div>

                            </div>

                            <div class="card-info-item">

                                <div class="card-info-label">
                                    Exemplares
                                </div>

                                <div class="card-info-value">
                                    {quantidade}
                                </div>

                            </div>

                            <div class="card-info-item">

                                <div class="card-info-label">
                                    Disponibilidade
                                </div>

                                <div class="card-info-value">
                                    {disponibilidade}
                                </div>

                            </div>

                        </div>

                    </div>
                    """
                )

                # ====================================================
                # BOTÃO EXCLUIR
                # ====================================================

                col1, col2 = st.columns([5, 1])

                with col2:

                    if st.button(
                        "🗑️ Excluir",
                        key=f"excluir_livro_{livro_id}",
                        use_container_width=True
                    ):

                        try:

                            if livro_possui_emprestimos(livro_id):

                                st.warning(
                                    f"⚠️ Não é possível excluir o livro "
                                    f"**{titulo}**, pois ele possui "
                                    f"registros de empréstimos."
                                )

                            else:

                                excluir_livro(livro_id)

                                st.success(
                                    f"Livro **{titulo}** excluído com sucesso!"
                                )

                                st.rerun()

                        except ValueError as erro:

                            st.warning(
                                str(erro)
                            )

                        except Exception:

                            st.error(
                                "Não foi possível excluir o livro no momento. "
                                "Tente novamente mais tarde."
                            )

                # ====================================================
                # ESPAÇAMENTO ENTRE OS CARDS
                # ====================================================

                st.markdown(
                    "<div style='height: 8px'></div>",
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "Nenhum livro cadastrado."
            )

    except Exception:

        st.error(
            "Não foi possível consultar os livros no momento. "
            "Tente novamente mais tarde."
        )


# ============================================================
# CADASTRAR LIVRO
# ============================================================

elif opcao == "Cadastrar livro":

    st.header("➕ Cadastrar livro")

    titulo = st.text_input(
        "Título do livro"
    )

    autor = st.text_input(
        "Autor"
    )

    ano_publicacao = st.number_input(
        "Ano de publicação",
        min_value=0,
        step=1
    )

    quantidade = st.number_input(
        "Quantidade",
        min_value=1,
        step=1
    )

    if st.button("Cadastrar livro"):

        if not titulo or not autor:

            st.warning(
                "Preencha o título e o autor."
            )

        else:

            try:

                cadastrar_livro(
                    titulo,
                    autor,
                    ano_publicacao,
                    quantidade
                )

                st.success(
                    "Livro cadastrado com sucesso!"
                )

            except Exception:

                st.error(
                    "Não foi possível cadastrar o livro no momento. Tente novamente mais tarde."
                )


# ============================================================
# EMPRÉSTIMOS
# ============================================================

elif opcao == "Empréstimos":

    st.header("📖 Empréstimos")

    # ========================================================
    # REGISTRAR NOVO EMPRÉSTIMO
    # ========================================================

    st.subheader("➕ Registrar empréstimo")

    nome_livro = st.text_input(
        "Nome do livro"
    )

    nome_aluno = st.text_input(
        "Nome do aluno"
    )

    data_emprestimo = st.date_input(
        "Data do empréstimo"
    )

    data_devolucao = st.date_input(
        "Data prevista para devolução"
    )

    if st.button("Registrar empréstimo"):

        if not nome_livro or not nome_aluno:

            st.warning(
                "Informe o nome do livro e o nome do aluno."
            )

        else:

            try:

                registrar_emprestimo(
                    nome_livro,
                    nome_aluno,
                    data_emprestimo,
                    data_devolucao
                )

                st.success(
                    "Empréstimo registrado com sucesso!"
                )

                st.rerun()

            except ValueError as erro:

                st.warning(
                    str(erro)
                )

            except Exception:

                st.error(
                    "Não foi possível registrar o empréstimo no momento. Tente novamente mais tarde."
                )


    st.divider()


    # ========================================================
    # LISTA DOS EMPRÉSTIMOS
    # ========================================================

    st.subheader("📋 Histórico de empréstimos")

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
                    status
                ) = emprestimo


                # ====================================================
                # ORGANIZAÇÃO DAS COLUNAS
                # ====================================================

                col1, col2, col3, col4, col5, col6 = st.columns(
                    [2, 2, 1.5, 1.5, 1.5, 1.8]
                )


                # ====================================================
                # LIVRO
                # ====================================================

                with col1:

                    st.write(
                        f"📚 **{livro}**"
                    )


                # ====================================================
                # ALUNO
                # ====================================================

                with col2:

                    st.write(
                        f"👤 {aluno}"
                    )


                # ====================================================
                # DATA DO EMPRÉSTIMO
                # ====================================================

                with col3:

                    st.write(
                        f"📅 {data_emprestimo}"
                    )


                # ====================================================
                # DATA DA DEVOLUÇÃO
                # ====================================================

                with col4:

                    st.write(
                        f"📆 {data_devolucao}"
                    )


                # ====================================================
                # STATUS
                # ====================================================

                with col5:

                    hoje = date.today()

                    if status == "DEVOLVIDO":

                        st.success(
                            "🟢 DEVOLVIDO"
                        )


                    elif status == "ATRASADO":
                        
                        st.error(
                            "🔴 ATRASADO"
                        )
                    
                    elif status == "ATIVO":

                        if (
                            data_devolucao is not None
                            and data_devolucao < hoje
                        ):

                            st.error(
                                "🔴 ATRASADO"
                            )

                        else:

                            st.warning(
                                "🟠 ATIVO"
                            )

                    elif status == "CANCELADO":

                        st.write(
                            "⚪ CANCELADO"
                        )

                    else:

                        st.write(
                            status
                        )
                # ====================================================
                # BOTÃO DE DEVOLUÇÃO
                # ====================================================

                with col6:

                    if status in ("ATIVO", "ATRASADO"):

                        if st.button(
                            "Registrar devolução",
                            key=f"devolver_{emprestimo_id}"
                        ):

                            try:

                                registrar_devolucao(
                                    emprestimo_id
                                )

                                st.success(
                                    "Livro devolvido com sucesso!"
                                )

                                st.rerun()

                            except Exception:

                                st.error(
                                    "Não foi possível registrar a devolução no momento. Tente novamente mais tarde."
                                )

                    elif status == "DEVOLVIDO":

                        st.write(
                            "✓ Devolvido"
                        )
                        
                    elif status == "CANCELADO":
                        
                        st.write(
                            "- Cancelado"
                        )
                        
                    else:
                        
                        st.write(
                            status
                        )

                st.divider()

        else:

            st.info(
                "Nenhum empréstimo foi registrado."
            )

    except Exception as erro:

        st.error(
            f"Erro ao consultar empréstimos: {erro}"
        )

# ===========================================
# AUDITORIA
# ===========================================

elif opcao == "Auditoria":

    st.header("📋 Auditoria")

    st.write(
        "Histórico de operações."
    )

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
                    data_hora
                ) = registro

                col1, col2, col3, col4 = st.columns(
                    [2, 2, 2, 3]
                )

                with col1:

                    st.write(
                        f"📅 {data_hora}"
                    )

                with col2:

                    st.write(
                        f"🔹 **{acao}**"
                    )

                with col3:

                    st.write(
                        f"📂 {entidade}"
                    )

                with col4:

                    st.write(
                        f"📝 {dados}"
                    )

                st.divider()

        else:

            st.info(
                "Nenhum registro de auditoria foi encontrado."
            )

    except Exception as erro:

        st.error(
            f"Não foi possível carregar os registros de auditoria: {erro}"
        )
        
# ===========================================
# RODAPÉ
# ===========================================
st.markdown(
    """
    <div class="footer">
        © 2026 Projeto realizado por Mário Fernando Santos Campos
        e Ana Beatriz Moura Carvalho. Todos os direitos reservados.
    </div>
    """,
    unsafe_allow_html=True
)