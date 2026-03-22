/* ── Mostrar / ocultar contraseña ── */
function togglePw(id, btn) {
    const input = document.getElementById(id);
    input.type = input.type === 'text' ? 'password' : 'text';
    btn.style.opacity = input.type === 'text' ? '1' : '0.5';
}

/* ── Fortaleza de contraseña ── */
function evalPw(input) {
    const pw = input.value;
    const segs = ['ps1', 'ps2', 'ps3', 'ps4'];
    let score = 0;
    if (pw.length >= 8) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    const cls = score <= 2 ? 'weak' : score === 3 ? 'medium' : 'strong';
    segs.forEach((id, i) => {
        const el = document.getElementById(id);
        el.className = 'seg' + (i < score ? ' ' + cls : '');
    });
    checkMatch();
}

/* ── Verificar coincidencia ── */
function checkMatch() {
    const pw1 = document.getElementById('new-pw').value;
    const pw2 = document.getElementById('confirm-pw').value;
    const hint = document.getElementById('hint-match');
    if (!pw2) { hint.textContent = ''; hint.className = 'field-hint'; return; }
    const ok = pw1 === pw2;
    hint.textContent = ok ? 'Las contraseñas coinciden ✓' : 'Las contraseñas no coinciden';
    hint.className = 'field-hint ' + (ok ? 'ok' : 'error');
}