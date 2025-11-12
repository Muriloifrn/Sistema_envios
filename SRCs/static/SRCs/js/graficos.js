document.addEventListener("DOMContentLoaded", () => {
    const {
        enviosLabels, enviosValores,
        remetentesLabels, remetentesValores,
        destinatariosLabels, destinatariosValores,
        gastosLabels, gastosValores,
        usuariosLabels, usuariosValores
    } = window.dashboardData;

    // ===== Modal =========
    const modal = document.getElementById('modalGrafico');
    const modalCanvas = document.getElementById('graficoModal');
    const fecharModal = document.getElementById('fecharModal');
    let graficoModalInstance = null;

    function abrirGraficoModal(chartInstance) {
        modal.classList.add('active');
        if (graficoModalInstance) graficoModalInstance.destroy();

        const config = {
            type: chartInstance.config.type,
            data: JSON.parse(JSON.stringify(chartInstance.data)),
            options: JSON.parse(JSON.stringify(chartInstance.options))
        };
        graficoModalInstance = new Chart(modalCanvas.getContext('2d'), config);
    }

    fecharModal.onclick = () => modal.classList.remove('active');
    modal.onclick = (e) => { if (e.target === modal) modal.classList.remove('active'); };

    // ====== Gráficos ======
    const graficoEnvio = new Chart(document.getElementById('graficoEnvios').getContext('2d'), {
        type: 'bar',
        data: { labels: enviosLabels, datasets: [{ label: 'Envios por mês', data: enviosValores, backgroundColor: '#79aa2b', borderColor: '#79aa2b', borderWidth: 1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    const graficoRemetentes = new Chart(document.getElementById('graficoRemetentes').getContext('2d'), {
        type: 'bar',
        data: { labels: remetentesLabels, datasets: [{ label: 'Envios por loja (remetente)', data: remetentesValores, backgroundColor: '#d70367', borderColor: '#d70367', borderWidth: 1 }] },
        options: { responsive: true, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
    });

    const graficoDestinatarios = new Chart(document.getElementById('graficoDestinatarios').getContext('2d'), {
        type: 'bar',
        data: { labels: destinatariosLabels, datasets: [{ label: 'Envios recebidos (destinatário)', data: destinatariosValores, backgroundColor: '#6d2d86', borderColor: '#6d2d86', borderWidth: 1 }] },
        options: { responsive: true, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
    });

    const graficoGastos = new Chart(document.getElementById('graficoGastosUnidade').getContext('2d'), {
        type: 'bar',
        data: { labels: gastosLabels, datasets: [{ label: 'Gastos (R$) por unidade', data: gastosValores, backgroundColor: '#efc600', borderColor: '#efc600', borderWidth: 1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    const graficoUsuario = new Chart(document.getElementById('graficoEnviosUsuario').getContext('2d'), {
        type: 'bar',
        data: { labels: usuariosLabels, datasets: [{ label: 'Envios por usuário', data: usuariosValores, backgroundColor: '#002748', borderColor: '#002748', borderWidth: 1 }] },
        options: { responsive: true, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
    });

    // Clique para abrir no modal
    graficoEnvio.canvas.onclick = () => abrirGraficoModal(graficoEnvio);
    graficoRemetentes.canvas.onclick = () => abrirGraficoModal(graficoRemetentes);
    graficoDestinatarios.canvas.onclick = () => abrirGraficoModal(graficoDestinatarios);
    graficoGastos.canvas.onclick = () => abrirGraficoModal(graficoGastos);
    graficoUsuario.canvas.onclick = () => abrirGraficoModal(graficoUsuario);
});
