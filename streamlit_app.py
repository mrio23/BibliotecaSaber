import streamlit as st
from datetime import date

from main import (
    cadastrar_livro,
    listar_livros,
    listar_alunos,
    registrar_emprestimo,
    listar_emprestimos,
    registrar_devolucao
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
        "Alunos",
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
# LISTAR ALUNOS
# ============================================================

elif opcao == "Alunos":
    st.header("📓 Alunos cadastrados")
    
    try:
        
        alunos = listar_alunos()
        
        if alunos:
            
            st.dataframe(
                alunos,
                use_container_width=True
            )
        
        else:
            
            st.info(
                "Nenhum aluno foi encontrado."
            )
            
    except Exception as erro:
        
        st.error(
            f"Erro ao procurar o aluno {erro}"
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

            except Exception as erro:

                st.error(
                    f"Erro ao registrar empréstimo: {erro}"
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

                    if status == "ATIVO":

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

                            except Exception as erro:

                                st.error(
                                    f"Erro ao registrar devolução: {erro}"
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
# RODAPÉ
# ===========================================
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: #0e1117;
        color: #ffffff;
        font-size: 14px;
        border-top: 1px solid #333;
        z-index: 999;
    }
    </style>

    <div class="footer">
        © 2026 Projeto realizado por Mário Fernando Santos Campos
        e Ana Beatriz Moura Carvalho. Todos os direitos reservados.
    </div>
    """,
    unsafe_allow_html=True
)