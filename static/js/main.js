(() => {
    "use strict";

    const root = document.documentElement;
    const body = document.body;
    const themeButton = document.querySelector("#theme-button");
    const menuButton = document.querySelector("#menu-button");
    const sidebarOverlay = document.querySelector("#sidebar-overlay");

    function updateThemeButton() {
        if (!themeButton) return;
        const darkThemeIsActive = root.dataset.theme === "dark";
        themeButton.setAttribute(
            "aria-label",
            darkThemeIsActive ? "Ativar tema claro" : "Ativar tema escuro"
        );
        themeButton.title = darkThemeIsActive ? "Tema claro" : "Tema escuro";
    }

    function toggleTheme() {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        root.dataset.theme = nextTheme;
        localStorage.setItem("fluxopag-theme", nextTheme);
        updateThemeButton();
    }

    function closeSidebar() {
        body.classList.remove("sidebar-open");
        if (menuButton) menuButton.setAttribute("aria-expanded", "false");
    }

    function toggleSidebar() {
        const sidebarIsOpen = body.classList.toggle("sidebar-open");
        menuButton.setAttribute("aria-expanded", String(sidebarIsOpen));
    }

    updateThemeButton();
    themeButton?.addEventListener("click", toggleTheme);
    menuButton?.setAttribute("aria-expanded", "false");
    menuButton?.addEventListener("click", toggleSidebar);
    sidebarOverlay?.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeSidebar();
    });

    document.querySelectorAll(".sidebar a").forEach((link) => {
        link.addEventListener("click", closeSidebar);
    });

    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirm || "Deseja continuar?";
            if (!window.confirm(message)) event.preventDefault();
        });
    });

    document.querySelectorAll(".clickable-row[data-url]").forEach((row) => {
        row.tabIndex = 0;
        row.setAttribute("role", "link");

        const openRow = (event) => {
            if (event.target.closest("a, button, input, select, textarea, form")) return;
            window.location.href = row.dataset.url;
        };

        row.addEventListener("click", openRow);
        row.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openRow(event);
            }
        });
    });

    document.querySelectorAll(".flash").forEach((message) => {
        window.setTimeout(() => message.remove(), 6000);
    });

    const serviceInputs = document.querySelectorAll('input[name="service_type"]');
    const serviceLabel = document.querySelector('input[name="service_label"]');

    function updateServiceLabel() {
        if (!serviceLabel || !serviceInputs.length) return;
        const selected = document.querySelector('input[name="service_type"]:checked');
        const type = selected?.value;
        serviceLabel.required = type === "table";

        if (type === "table") {
            serviceLabel.placeholder = "Ex.: 4";
        } else if (type === "pickup") {
            serviceLabel.placeholder = "Ex.: Retirada 12";
        } else {
            serviceLabel.placeholder = "Opcional — padrão: Balcão";
        }
    }

    serviceInputs.forEach((input) => input.addEventListener("change", updateServiceLabel));
    updateServiceLabel();

    const paymentForm = document.querySelector("#payment-form");
    if (paymentForm) {
        const paymentInputs = paymentForm.querySelectorAll('input[name="payment_method"]');
        const cashFields = paymentForm.querySelector("#cash-fields");
        const cashReceived = paymentForm.querySelector("#cash-received");
        const changeValue = paymentForm.querySelector("#change-value");
        const orderTotal = Number(paymentForm.dataset.total || 0);

        function parseMoney(value) {
            let text = String(value || "").replace("R$", "").replace(/\s/g, "");
            if (text.includes(",")) {
                text = text.replace(/\./g, "").replace(",", ".");
            }
            const amount = Number(text);
            return Number.isFinite(amount) ? amount : 0;
        }

        function formatMoney(value) {
            return new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(Math.max(value, 0));
        }

        function updateChange() {
            const received = parseMoney(cashReceived.value);
            changeValue.textContent = formatMoney(received - orderTotal);
        }

        function updatePaymentFields() {
            const selected = paymentForm.querySelector('input[name="payment_method"]:checked');
            const cashIsSelected = selected?.value === "cash";
            cashFields.hidden = !cashIsSelected;
            cashReceived.required = cashIsSelected;
            if (!cashIsSelected) cashReceived.value = "";
            updateChange();
        }

        paymentInputs.forEach((input) => input.addEventListener("change", updatePaymentFields));
        cashReceived.addEventListener("input", updateChange);
        updatePaymentFields();
    }
})();
