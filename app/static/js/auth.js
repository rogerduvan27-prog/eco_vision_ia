/* ── Tabs ─────────────────────────────────────────────────── */
function switchTab(tab) {
    const isLogin = tab === 'login';

    // Paneles
    document.getElementById('panel-login').style.display = isLogin ? 'block' : 'none';
    document.getElementById('panel-registro').style.display = isLogin ? 'none' : 'block';

    // Tabs activos
    document.querySelectorAll('.tab').forEach((el, i) => {
        el.classList.toggle('active', isLogin ? i === 0 : i === 1);
    });

    // Slider animado
    const slider = document.getElementById('tab-slider');
    slider.classList.toggle('right', !isLogin);

    // Actualizar URL sin recargar
    const path = isLogin ? '/login' : '/registro';
    history.pushState(null, '', path);
}

/* ── Mostrar / ocultar contraseña ─────────────────────────── */
function togglePw(inputId, btn) {
    const input = document.getElementById(inputId);
    const isText = input.type === 'text';
    input.type = isText ? 'password' : 'text';
    btn.style.opacity = isText ? '0.5' : '1';
}

/* ── Validar usuario ──────────────────────────────────────── */
function validarUsuario(input) {
    const v = input.value.trim();
    const hint = document.getElementById('hint-usuario');
    if (!v) { hint.textContent = ''; hint.className = 'field-hint'; return; }

    if (v.length < 3) {
        hint.textContent = 'Mínimo 3 caracteres';
        hint.className = 'field-hint error';
    } else if (/\s/.test(v)) {
        hint.textContent = 'No se permiten espacios';
        hint.className = 'field-hint error';
    } else {
        hint.textContent = 'Usuario válido ✓';
        hint.className = 'field-hint ok';
    }
}

/* ── Validar email ────────────────────────────────────────── */
function validarEmail(input) {
    const v = input.value.trim();
    const hint = document.getElementById('hint-email');
    if (!v) { hint.textContent = ''; hint.className = 'field-hint'; return; }

    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    hint.textContent = ok ? 'Correo válido ✓' : 'Formato inválido (ej: nombre@correo.com)';
    hint.className = 'field-hint ' + (ok ? 'ok' : 'error');
}

/* ── Fortaleza de contraseña ──────────────────────────────── */
function evalFortaleza(input) {
    const pw = input.value;
    const segs = ['seg1', 'seg2', 'seg3', 'seg4'];
    let score = 0;

    if (pw.length >= 8) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;

    const niveles = ['', 'weak', 'weak', 'medium', 'strong'];
    const labels = ['', 'Débil', 'Regular', 'Buena', 'Fuerte 🔒'];

    segs.forEach((id, i) => {
        const el = document.getElementById(id);
        el.className = 'seg' + (i < score ? ' ' + niveles[score] : '');
    });

    const hint = document.getElementById('hint-fortaleza');
    hint.textContent = pw.length ? 'Seguridad: ' + labels[score] : '';
    hint.className = 'field-hint' + (score >= 3 ? ' ok' : score > 0 ? ' error' : '');

    verificarMatch(document.getElementById('confirmar'));
}

/* ── Verificar que las contraseñas coincidan ──────────────── */
function verificarMatch(input) {
    const pw1 = document.getElementById('password-reg').value;
    const pw2 = input.value;
    const hint = document.getElementById('hint-match');

    if (!pw2) { hint.textContent = ''; hint.className = 'field-hint'; return; }

    const coinciden = pw1 === pw2;
    hint.textContent = coinciden ? 'Las contraseñas coinciden ✓' : 'Las contraseñas no coinciden';
    hint.className = 'field-hint ' + (coinciden ? 'ok' : 'error');
}