const tabCartas = document.getElementById("tab-cartas");
const tabEscribir = document.getElementById("tab-escribir");

const vistaEscribir = document.getElementById("vista-escribir");
const vistaCartas = document.getElementById("vista-cartas");

const formCarta = document.getElementById("form-carta");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const limpiarDibujo = document.getElementById("limpiar-dibujo");
const mensaje = document.getElementById("mensaje");

const listaCartas = document.getElementById("lista-cartas");
const detalleCarta = document.getElementById("detalle-carta");
const detalleTitulo = document.getElementById("detalle-titulo");
const detalleTexto = document.getElementById("detalle-texto");
const detalleImagen = document.getElementById("detalle-imagen");

let dibujando = false;


// =========================================
// PESTAÑAS
// =========================================

tabCartas.addEventListener("click", () => {
    vistaEscribir.hidden = true;
    vistaCartas.hidden = false;
    cargarListaCartas();
});

tabEscribir.addEventListener("click", () => {
    vistaEscribir.hidden = false;
    vistaCartas.hidden = true;
});




// =========================================
// CANVAS: MOUSE + PANTALLA TÁCTIL
// =========================================

function obtenerPosicion(event) {
    const rect = canvas.getBoundingClientRect();

    let clientX;
    let clientY;

    if (event.touches && event.touches.length > 0) {
        clientX = event.touches[0].clientX;
        clientY = event.touches[0].clientY;
    } else {
        clientX = event.clientX;
        clientY = event.clientY;
    }

    return {
        x: (clientX - rect.left) * (canvas.width / rect.width),
        y: (clientY - rect.top) * (canvas.height / rect.height)
    };
}

function comenzarDibujo(event) {
    event.preventDefault();

    dibujando = true;

    const posicion = obtenerPosicion(event);

    ctx.beginPath();
    ctx.moveTo(posicion.x, posicion.y);
}

function dibujar(event) {
    if (!dibujando) return;

    event.preventDefault();

    const posicion = obtenerPosicion(event);

    ctx.lineTo(posicion.x, posicion.y);
    ctx.stroke();
}

function terminarDibujo(event) {
    if (event) event.preventDefault();

    dibujando = false;
    ctx.closePath();
}

canvas.addEventListener("mousedown", comenzarDibujo);
canvas.addEventListener("mousemove", dibujar);
canvas.addEventListener("mouseup", terminarDibujo);
canvas.addEventListener("mouseleave", terminarDibujo);

canvas.addEventListener("touchstart", comenzarDibujo, { passive: false });
canvas.addEventListener("touchmove", dibujar, { passive: false });
canvas.addEventListener("touchend", terminarDibujo, { passive: false });


// =========================================
// LIMPIAR DIBUJO
// =========================================

function limpiarCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

limpiarDibujo.addEventListener("click", limpiarCanvas);


// =========================================
// ENVIAR CARTA
// =========================================

formCarta.addEventListener("submit", async (event) => {
    event.preventDefault();

    const de = document.getElementById("de").value;
    const para = document.getElementById("para").value;
    const carta = document.getElementById("carta").value;

    // Convierte el dibujo del canvas a PNG.
    const dibujo = canvas.toDataURL("image/png");

    mensaje.textContent = "Guardando carta...";

    try {
        const response = await fetch("/api/cartas", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                de: de,
                para: para,
                carta: carta,
                dibujo: dibujo
            })
        });

        const resultado = await response.json();

        if (!response.ok) {
            throw new Error(resultado.error || "Error al guardar la carta.");
        }

        mensaje.textContent =
            `${resultado.nombre} enviada.`;

        formCarta.reset();
        limpiarCanvas();

    } catch (error) {
        mensaje.textContent = error.message;
    }
});


// =========================================
// LISTA DE CARTAS
// =========================================

async function cargarListaCartas() {
    listaCartas.innerHTML = "Cargando...";
    detalleCarta.hidden = true;

    try {
        const response = await fetch("/api/cartas");

        if (!response.ok) {
            throw new Error("No se pudieron cargar las cartas.");
        }

        const cartas = await response.json();

        listaCartas.innerHTML = "";

        if (cartas.length === 0) {
            listaCartas.textContent = "Todavía no hay cartas.";
            return;
        }

        cartas.forEach((carta) => {
            const boton = document.createElement("button");

            boton.type = "button";
            boton.textContent = carta.nombre;

            boton.addEventListener("click", () => {
                mostrarCarta(carta.id);
            });

            listaCartas.appendChild(boton);
        });

    } catch (error) {
        listaCartas.textContent = error.message;
    }
}


// =========================================
// MOSTRAR UNA CARTA
// =========================================

async function mostrarCarta(id) {
    try {
        const response = await fetch(`/api/cartas/${id}`);

        if (!response.ok) {
            throw new Error("No se pudo cargar la carta.");
        }

        const carta = await response.json();

        detalleTitulo.textContent = `Carta Nº${String(carta.id)}`;

        // textContent evita interpretar el texto de la carta como HTML.
        detalleTexto.textContent = carta.texto;

        detalleImagen.src = carta.imagen_url;
        detalleImagen.alt = `Dibujo de Carta_${String(carta.id).padStart(3, "0")}`;

        detalleCarta.hidden = false;

    } catch (error) {
        detalleTitulo.textContent = "Error";
        detalleTexto.textContent = error.message;
        detalleCarta.hidden = false;
    }
}


// =========================================
// CONFIGURACIÓN INICIAL DEL CANVAS
// =========================================

ctx.lineWidth = 3;
ctx.lineCap = "round";
ctx.lineJoin = "round";
