import streamlit as st

from main import (
    cadastrar_livro,
    listar_livros,
    registrar_emprestimo
)


st.set_page_config(
    page_title="SaberLibrary",
    page_icon="📚",
    layout="wide"
)


st.title("📚 SaberLibrary")
st.subheader("Sistema de gerenciamento de biblioteca")


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


if opcao == "Início":

    st.header("Início")

    st.write(
        "Bem-vindo ao sistema SaberLibrary."
    )


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
            st.info("Nenhum livro cadastrado.")

    except Exception as erro:

        st.error(
            f"Erro ao consultar os livros: {erro}"
        )


elif opcao == "Cadastrar livro":

    st.header("➕ Cadastrar livro")

    titulo = st.text_input("Título do livro")
    autor = st.text_input("Autor")
    ano_publicacao = st.text_input("Ano de Publicação")
    quantidade = st.text_input("Quantidade")

    if st.button("Cadastrar"):

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


elif opcao == "Empréstimos":

    st.header("📖 Empréstimos")

    livro_id = st.number_input(
        "ID do livro",
        min_value=1,
        step=1
    )
    
    aluno_id = st.number_input(
        "Matrícula do aluno",
        min_value=1,
        step=1
    )
    
    data_empresitmo = st.date_input(
        "Data do empréstimo"
    )
    
    data_devolucao = st.date_input(
        "Data de devolução"
    )
    
    status = st.selectbox(
        "Status",
        [
            "EMPRESTADO",
            "DEVOLVIDO"
        ]
    )
    
    if st.button("Registrar empréstimo"):
        
        try:
            
            registrar_emprestimo(
                livro_id,
                aluno_id,
                data_empresitmo,
                data_devolucao,
                status
            )
            
            st.success(
                "Empréstimo registrado com sucesso!"
            )
    
        except Exception as erro:
        
            st.error(
                f"Erro ao registrar empréstimo: {erro}"
                )
    
    st.info(
        "Área de gerenciamento de empréstimos."
    )