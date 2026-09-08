# Cartas

Aplicación web para escribir cartas y realizar un dibujo con mouse o pantalla táctil.

## Estructura

- `app.py`: servidor Flask y API.
- `templates/index.html`: estructura HTML.
- `static/js/app.js`: pestañas, dibujo y comunicación con Flask.
- `static/css/style.css`: hoja CSS preparada para estilos futuros.
- `data/`: archivos de texto y registro de cartas.
- `static/drawings/`: imágenes PNG generadas.

## Ejecutar localmente

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Luego:

```bash
pip install -r requirements.txt
python app.py
```

Abrir:

`http://127.0.0.1:5000`

## Deploy

GitHub puede almacenar el código, pero GitHub Pages no ejecuta Python/Flask.

Para desplegar esta aplicación, conecta el repositorio de GitHub a un servicio que ejecute Flask, por ejemplo Render, y utiliza:

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```

Nota: el ejemplo usa el sistema de archivos para guardar las cartas. En un servicio cloud con almacenamiento efímero se necesitará un almacenamiento persistente para conservarlas después de reinicios o redeploys.
