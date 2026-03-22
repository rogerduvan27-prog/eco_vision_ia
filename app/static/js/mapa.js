/* ── Variables globales ── */
let mapa, marcadorUsuario, capaPuntos = [];
let filtroActivo = 'todos';
let busquedaActiva = '';

const BOGOTA = [4.711, -74.0721];
const ZOOM_INICIAL = 13;

/* ── Íconos personalizados ── */
function crearIcono(color, emoji) {
    return L.divIcon({
        className: '',
        html: `<div style="
      width:36px;height:36px;border-radius:50%;
      background:${color};border:2px solid #0a1a12;
      display:flex;align-items:center;justify-content:center;
      font-size:16px;box-shadow:0 2px 8px rgba(0,0,0,0.4)
    ">${emoji}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -20]
    });
}

const ICONOS = {
    reciclaje: crearIcono('#2d6a4f', '♻️'),
    centro: crearIcono('#185FA5', '🏭'),
    empresa: crearIcono('#854F0B', '🏢')
};

const ICONO_USUARIO = L.divIcon({
    className: '',
    html: `<div style="
    width:16px;height:16px;border-radius:50%;
    background:#378ADD;border:3px solid white;
    box-shadow:0 0 0 4px rgba(55,138,221,0.25)
  "></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});

/* ── Inicializar mapa ── */
function inicializarMapa() {
    mapa = L.map('mapa', { zoomControl: true }).setView(BOGOTA, ZOOM_INICIAL);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19
    }).addTo(mapa);

    PUNTOS.forEach((p, i) => {
        const icono = ICONOS[p.tipo] || ICONOS.reciclaje;
        const marcador = L.marker([p.lat, p.lng], { icon: icono })
            .addTo(mapa)
            .bindPopup(`
        <div style="font-family:'DM Sans',sans-serif;min-width:160px">
          <div style="font-weight:700;font-size:13px;color:#eaf6ee;margin-bottom:4px">${p.emoji} ${p.nombre}</div>
          <div style="font-size:11px;color:#7aaa8f;margin-bottom:3px">${p.direccion}</div>
          <div style="font-size:11px;color:#7aaa8f;margin-bottom:6px">${p.materiales}</div>
          <div style="font-size:10px;font-weight:700;color:${p.abierto ? '#52b788' : '#f4845f'}">
            ${p.abierto ? '● Abierto' : '● Cerrado'}
          </div>
        </div>
      `);
        capaPuntos.push({ marcador, datos: p, index: i });
    });

    obtenerUbicacion();
}

/* ── Geolocalización ── */
function obtenerUbicacion() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
        pos => {
            const { latitude: lat, longitude: lng } = pos.coords;
            if (marcadorUsuario) mapa.removeLayer(marcadorUsuario);
            marcadorUsuario = L.marker([lat, lng], { icon: ICONO_USUARIO })
                .addTo(mapa)
                .bindPopup('<div style="color:#eaf6ee;font-size:12px">📍 Tu ubicación</div>');
            mapa.setView([lat, lng], 14);
            calcularDistancias(lat, lng);
        },
        () => calcularDistancias(BOGOTA[0], BOGOTA[1])
    );
}

/* ── Centrar en ubicación ── */
function centrarUbicacion() {
    obtenerUbicacion();
}

/* ── Calcular distancias ── */
function calcularDistancias(latUser, lngUser) {
    PUNTOS.forEach((p, i) => {
        const dist = distanciaKm(latUser, lngUser, p.lat, p.lng);
        const el = document.getElementById(`dist-${i + 1}`);
        if (el) el.textContent = dist < 1
            ? `${Math.round(dist * 1000)} m`
            : `${dist.toFixed(1)} km`;
    });
}

function distanciaKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

/* ── Ir a un punto al hacer clic ── */
function irAPunto(lat, lng, nombre) {
    mapa.setView([lat, lng], 16);
    capaPuntos.forEach(cp => {
        if (cp.datos.lat === lat && cp.datos.lng === lng) {
            cp.marcador.openPopup();
        }
    });
}

/* ── Filtrar por tipo ── */
function filtrar(btn) {
    filtroActivo = btn.dataset.tipo;
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    aplicarFiltros();
}

/* ── Buscar por nombre ── */
function buscar(texto) {
    busquedaActiva = texto.toLowerCase().trim();
    aplicarFiltros();
}

/* ── Aplicar filtros combinados ── */
function aplicarFiltros() {
    let visibles = 0;
    document.querySelectorAll('.punto-card').forEach(card => {
        const tipoOk = filtroActivo === 'todos' || card.dataset.tipo === filtroActivo;
        const nombreOk = !busquedaActiva || card.dataset.nombre.includes(busquedaActiva);
        const mostrar = tipoOk && nombreOk;
        card.classList.toggle('oculto', !mostrar);
        if (mostrar) visibles++;
    });

    capaPuntos.forEach(cp => {
        const tipoOk = filtroActivo === 'todos' || cp.datos.tipo === filtroActivo;
        const nombreOk = !busquedaActiva || cp.datos.nombre.toLowerCase().includes(busquedaActiva);
        if (tipoOk && nombreOk) {
            if (!mapa.hasLayer(cp.marcador)) cp.marcador.addTo(mapa);
        } else {
            if (mapa.hasLayer(cp.marcador)) mapa.removeLayer(cp.marcador);
        }
    });

    const countEl = document.getElementById('count');
    if (countEl) countEl.textContent = `${visibles} puntos`;
}

/* ── Iniciar al cargar ── */
document.addEventListener('DOMContentLoaded', inicializarMapa);