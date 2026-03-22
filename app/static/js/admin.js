/* ── Filtrar tickets por estado ── */
function filtrarTickets(btn) {
    const estado = btn.dataset.estado;
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    let visibles = 0;
    document.querySelectorAll('.ticket-card').forEach(card => {
        const mostrar = estado === 'todos' || card.dataset.estado === estado;
        card.classList.toggle('oculto', !mostrar);
        if (mostrar) visibles++;
    });
}

/* ── Scroll suave a sección ── */
function irA(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}