from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import os
import base64
import binascii

app = Flask(__name__)


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Faltan las variables de entorno SUPABASE_URL y SUPABASE_KEY."
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BUCKET_NAME = "dibujos"


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# OBTENER TODAS LAS CARTAS
# =========================================================

@app.get("/api/cartas")
def get_letters():

    try:
        response = (
            supabase
            .table("cartas")
            .select("id, de, para")
            .order("id", desc=False)
            .execute()
        )

        letters = response.data or []

        return jsonify([
            {
                "id": letter["id"],
                "nombre": f"Carta Nº{letter['id']}",
                "de": letter["de"],
                "para": letter["para"]
            }
            for letter in letters
        ])

    except Exception as error:

        print("ERROR AL OBTENER CARTAS:", error)

        return jsonify({
            "error": "No se pudieron cargar las cartas."
        }), 500


# =========================================================
# OBTENER UNA CARTA
# =========================================================

@app.get("/api/cartas/<int:letter_id>")
def get_letter(letter_id):

    try:

        response = (
            supabase
            .table("cartas")
            .select("*")
            .eq("id", letter_id)
            .single()
            .execute()
        )

        letter = response.data

        if not letter:
            return jsonify({
                "error": "Carta no encontrada"
            }), 404

        return jsonify(letter)

    except Exception as error:

        print("ERROR AL OBTENER CARTA:", error)

        return jsonify({
            "error": "Carta no encontrada"
        }), 404


# =========================================================
# CREAR UNA CARTA
# =========================================================

@app.post("/api/cartas")
def create_letter():

    payload = request.get_json(silent=True) or {}

    de = str(payload.get("de", "")).strip()
    para = str(payload.get("para", "")).strip()
    carta = str(payload.get("carta", "")).strip()
    dibujo = payload.get("dibujo", "")


    # -----------------------------------------------------
    # VALIDAR DATOS
    # -----------------------------------------------------

    if not de or not para or not carta:

        return jsonify({
            "error": "Los campos De, Para y Escriba carta son obligatorios."
        }), 400


    if (
        not isinstance(dibujo, str)
        or not dibujo.startswith("data:image/png;base64,")
    ):

        return jsonify({
            "error": "El dibujo no es válido."
        }), 400


    # -----------------------------------------------------
    # PREPARAR TEXTO
    # -----------------------------------------------------

    texto = f"De: {de}\nPara: {para}\n{carta}"


    try:

        # -------------------------------------------------
        # OBTENER SIGUIENTE ID
        # -------------------------------------------------

        response = (
            supabase
            .table("cartas")
            .select("id")
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        existing_letters = response.data or []

        if existing_letters:
            letter_id = int(existing_letters[0]["id"]) + 1
        else:
            letter_id = 1


        # -------------------------------------------------
        # CONVERTIR BASE64 A PNG
        # -------------------------------------------------

        image_data = dibujo.split(",", 1)[1]

        image_bytes = base64.b64decode(
            image_data,
            validate=True
        )


        # -------------------------------------------------
        # NOMBRE DE LA IMAGEN
        # -------------------------------------------------

        imagen_filename = f"imagen_{letter_id:07d}.png"


        # -------------------------------------------------
        # SUBIR IMAGEN A SUPABASE STORAGE
        # -------------------------------------------------

        supabase.storage \
            .from_(BUCKET_NAME) \
            .upload(
                imagen_filename,
                image_bytes,
                {
                    "content-type": "image/png",
                    "upsert": "false"
                }
            )


        # -------------------------------------------------
        # OBTENER URL PÚBLICA
        # -------------------------------------------------

        image_url_response = (
            supabase
            .storage
            .from_(BUCKET_NAME)
            .get_public_url(imagen_filename)
        )

        imagen_url = image_url_response


        # -------------------------------------------------
        # GUARDAR CARTA EN LA BASE DE DATOS
        # -------------------------------------------------

        letter = {
            "id": letter_id,
            "de": de,
            "para": para,
            "carta": carta,
            "texto": texto,
            "imagen_url": imagen_url,
            "creada": datetime.now().isoformat()
        }


        supabase \
            .table("cartas") \
            .insert(letter) \
            .execute()


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return jsonify({
            "ok": True,
            "id": letter_id,
            "nombre": f"Carta Nº{letter_id}"
        }), 201


    except (ValueError, binascii.Error):

        return jsonify({
            "error": "No se pudo procesar el dibujo."
        }), 400


    except Exception as error:

        print("ERROR AL CREAR CARTA:", error)

        return jsonify({
            "error": "No se pudo guardar la carta."
        }), 500


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
