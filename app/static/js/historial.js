/* ── Filtrar registros por tipo ── */
function filtrar(btn) {
    const tipo = btn.dataset.tipo;

    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');

    const cards = document.querySelectorAll('.registro-card');
    let visibles = 0;

    cards.forEach((card, i) => {
        const mostrar = tipo === 'todos' || card.dataset.tipo === tipo;
        card.classList.toggle('oculto', !mostrar);
        if (mostrar) {
            card.style.animationDelay = (visibles * 0.04) + 's';
            visibles++;
        }
    });

    const sinResultados = document.getElementById('sin-resultados');
    if (sinResultados) {
        sinResultados.style.display = visibles === 0 ? 'block' : 'none';
    }
}