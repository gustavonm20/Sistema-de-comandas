(() => {
    "use strict";

    const raiz = document.documentElement;
    const corpo = document.body;
    const botaoTema = document.querySelector("#botao-tema");
    const botaoMenu = document.querySelector("#botao-menu");
    const sobreposicao = document.querySelector("#sobreposicao-barra-lateral");

    function atualizarBotaoTema() {
        if (!botaoTema) return;
        const temaEscuroAtivo = raiz.dataset.tema === "escuro";
        botaoTema.setAttribute("aria-label", temaEscuroAtivo ? "Ativar tema claro" : "Ativar tema escuro");
        botaoTema.title = temaEscuroAtivo ? "Tema claro" : "Tema escuro";
    }

    function alternarTema() {
        const proximoTema = raiz.dataset.tema === "escuro" ? "claro" : "escuro";
        raiz.dataset.tema = proximoTema;
        localStorage.setItem("fluxopag-tema", proximoTema);
        atualizarBotaoTema();
    }

    function fecharBarraLateral() {
        corpo.classList.remove("barra-lateral-aberta");
        if (botaoMenu) botaoMenu.setAttribute("aria-expanded", "false");
    }

    function alternarBarraLateral() {
        const estaAberta = corpo.classList.toggle("barra-lateral-aberta");
        botaoMenu.setAttribute("aria-expanded", String(estaAberta));
    }

    atualizarBotaoTema();
    botaoTema?.addEventListener("click", alternarTema);
    botaoMenu?.setAttribute("aria-expanded", "false");
    botaoMenu?.addEventListener("click", alternarBarraLateral);
    sobreposicao?.addEventListener("click", fecharBarraLateral);

    document.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape") fecharBarraLateral();
    });
    document.querySelectorAll(".barra-lateral a").forEach((ligacao) => {
        ligacao.addEventListener("click", fecharBarraLateral);
    });
    document.querySelectorAll("form[data-confirmacao]").forEach((formulario) => {
        formulario.addEventListener("submit", (evento) => {
            const mensagem = formulario.dataset.confirmacao || "Deseja continuar?";
            if (!window.confirm(mensagem)) evento.preventDefault();
        });
    });
    document.querySelectorAll(".linha-clicavel[data-endereco]").forEach((linha) => {
        linha.tabIndex = 0;
        linha.setAttribute("role", "link");
        const abrirLinha = (evento) => {
            if (evento.target.closest("a, button, input, select, textarea, form")) return;
            window.location.href = linha.dataset.endereco;
        };
        linha.addEventListener("click", abrirLinha);
        linha.addEventListener("keydown", (evento) => {
            if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                abrirLinha(evento);
            }
        });
    });
    document.querySelectorAll(".mensagem").forEach((mensagem) => {
        window.setTimeout(() => mensagem.remove(), 6000);
    });

    const camposAtendimento = document.querySelectorAll('input[name="tipo_atendimento"]');
    const identificacaoAtendimento = document.querySelector('input[name="identificacao_atendimento"]');
    function atualizarIdentificacaoAtendimento() {
        if (!identificacaoAtendimento || !camposAtendimento.length) return;
        const selecionado = document.querySelector('input[name="tipo_atendimento"]:checked');
        const tipo = selecionado?.value;
        identificacaoAtendimento.required = tipo === "mesa";
        if (tipo === "mesa") identificacaoAtendimento.placeholder = "Ex.: 4";
        else if (tipo === "retirada") identificacaoAtendimento.placeholder = "Ex.: Retirada 12";
        else identificacaoAtendimento.placeholder = "Opcional — padrão: Balcão";
    }
    camposAtendimento.forEach((campo) => campo.addEventListener("change", atualizarIdentificacaoAtendimento));
    atualizarIdentificacaoAtendimento();

    const formularioPagamento = document.querySelector("#formulario-pagamento");
    if (formularioPagamento) {
        const camposPagamento = formularioPagamento.querySelectorAll('input[name="forma_pagamento"]');
        const camposDinheiro = formularioPagamento.querySelector("#campos-dinheiro");
        const valorRecebido = formularioPagamento.querySelector("#valor-recebido");
        const valorTroco = formularioPagamento.querySelector("#valor-troco");
        const totalPedido = Number(formularioPagamento.dataset.total || 0);

        function converterValor(valor) {
            let texto = String(valor || "").replace("R$", "").replace(/\s/g, "");
            if (texto.includes(",")) texto = texto.replace(/\./g, "").replace(",", ".");
            const quantia = Number(texto);
            return Number.isFinite(quantia) ? quantia : 0;
        }
        function formatarValor(valor) {
            return new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"}).format(Math.max(valor, 0));
        }
        function atualizarTroco() {
            const recebido = converterValor(valorRecebido.value);
            valorTroco.textContent = formatarValor(recebido - totalPedido);
        }
        function atualizarCamposPagamento() {
            const selecionado = formularioPagamento.querySelector('input[name="forma_pagamento"]:checked');
            const dinheiroSelecionado = selecionado?.value === "dinheiro";
            camposDinheiro.hidden = !dinheiroSelecionado;
            valorRecebido.required = dinheiroSelecionado;
            if (!dinheiroSelecionado) valorRecebido.value = "";
            atualizarTroco();
        }
        camposPagamento.forEach((campo) => campo.addEventListener("change", atualizarCamposPagamento));
        valorRecebido.addEventListener("input", atualizarTroco);
        atualizarCamposPagamento();
    }
})();
