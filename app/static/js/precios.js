/* ── Filtrar materiales por categoría ── */
function filtrar(btn) {
    const cat = btn.dataset.cat;

    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');

    document.querySelectorAll('.material-card').forEach((card, i) => {
        const mostrar = cat === 'todos' || card.dataset.cat === cat;
        card.classList.toggle('oculto', !mostrar);
        if (mostrar) card.style.animationDelay = (i * 0.04) + 's';
    });
}