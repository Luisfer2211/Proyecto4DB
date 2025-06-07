from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm_models import VistaCancionesCompletas, VistaResenasAlbum, Base
from crud_canciones import crud_canciones
from crud_resenas import crud_resenas
from orm_models import VistaAlbumesDetalles


from sqlalchemy import text

import os

# Leer contraseña desde archivo
with open("contraseña.txt", "r", encoding="utf-8") as f:
    password = f.read().strip()

# Configurar Flask y SQLAlchemy
app = Flask(__name__)
DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/produccion_musical_db"
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)
app.register_blueprint(crud_canciones)

app.register_blueprint(crud_resenas) 

# Ruta principal
@app.route("/")
def home():
    return render_template("index.html")

# CRUD 1: Vista de Canciones
@app.route("/canciones")
def canciones():
    session = SessionLocal()

    canciones = session.query(VistaCancionesCompletas).all()

    # ✅ Serializar correctamente con mappings().all() y list(dict(...))
    usuarios = [dict(r) for r in session.execute(text("SELECT id, nombre FROM usuario WHERE rol = 'artista'")).mappings()]
    albumes = [dict(r) for r in session.execute(text("SELECT id, titulo, artista_id FROM album")).mappings()]
    generos = [dict(r) for r in session.execute(text("SELECT id, nombre FROM genero")).mappings()]
    claves = [r['clave'] for r in session.execute(text("SELECT unnest(enum_range(NULL::clave_musical)) AS clave")).mappings()]

    # ✅ Construir mapa para combobox dependiente
    artista_album_map = {
        str(a["id"]): [
            {"id": al["id"], "titulo": al["titulo"]}
            for al in albumes if al["artista_id"] == a["id"]
        ]
        for a in usuarios
    }

    session.close()
    return render_template("canciones/index.html",
        canciones=canciones,
        artistas=usuarios,
        albumes=albumes,
        generos=generos,
        claves=claves,
        artista_album_map=artista_album_map
    )



# CRUD 2: Vista de Reseñas
@app.route("/resenas")
def resenas():
    session = SessionLocal()
    resenas = session.query(VistaResenasAlbum).all()
    session.close()
    return render_template("resenas/index.html", resenas=resenas)

# CRUD 3: Vista de Álbumes
@app.route("/albumes")
def albumes():
    session = SessionLocal()
    albumes = session.query(VistaAlbumesDetalles).all()

    # Obtener lista de artistas
    artistas = [dict(r) for r in session.execute(text("SELECT id, nombre FROM usuario WHERE rol = 'artista'")).mappings()]

    session.close()
    return render_template("albumes/index.html", albumes=albumes, artistas=artistas)

# Correr la app
if __name__ == "__main__":
    app.run(debug=True)
