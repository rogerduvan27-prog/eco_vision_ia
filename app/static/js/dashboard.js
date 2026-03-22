/* ── Tips ecológicos rotativos ────────────────────────────── */
const TIPS = [
    'Una botella PET tarda 450 años en degradarse en la naturaleza.',
    'El aluminio puede reciclarse infinitas veces sin perder calidad.',
    'Reciclar una tonelada de papel salva 17 árboles y ahorra 26.000 litros de agua.',
    'El vidrio tarda más de 4.000 años en descomponerse en un vertedero.',
    'Colombia recicla solo el 17% de sus residuos sólidos — ¡tú puedes cambiar eso!',
    'Separar correctamente los residuos en casa puede reducir un 70% de lo que va al relleno sanitario.',
    'El cartón reciclado usa un 75% menos de energía que fabricar uno nuevo.',
    'Una lata de aluminio reciclada ahorra energía para mantener un televisor encendido 3 horas.'
];

let tipActual = 0;
let intervalo;

function crearDots() {
    const container = document.getElementById('tip-dots');
    if (!container) return;
    container.innerHTML = '';
    TIPS.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = 'tip-dot' + (i === 0 ? ' active' : '');
        dot.addEventListener('click', () => irATip(i));
        container.appendChild(dot);
    });
}

function actualizarTip(index) {
    const texto = document.getElementById('tip-text');
    const dots = document.querySelectorAll('.tip-dot');
    if (!texto) return;

    texto.classList.add('fade');
    setTimeout(() => {
        texto.textContent = TIPS[index];
        texto.classList.remove('fade');
    }, 400);

    dots.forEach((d, i) => d.classList.toggle('active', i === index));
    tipActual = index;
}

function irATip(index) {
    clearInterval(intervalo);
    actualizarTip(index);
    iniciarIntervalo();
}

function iniciarIntervalo() {
    intervalo = setInterval(() => {
        const siguiente = (tipActual + 1) % TIPS.length;
        actualizarTip(siguiente);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    crearDots();
    actualizarTip(0);
    iniciarIntervalo();
    iniciarGraficas();
});

/* ── Gráficas Chart.js ─────────────────────────────────────── */
function iniciarGraficas() {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#7aaa8f';
    Chart.defaults.font.family = "'DM Sans', sans-serif";

    // Gráfica barras: actividad semanal
    const ctxSemanal = document.getElementById('chart-semanal');
    if (ctxSemanal && typeof GRAF_SEMANAL !== 'undefined') {
        new Chart(ctxSemanal, {
            type: 'bar',
            data: {
                labels: GRAF_SEMANAL.labels,
                datasets: [{
                    data: GRAF_SEMANAL.data,
                    backgroundColor: GRAF_SEMANAL.data.map((v, i, arr) =>
                        v === Math.max(...arr) ? '#95d5b2' : '#52b788'
                    ),
                    borderRadius: 6,
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
                    }
                },
                scales: {
                    x: { grid: { color: 'rgba(82,183,136,0.06)' }, ticks: { font: { size: 11 } } },
                    y: { grid: { color: 'rgba(82,183,136,0.06)' }, ticks: { font: { size: 11 }, stepSize: 1 }, beginAtZero: true }
                }
            }
        });
    }

    // Gráfica dona: materiales
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
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { font: { size: 11 }, padding: 10, usePointStyle: true, pointStyleWidth: 8 }
                    },
                    tooltip: {
                        callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} clasificaciones` },
                        backgroundColor: '#112318',
                        borderColor: 'rgba(82,183,136,0.3)',
                        borderWidth: 1,
                    }
                }
            }
        });
    }
}