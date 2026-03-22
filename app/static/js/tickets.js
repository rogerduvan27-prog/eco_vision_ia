/* ── Modal ─────────────────────────────────────────────────── */
function abrirModal() {
    document.getElementById('modal-overlay').classList.add('open');
    document.body.style.overflow = 'hidden';
}

function cerrarModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.remove('open');
    document.body.style.overflow = '';
}

/* ── Cerrar con Escape ─────────────────────────────────────── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') cerrarModal();
});