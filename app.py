from flask import Flask, render_template, request, jsonify
from pathlib import Path
from datetime import datetime
import json
import base64
import re

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DRAWINGS_DIR = BASE_DIR / "static" / "drawings"
LETTERS_FILE = DATA_DIR / "cartas.json"

DATA_DIR.mkdir(exist_ok=True)
DRAWINGS_DIR.mkdir(parents=True, exist_ok=True)

def load_letters():
    if not LETTERS_FILE.exists():
        return []
    try:
        return json.loads(LETTERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def save_letters(letters):
    LETTERS_FILE.write_text(
        json.dumps(letters, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def next_id(letters):
    if not letters:
        return 1
    return max(letter["id"] for letter in letters) + 1

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/cartas")
def get_letters():
    letters = load_letters()
    return jsonify([
        {
            "id": letter["id"],
            "nombre": f"Carta Nº{letter['id']}",
            "de": letter["de"],
            "para": letter["para"]
        }
        for letter in letters
    ])

@app.get("/api/cartas/<int:letter_id>")
def get_letter(letter_id):
    letters = load_letters()
    letter = next((x for x in letters if x["id"] == letter_id), None)

    if letter is None:
        return jsonify({"error": "Carta no encontrada"}), 404

    return jsonify(letter)

@app.post("/api/cartas")
def create_letter():
    payload = request.get_json(silent=True) or {}

    de = str(payload.get("de", "")).strip()
    para = str(payload.get("para", "")).strip()
    carta = str(payload.get("carta", "")).strip()
    dibujo = payload.get("dibujo", "")

    if not de or not para or not carta:
        return jsonify({
            "error": "Los campos De, Para y Escriba carta son obligatorios."
        }), 400

    if not isinstance(dibujo, str) or not dibujo.startswith("data:image/png;base64,"):
        return jsonify({"error": "El dibujo no es válido."}), 400

    # Formato solicitado para el archivo de texto.
    texto = f"De: {de}\nPara: {para}\n{carta}"

    letters = load_letters()
    letter_id = next_id(letters)

    texto_filename = f"texto_{letter_id:07d}.txt"
    imagen_filename = f"imagen_{letter_id:07d}.png"

    # Se guardan dentro de una carpeta propia para cada carta.
    letter_dir = DATA_DIR / f"Carta_{letter_id:07d}"
    letter_dir.mkdir(exist_ok=True)

    (letter_dir / texto_filename).write_text(texto, encoding="utf-8")

    try:
        image_data = dibujo.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
    except (IndexError, ValueError, base64.binascii.Error):
        return jsonify({"error": "No se pudo guardar el dibujo."}), 400

    drawing_path = DRAWINGS_DIR / imagen_filename
    drawing_path.write_bytes(image_bytes)

    letter = {
        "id": letter_id,
        "de": de,
        "para": para,
        "carta": carta,
        "texto": texto,
        "texto_filename": texto_filename,
        "imagen_filename": imagen_filename,
        "imagen_url": f"/static/drawings/{imagen_filename}",
        "creada": datetime.now().isoformat(timespec="seconds")
    }

    letters.append(letter)
    save_letters(letters)

    return jsonify({
        "ok": True,
        "id": letter_id,
        "nombre": f"Carta Nº{letter_id}"
    }), 201

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)
