# ORM/crud_canciones.py
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
from orm_models import engine, VistaCancionesCompletas
from models import Cancion, Album, Usuario, Genero, CancionGenero
from datetime import timedelta
from sqlalchemy import select
from flask import jsonify
from collections import defaultdict
from sqlalchemy import text
from flask import send_file
import csv
import io
import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


crud_canciones = Blueprint('crud_canciones', __name__)
Session = sessionmaker(bind=engine)

@crud_canciones.route('/canciones')
def index_canciones():
    session = Session()
    canciones = session.query(VistaCancionesCompletas).all()
    claves = [r['clave'] for r in session.execute(text("SELECT unnest(enum_range(NULL::clave_musical)) AS clave")).mappings()]


    # Convertir resultados a dicts para evitar errores de serialización
    raw_albums = session.query(Album.id, Album.titulo, Album.artista_id).all()
    albums = [dict(a._mapping) for a in raw_albums]

    raw_artistas = session.query(Usuario.id, Usuario.nombre).filter(Usuario.rol == 'artista').all()
    artistas = [dict(a._mapping) for a in raw_artistas]

    generos = [dict(g._mapping) for g in session.query(Genero.id, Genero.nombre).all()]

    artista_album_map = defaultdict(list)
    for album in albums:
        artista_album_map[str(album["artista_id"])].append({
            "id": album["id"],
            "nombre": album["titulo"]
        })

    session.close()
    return render_template("canciones/index.html",
        canciones=canciones,
        albums=albums,
        artistas=artistas,
        generos=generos,
        claves=claves,
        artista_album_map=dict(artista_album_map)  # Convertir defaultdict a dict
    )


@crud_canciones.route('/canciones/actualizar_en_linea/<int:id>', methods=['POST'])
def actualizar_cancion_en_linea(id):
    data = request.get_json()
    session = Session()

    try:
        cancion = session.query(Cancion).get(id)
        if not cancion:
            return jsonify({"error": "Canción no encontrada"}), 404

        cancion.nombre = data.get('nombre')
        cancion.album_id = int(data.get('album'))
        cancion_genero = session.query(CancionGenero).filter_by(cancion_id=id).first()
        if cancion_genero:
            cancion_genero.genero_id = int(data.get('genero'))

        session.commit()
        return jsonify({"mensaje": "Canción actualizada exitosamente"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@crud_canciones.route('/canciones/crear', methods=['GET', 'POST'])
def crear_cancion():
    if request.method == 'POST':
        session = Session()
        nueva = Cancion(
            album_id=int(request.form['album_id']),
            nombre=request.form['nombre'],
            duracion=timedelta(minutes=int(request.form['min']), seconds=int(request.form['sec'])),
            clave=request.form['clave'],
            licencia_id=int(request.form['licencia_id'])
        )
        session.add(nueva)
        session.commit()
        session.close()
        return redirect(url_for('crud_canciones.index_canciones'))
    return render_template('canciones/crear.html')

@crud_canciones.route('/canciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_cancion(id):
    session = Session()
    cancion = session.query(Cancion).get(id)
    if request.method == 'POST':
        cancion.nombre = request.form['nombre']
        cancion.duracion = timedelta(minutes=int(request.form['min']), seconds=int(request.form['sec']))
        cancion.clave = request.form['clave']
        session.commit()
        session.close()
        return redirect(url_for('crud_canciones.index_canciones'))
    return render_template('canciones/editar.html', cancion=cancion)

@crud_canciones.route('/canciones/eliminar/<int:id>', methods=['POST'])
def eliminar_cancion(id):
    session = Session()
    try:
        # Eliminar colaboraciones, géneros, archivos, historial, etc. relacionados a la canción
        session.execute(text("DELETE FROM colaboracion WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM cancion_genero WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM archivo_multimedia WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM historial_cambios WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM playlist_cancion WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM comentario WHERE cancion_id = :id"), {"id": id})
        session.execute(text("DELETE FROM metrica_cancion WHERE cancion_id = :id"), {"id": id})

        # Ahora sí puedes borrar la canción
        session.execute(text("DELETE FROM cancion WHERE id = :id"), {"id": id})
        session.commit()
        return redirect(url_for('crud_canciones.index_canciones'))
    except Exception as e:
        session.rollback()
        return f"❌ Error: {e}", 500
    finally:
        session.close()


@crud_canciones.route('/canciones/crear_ajax', methods=['POST'])
def crear_cancion_ajax():
    data = request.get_json()
    session = Session()

    try:
        duracion = data['duracion']
        h, m, s = map(int, duracion.split(':'))
        from datetime import timedelta
        nueva = Cancion(
            album_id=int(data['album_id']),
            nombre=data['nombre'],
            duracion=timedelta(hours=h, minutes=m, seconds=s),
            clave=data['clave'],
            licencia_id=1
        )
        session.add(nueva)
        session.flush()

        # Si mandó género, crear o asociar
        genero_nombre = data.get('genero_nombre')
        if genero_nombre:
            from models import Genero, CancionGenero
            genero = session.query(Genero).filter_by(nombre=genero_nombre).first()
            if not genero:
                genero = Genero(nombre=genero_nombre)
                session.add(genero)
                session.flush()
            session.add(CancionGenero(cancion_id=nueva.id, genero_id=genero.id))

        session.commit()
        return jsonify({"mensaje": "Creado"})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



@crud_canciones.route("/reporte_canciones", methods=["GET"])
def reporte_canciones():
    session = Session()
    query = session.query(VistaCancionesCompletas)

    # Filtros desde GET
    artista = request.args.get("artista")
    album = request.args.get("album")
    genero = request.args.get("genero")
    clave = request.args.get("clave")
    duracion = request.args.get("duracion")

    # Aplicar filtros si existen
    if artista:
        query = query.filter(VistaCancionesCompletas.artista == artista)
    if album:
        query = query.filter(VistaCancionesCompletas.album == album)
    if genero:
        query = query.filter(VistaCancionesCompletas.genero == genero)
    if clave:
        query = query.filter(VistaCancionesCompletas.clave == clave)
    if duracion:
        if duracion == "3":
            query = query.filter(VistaCancionesCompletas.duracion.between("0:03:00", "0:03:59"))
        elif duracion == "4":
            query = query.filter(VistaCancionesCompletas.duracion.between("0:04:00", "0:04:59"))
        elif duracion == "5":
            query = query.filter(VistaCancionesCompletas.duracion.between("0:05:00", "0:05:59"))

    resultados = query.all()

    # ✅ Datos auxiliares para los filtros
        # ✅ Datos auxiliares para filtros (sin valores nulos)
    artistas = [r[0] for r in session.query(VistaCancionesCompletas.artista)
                                   .filter(VistaCancionesCompletas.artista.isnot(None))
                                   .distinct().order_by(VistaCancionesCompletas.artista).all()]

    albumes = [r[0] for r in session.query(VistaCancionesCompletas.album)
                                   .filter(VistaCancionesCompletas.album.isnot(None))
                                   .distinct().order_by(VistaCancionesCompletas.album).all()]

    generos = [r[0] for r in session.query(VistaCancionesCompletas.genero)
                                   .filter(VistaCancionesCompletas.genero.isnot(None))
                                   .distinct().order_by(VistaCancionesCompletas.genero).all()]

    claves = [r[0] for r in session.query(VistaCancionesCompletas.clave).distinct().all()]

    session.close()

    # Exportar
    formato = request.args.get("formato")
    if formato == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Nombre", "Álbum", "Artista", "Género", "Duración", "Clave"])
        for c in resultados:
            writer.writerow([c.cancion_id, c.nombre_cancion, c.album, c.artista, c.genero, c.duracion, c.clave])
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), download_name="reporte_canciones.csv", as_attachment=True)

    elif formato == "json":
        data = [
            {
                "id": c.cancion_id,
                "nombre": c.nombre_cancion,
                "album": c.album,
                "artista": c.artista,
                "genero": c.genero,
                "duracion": str(c.duracion),
                "clave": c.clave
            }
            for c in resultados
        ]
        return send_file(io.BytesIO(json.dumps(data, indent=2).encode()), download_name="reporte_canciones.json", as_attachment=True)

    elif formato == "pdf":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        data = [["ID", "Nombre", "Álbum", "Artista", "Género", "Duración", "Clave"]]
        for c in resultados:
            data.append([c.cancion_id, c.nombre_cancion, c.album, c.artista, c.genero, str(c.duracion), c.clave])
        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        doc.build([tabla])
        output.seek(0)
        return send_file(output, download_name="reporte_canciones.pdf", as_attachment=True)

    # ✅ Render con filtros
    return render_template("canciones/reporte.html",
        canciones=resultados,
        artistas=artistas,
        albumes=albumes,
        generos=generos,
        claves=claves
    )
