import streamlit as st
from sqlalchemy import create_engine, text

# Configuração da página
st.set_page_config(
    page_title="SaberLibrary",
    page_icon="📚",
    layout="wide"
)

st.title("📚 SaberLibrary")
st.subheader("Sistema de gerenciamento de biblioteca")

# Conexão com PostgreSQL
DATABASE_URL = "postgresql://postgres:root@localhost:5432/saberlibrary"

engine = create_engine(DATABASE_URL)

# Teste da conexão
try:
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))

    st.success("Banco de dados conectado com sucesso!")

except Exception as erro:
    st.error(f"Erro ao conectar ao banco de dados: {erro}")


# Menu lateral
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

        with engine.connect() as conexao:

            resultado = conexao.execute(
                text("""
                    SELECT *
                    FROM livros
                    ORDER BY id
                """)
            )

            livros = resultado.fetchall()

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

    if st.button("Cadastrar"):

        if not titulo or not autor:

            st.warning(
                "Preencha o título e o autor."
            )

        else:

            try:

                with engine.begin() as conexao:

                    conexao.execute(
                        text("""
                            INSERT INTO livros
                            (titulo, autor)
                            VALUES
                            (:titulo, :autor)
                        """),
                        {
                            "titulo": titulo,
                            "autor": autor
                        }
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

    st.info(
        "Área de gerenciamento de empréstimos."
    )