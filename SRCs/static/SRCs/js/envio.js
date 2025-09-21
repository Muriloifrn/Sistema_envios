document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".form-envio");
    const btnSalvar = document.getElementById("btnSalvar");
    const gerarPdfInput = document.getElementById("gerar_pdf");

    const addItemBtn = document.getElementById("add-item");
    const formsetContainer = document.getElementById("formset-itens");
    const emptyFormTemplate = document.getElementById("empty-form-template").innerHTML;
    const totalGeralEl = document.getElementById("total-geral");

    // ======== Adicionar item ========
    addItemBtn.addEventListener("click", () => {
        // Descobre quantos formulários existem
        const totalForms = document.querySelectorAll(".item-form").length;
        const managementForm = document.querySelector("#id_form-TOTAL_FORMS");

        // Clona o template e substitui __prefix__ pelo índice correto
        let newForm = emptyFormTemplate.replace(/__prefix__/g, totalForms);
        formsetContainer.insertAdjacentHTML("beforeend", newForm);

        // Atualiza TOTAL_FORMS
        managementForm.value = totalForms + 1;

        atualizarTotal();
    });

    // ======== Remover item ========
    formsetContainer.addEventListener("click", (e) => {
        if (e.target.classList.contains("remover-item")) {
            e.target.closest(".item-form").remove();

            // Recalcula TOTAL_FORMS
            const forms = document.querySelectorAll(".item-form");
            document.querySelector("#id_form-TOTAL_FORMS").value = forms.length;

            atualizarTotal();
        }
    });

    // ======== Atualizar total ao digitar ========
    formsetContainer.addEventListener("input", atualizarTotal);

    function atualizarTotal() {
        let total = 0;
        document.querySelectorAll(".item-form").forEach(form => {
            const qtd = parseFloat(form.querySelector("[name$='quantidade']").value) || 0;
            const valor = parseFloat(form.querySelector("[name$='valor_unitario']").value) || 0;
            total += qtd * valor;
        });
        totalGeralEl.textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
    }

    // ======== Perguntar sobre PDF antes de enviar ========
    btnSalvar.addEventListener("click", () => {
        const gerar = confirm("Deseja gerar PDF de declaração de conteúdo?");
        gerarPdfInput.value = gerar ? "sim" : "nao";
        form.submit();
    });
});
