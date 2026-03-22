/* ── Estado global ── */
let modelo = null;
let streamCamara = null;
let resultadoActual = null;
let tabActivo = 'camara';

/* ── Mapeo MobileNet → categorías EcoVision ── */
const CATEGORIAS = {
    bottle: { nombre: 'Botella PET', tipo: 'Plástico', emoji: '♻️', reciclable: true, contenedor: 'Azul (plástico)', precio: 400 },
    water_bottle: { nombre: 'Botella de agua', tipo: 'Plástico', emoji: '💧', reciclable: true, contenedor: 'Azul (plástico)', precio: 400 },
    pop_bottle: { nombre: 'Botella plástica', tipo: 'Plástico', emoji: '🥤', reciclable: true, contenedor: 'Azul (plástico)', precio: 350 },
    wine_bottle: { nombre: 'Botella de vidrio', tipo: 'Vidrio', emoji: '🍾', reciclable: true, contenedor: 'Verde (vidrio)', precio: 180 },
    beer_bottle: { nombre: 'Botella de vidrio', tipo: 'Vidrio', emoji: '🍺', reciclable: true, contenedor: 'Verde (vidrio)', precio: 180 },
    can: { nombre: 'Lata de aluminio', tipo: 'Metal', emoji: '🥫', reciclable: true, contenedor: 'Gris (metal)', precio: 2500 },
    tin_can: { nombre: 'Lata metálica', tipo: 'Metal', emoji: '🥫', reciclable: true, contenedor: 'Gris (metal)', precio: 600 },
    newspaper: { nombre: 'Periódico', tipo: 'Papel', emoji: '📰', reciclable: true, contenedor: 'Gris (papel)', precio: 100 },
    book: { nombre: 'Papel / Libro', tipo: 'Papel', emoji: '📄', reciclable: true, contenedor: 'Gris (papel)', precio: 200 },
    envelope: { nombre: 'Cartón', tipo: 'Papel', emoji: '📦', reciclable: true, contenedor: 'Gris (papel)', precio: 120 },
    banana: { nombre: 'Residuo orgánico', tipo: 'Orgánico', emoji: '🍌', reciclable: false, contenedor: 'Marrón (orgánico)', precio: 0 },
    apple: { nombre: 'Residuo orgánico', tipo: 'Orgánico', emoji: '🍎', reciclable: false, contenedor: 'Marrón (orgánico)', precio: 0 },
    orange: { nombre: 'Residuo orgánico', tipo: 'Orgánico', emoji: '🍊', reciclable: false, contenedor: 'Marrón (orgánico)', precio: 0 },
};

const CONSEJOS = {
    'Plástico': 'Enjuaga el envase y retira la tapa antes de depositarlo.',
    'Papel': 'Mantén el papel seco y libre de grasa para que sea reciclable.',
    'Vidrio': 'Retira tapas metálicas antes de depositarlo en el contenedor verde.',
    'Metal': 'Aplasta las latas para ahorrar espacio. El aluminio es muy valioso.',
    'Orgánico': 'Los residuos orgánicos van al compostaje, no al reciclaje común.',
    'General': 'Limpia y seca el material antes de reciclarlo.',
};

/* ── Inicializar MobileNet ── */
async function cargarModelo() {
    try {
        modelo = await mobilenet.load();
        console.log('MobileNet cargado ✓');
        iniciarCamara();
    } catch (e) {
        console.error('Error cargando MobileNet:', e);
    }
}

/* ── Cámara ── */
async function iniciarCamara() {
    const video = document.getElementById('video');
    const hint = document.getElementById('camara-hint');
    const btn = document.getElementById('btn-capture');
    try {
        streamCamara = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        video.srcObject = streamCamara;
        video.style.display = 'block';
        hint.textContent = 'Apunta al residuo y captura';
        btn.disabled = false;
    } catch (e) {
        hint.textContent = 'Cámara no disponible — usa la galería';
        document.getElementById('tab-galeria').click();
    }
}

function detenerCamara() {
    if (streamCamara) {
        streamCamara.getTracks().forEach(t => t.stop());
        streamCamara = null;
    }
}

/* ── Capturar foto ── */
function capturarFoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas-capture');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    clasificarCanvas(canvas);
}

/* ── Galería ── */
function cargarImagen(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        const img = document.getElementById('preview-img');
        img.src = e.target.result;
        img.style.display = 'block';
        document.getElementById('btn-analizar').style.display = 'block';
        document.querySelector('.drop-zone').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function soltar(event) {
    event.preventDefault();
    document.querySelector('.drop-zone').classList.remove('drag-over');
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        const input = document.getElementById('input-file');
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        cargarImagen({ target: input });
    }
}

function clasificarImagen() {
    const img = document.getElementById('preview-img');
    const canvas = document.getElementById('canvas-capture');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    canvas.getContext('2d').drawImage(img, 0, 0);
    clasificarCanvas(canvas);
}

/* ── Clasificar con MobileNet ── */
async function clasificarCanvas(canvas) {
    mostrarLoader();
    try {
        if (!modelo) modelo = await mobilenet.load();
        const predicciones = await modelo.classify(canvas, 3);
        const top = predicciones[0];
        procesarResultado(top.className, top.probability);
    } catch (e) {
        console.error('Error en clasificación:', e);
        mostrarPlaceholder();
    }
}

/* ── Procesar resultado ── */
function procesarResultado(label, probabilidad) {
    const labelLower = label.toLowerCase().replace(/ /g, '_').split(',')[0].trim();

    let cat = null;
    for (const [key, val] of Object.entries(CATEGORIAS)) {
        if (labelLower.includes(key)) { cat = val; break; }
    }

    if (!cat) {
        cat = {
            nombre: label.split(',')[0].trim(),
            tipo: 'General', emoji: '❓',
            reciclable: false, contenedor: 'Negro (general)', precio: 0
        };
    }

    const confianza = Math.round(probabilidad * 100);
    resultadoActual = { ...cat, confianza, label_ia: label };

    mostrarResultado(resultadoActual);
}

/* ── Mostrar resultado en UI ── */
function mostrarResultado(r) {
    document.getElementById('resultado-loader').style.display = 'none';
    document.getElementById('resultado-placeholder').style.display = 'none';
    document.getElementById('resultado-card').style.display = 'block';

    document.getElementById('res-emoji').textContent = r.emoji;
    document.getElementById('res-nombre').textContent = r.nombre;
    document.getElementById('res-tipo').textContent = r.tipo;
    document.getElementById('confianza-val').textContent = r.confianza + '%';
    document.getElementById('confianza-fill').style.width = r.confianza + '%';
    document.getElementById('info-contenedor').textContent = r.contenedor;
    document.getElementById('info-precio').textContent = r.precio > 0 ? `$${r.precio}/kg` : 'Sin valor';
    document.getElementById('info-categoria').textContent = r.tipo;
    document.getElementById('info-estado').textContent = r.reciclable ? '✓ Reciclable' : '✗ No reciclable';
    document.getElementById('info-estado').style.color = r.reciclable ? '#52b788' : '#f4845f';
    document.getElementById('consejo-text').textContent = CONSEJOS[r.tipo] || CONSEJOS['General'];
    document.getElementById('btn-guardar').disabled = false;
}

/* ── Guardar en historial ── */
async function guardarHistorial() {
    if (!resultadoActual) return;
    const btn = document.getElementById('btn-guardar');
    btn.disabled = true;
    btn.textContent = 'Guardando...';

    try {
        const res = await fetch('/clasificador/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resultadoActual)
        });
        const data = await res.json();
        btn.textContent = data.ok ? '✓ Guardado en historial' : '✗ Error al guardar';
        if (!data.ok) setTimeout(() => { btn.disabled = false; btn.textContent = 'Guardar en historial'; }, 2000);
    } catch (e) {
        btn.textContent = '✗ Error de conexión';
        setTimeout(() => { btn.disabled = false; btn.textContent = 'Guardar en historial'; }, 2000);
    }
}

/* ── Nuevo residuo ── */
function nuevoResiduo() {
    resultadoActual = null;
    mostrarPlaceholder();
    if (tabActivo === 'galeria') {
        document.getElementById('preview-img').style.display = 'none';
        document.getElementById('btn-analizar').style.display = 'none';
        document.querySelector('.drop-zone').style.display = 'block';
        document.getElementById('input-file').value = '';
    }
}

/* ── Estados UI ── */
function mostrarLoader() {
    document.getElementById('resultado-placeholder').style.display = 'none';
    document.getElementById('resultado-card').style.display = 'none';
    document.getElementById('resultado-loader').style.display = 'block';
}

function mostrarPlaceholder() {
    document.getElementById('resultado-loader').style.display = 'none';
    document.getElementById('resultado-card').style.display = 'none';
    document.getElementById('resultado-placeholder').style.display = 'block';
}

/* ── Switch tabs ── */
function switchTab(tab) {
    tabActivo = tab;
    const isCamera = tab === 'camara';
    document.getElementById('panel-camara').style.display = isCamera ? 'block' : 'none';
    document.getElementById('panel-galeria').style.display = isCamera ? 'none' : 'block';
    document.getElementById('tab-camara').classList.toggle('activo', isCamera);
    document.getElementById('tab-galeria').classList.toggle('activo', !isCamera);
    document.getElementById('tab-slider').classList.toggle('right', !isCamera);
    if (isCamera) iniciarCamara();
    else detenerCamara();
    mostrarPlaceholder();
}

/* ── Iniciar ── */
document.addEventListener('DOMContentLoaded', cargarModelo);