document.addEventListener('DOMContentLoaded', function () {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#7aaa8f';
    Chart.defaults.font.family = "'DM Sans', sans-serif";

    /* ── Gráfica barras: actividad semanal ── */
    const ctxSemanal = document.getElementById('chart-semanal');
    if (ctxSemanal && typeof GRAF_SEMANAL !== 'undefined') {
        new Chart(ctxSemanal, {
            type: 'bar',
            data: {
                labels: GRAF_SEMANAL.labels,
                datasets: [{
                    label: 'Clasificaciones',
                    data: GRAF_SEMANAL.data,
                    backgroundColor: GRAF_SEMANAL.data.map((v, i, arr) =>
                        v === Math.max(...arr) ? '#95d5b2' : '#52b788'
                    ),
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: { label: ctx => ` ${ctx.parsed.y} clasificaciones` },
                        backgroundColor: '#112318',
                        borderColor: 'rgba(82,183,136,0.3)',
                        borderWidth: 1,
                        padding: 10,
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(82,183,136,0.06)' },
                        ticks: { font: { size: 12 } }
                    },
                    y: {
                        grid: { color: 'rgba(82,183,136,0.06)' },
                        ticks: { font: { size: 12 }, stepSize: 1 },
                        beginAtZero: true,
                    }
                }
            }
        });
    }

    /* ── Gráfica dona: distribución materiales ── */
    const ctxMat = document.getElementById('chart-materiales');
    if (ctxMat && typeof GRAF_MATERIALES !== 'undefined' && GRAF_MATERIALES.data.length > 0) {
        new Chart(ctxMat, {
            type: 'doughnut',
            data: {
                labels: GRAF_MATERIALES.labels,
                datasets: [{
                    data: GRAF_MATERIALES.data,
                    backgroundColor: GRAF_MATERIALES.colores,
                    borderColor: '#112318',
                    borderWidth: 3,
                    hoverOffset: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            font: { size: 12 },
                            padding: 14,
                            usePointStyle: true,
                            pointStyleWidth: 10,
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.label}: ${ctx.parsed} clasificaciones`
                        },
                        backgroundColor: '#112318',
                        borderColor: 'rgba(82,183,136,0.3)',
                        borderWidth: 1,
                        padding: 10,
                    }
                }
            }
        });
    }
});