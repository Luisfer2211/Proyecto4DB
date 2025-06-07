from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from sqlalchemy.orm import sessionmaker
from orm_models import engine, VistaResenasAlbum
from models import Resena, Usuario, Album
from collections import defaultdict
from sqlalchemy import text
from datetime import datetime

crud_resenas = Blueprint('crud_resenas', __name__)
Session = sessionmaker(bind=engine)

@crud_resenas.route("/resenas")
def index_resenas():
    session = Session()
    resenas = session.query(VistaResenasAlbum).all()

    # Críticos: usuarios que no son artistas
    criticos = [dict(c._mapping) for c in session.query(Usuario.id, Usuario.nombre)]

    # Artistas: usuarios que sí son artistas
    artistas = [dict(a._mapping) for a in session.query(Usuario.id, Usuario.nombre).filter(Usuario.rol == 'artista')]

    # Álbumes
    albumes = [dict(a._mapping) for a in session.query(Album.id, Album.titulo, Album.artista_id)]

    # Mapa artista → álbumes
    artista_album_map = defaultdict(list)
    for album in albumes:
        artista_album_map[str(album['artista_id'])].append({
            "id": album['id'],
            "nombre": album['titulo']
        })

    session.close()
    return render_template("resenas/index.html",
        resenas=resenas,
        criticos=criticos,
        artistas=artistas,
        artista_album_map=dict(artista_album_map)
    )

@crud_resenas.route("/resenas/crear", methods=["POST"])
def crear_resena():
    data = request.get_json()
    session = Session()

    try:
        nueva = Resena(
            usuario_id=int(data["critico_id"]),
            album_id=int(data["album_id"]),
            puntaje=int(data["puntaje"]),
            texto=data["texto"],
            anio=int(data["anio"]),
            fecha=datetime.now()
        )
        session.add(nueva)
        session.commit()
        return jsonify({"mensaje": "Reseña creada correctamente"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@crud_resenas.route("/resenas/actualizar/<int:id>", methods=["POST"])
def actualizar_resena(id):
    data = request.get_json()
    session = Session()

    try:
        resena = session.query(Resena).get(id)
        if not resena:
            return jsonify({"error": "No encontrada"}), 404

        resena.usuario_id = int(data["critico"])
        resena.album_id = int(data["album"])
        resena.puntaje = int(data["puntaje"])
        resena.texto = data["texto"]
        resena.anio = int(data["anio"])

        session.commit()
        return jsonify({"mensaje": "Reseña actualizada"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@crud_resenas.route("/resenas/eliminar/<int:id>", methods=["POST"])
def eliminar_resena(id):
    session = Session()
    try:
        resena = session.query(Resena).get(id)
        session.delete(resena)
        session.commit()
        return redirect(url_for("crud_resenas.index_resenas"))  # ← Usa el nombre real de la vista
    except Exception as e:
        session.rollback()
        return f"❌ Error: {e}", 500
    finally:
        session.close()



@crud_resenas.route("/resenas/actualizar_en_linea/<int:id>", methods=["POST"])
def actualizar_resena_en_linea(id):
    session = Session()
    data = request.get_json()

    try:
        resena = session.query(Resena).get(id)
        if not resena:
            return jsonify({"error": "Reseña no encontrada"}), 404

        resena.critico_id = int(data.get("critico"))
        resena.album_id = int(data.get("album"))
        resena.puntaje = int(data.get("puntaje"))
        resena.texto = data.get("texto")

        session.commit()
        return jsonify({"mensaje": "Reseña actualizada correctamente"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
