import streamlit as st

from main import (
    cadastrar_livro,
    listar_livros,
    registrar_emprestimo
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
# CABEÇALHO
# ============================================================

st.title("📚 Biblioteca Virtual Saber")
st.subheader("Sistema de gerenciamento de biblioteca.")


# ============================================================
# MENU
# ============================================================

st.sidebar.title("Menu")

opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    [
        "Início",
        "Livros",
        "Cadastrar livro",
        "Empréstimos"
    ]
)


# ============================================================
# INÍCIO
# ============================================================

if opcao == "Início":

    st.header("Início")

    st.write(
        "Bem-vindo ao sistema Biblioteca Virtual Saber."
    )


# ============================================================
# LISTAR LIVROS
# ============================================================

elif opcao == "Livros":

    st.header("📚 Livros cadastrados")

    try:

        livros = listar_livros()

        if livros:

            st.dataframe(
                livros,
                use_container_width=True
            )

        else:

            st.info(
                "Nenhum livro cadastrado."
            )

    except Exception as erro:

        st.error(
            f"Erro ao consultar os livros: {erro}"
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

            except Exception as erro:

                st.error(
                    f"Erro ao cadastrar livro: {erro}"
                )


# ============================================================
# EMPRÉSTIMOS
# ============================================================

elif opcao == "Empréstimos":

    st.header("📖 Registrar empréstimo")

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
                "Informe o nome do livro e a matrícula do aluno."
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

            except ValueError as erro:

                st.warning(
                    str(erro)
                )

            except Exception as erro:

                st.error(
                    f"Erro ao registrar empréstimo: {erro}"
                )

# ===========================================
# RODAPÉ
# ===========================================

st.markdown(
    """
    <style>
    .footer {
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: #0e1117;
        color: #ffffff;
        font-size: 14px;
        border-top: 1px solid #333;
    }
    </style>
    
    <div class="footer">
        @ 2026  Projeto realizado por Mário Fernando Santos Campos e Ana Beatriz Moura Carvalho. Todos os direitos reservados.
    </div>
    """,
    unsafe_allow_html=True
)