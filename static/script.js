(() => {

    // ============================================================
    // BIBLIOTECA SABER — INTERAÇÕES VISUAIS
    // ============================================================

    const adicionarInteracoes = () => {

        // --------------------------------------------------------
        // BOTÕES
        // --------------------------------------------------------

        const botoes = document.querySelectorAll(
            '[data-testid="stButton"] button'
        );

        botoes.forEach((botao) => {

            if (botao.dataset.saberInicializado === "true") {
                return;
            }

            botao.dataset.saberInicializado = "true";

            botao.addEventListener("click", () => {

                botao.classList.remove("saber-click");

                void botao.offsetWidth;

                botao.classList.add("saber-click");

                setTimeout(() => {
                    botao.classList.remove("saber-click");
                }, 180);

            });

        });


        // --------------------------------------------------------
        // CAMPOS
        // --------------------------------------------------------

        const campos = document.querySelectorAll(
            '[data-testid="stTextInput"] input,' +
            '[data-testid="stNumberInput"] input,' +
            '[data-testid="stDateInput"] input'
        );

        campos.forEach((campo) => {

            if (campo.dataset.saberInicializado === "true") {
                return;
            }

            campo.dataset.saberInicializado = "true";

            campo.addEventListener("focus", () => {
                campo.classList.add("saber-focus");
            });

            campo.addEventListener("blur", () => {
                campo.classList.remove("saber-focus");
            });

        });


        // --------------------------------------------------------
        // CARDS
        // --------------------------------------------------------

        const cards = document.querySelectorAll(
            ".metric-card," +
            ".entity-card," +
            ".book-card," +
            ".loan-card," +
            ".audit-card," +
            ".quick-card"
        );

        cards.forEach((card) => {

            if (card.dataset.saberInicializado === "true") {
                return;
            }

            card.dataset.saberInicializado = "true";

            card.addEventListener("mouseenter", () => {
                card.classList.add("saber-card-hover");
            });

            card.addEventListener("mouseleave", () => {
                card.classList.remove("saber-card-hover");
            });

        });

    };


    // ============================================================
    // EXECUÇÃO INICIAL
    // ============================================================

    adicionarInteracoes();


    // ============================================================
    // OBSERVA ALTERAÇÕES DO STREAMLIT
    // ============================================================

    const observer = new MutationObserver(() => {
        adicionarInteracoes();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();