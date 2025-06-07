from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import random

from models import (
    Base, Usuario, Artista, Productor, Genero, Estudio, Instrumento, Licencia, Album,
    Cancion, Playlist, Colaboracion, CancionGenero, PlaylistCancion, Grabacion,
    InstrumentoGrabacion, ArchivoMultimedia, HistorialCambios, Comentario, Resena,
    MetricaCancion, SelloDiscografico, Contrato
)

with open("contraseña.txt", "r", encoding="utf-8") as f:
    password = f.read().strip()

DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/produccion_musical_db"

engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Función de fecha aleatoria
def random_date():
    return date.today() - timedelta(days=random.randint(100, 2000))

# Archivo de logs SQL
insert_log = []

def log_insert(sql):
    insert_log.append(sql)

# 1. Usuarios
usuarios = [
    Usuario(nombre="Taylor Swift", email="taylor@mail.com", rol="artista"),
    Usuario(nombre="Bad Bunny", email="bunny@mail.com", rol="artista"),
    Usuario(nombre="The Weeknd", email="weeknd@mail.com", rol="artista"),
    Usuario(nombre="Adele", email="adele@mail.com", rol="artista"),
    Usuario(nombre="Dua Lipa", email="dua@mail.com", rol="artista"),
]
session.add_all(usuarios)
session.flush()
log_insert("-- INSERT INTO usuario")
for u in usuarios:
    log_insert(f"INSERT INTO usuario (id, nombre, email, rol) VALUES ({u.id}, '{u.nombre}', '{u.email}', '{u.rol}');")

# 2. Artistas
artistas = [
    Artista(usuario_id=u.id, bio="Bio", redes={"ig": f"@{u.nombre.lower().replace(' ', '')}"})
    for u in usuarios
]
session.add_all(artistas)
session.flush()
log_insert("-- INSERT INTO artista")
for a in artistas:
    log_insert(f"INSERT INTO artista (id, usuario_id, bio, redes) VALUES ({a.id}, {a.usuario_id}, 'Bio', '{{\"ig\": \"{a.redes['ig']}\"}}');")

# 3. Productores
productores = [Productor(usuario_id=u.id, experiencia="5 años") for u in usuarios]
session.add_all(productores)
session.flush()
log_insert("-- INSERT INTO productor")
for p in productores:
    log_insert(f"INSERT INTO productor (id, usuario_id, experiencia) VALUES ({p.id}, {p.usuario_id}, '{p.experiencia}');")

# 4. Géneros
generos = [Genero(nombre=n) for n in ["Pop", "R&B", "Trap", "Rock", "Indie"]]
session.add_all(generos)
session.flush()
log_insert("-- INSERT INTO genero")
for g in generos:
    log_insert(f"INSERT INTO genero (id, nombre) VALUES ({g.id}, '{g.nombre}');")

# 5. Estudios
estudios = [Estudio(nombre=f"Estudio {i}", ubicacion=f"Ciudad {i}") for i in range(1, 6)]
session.add_all(estudios)
session.flush()
for e in estudios:
    log_insert(f"INSERT INTO estudio (id, nombre, ubicacion) VALUES ({e.id}, '{e.nombre}', '{e.ubicacion}');")

# 6. Instrumentos
instrumentos = [Instrumento(nombre=f"Instrumento {i}", tipo="Cuerda") for i in range(1, 6)]
session.add_all(instrumentos)
session.flush()
for i, inst in enumerate(instrumentos):
    log_insert(f"INSERT INTO instrumento (id, nombre, tipo) VALUES ({inst.id}, '{inst.nombre}', 'Cuerda');")

# 7. Licencias
licencias = [
    Licencia(tipo="copyright", descripcion="Uso comercial"),
    Licencia(tipo="creative_commons", descripcion="Compartir con crédito"),
    Licencia(tipo="uso_libre", descripcion="Sin restricciones"),
    Licencia(tipo="copyright", descripcion="Derechos reservados"),
    Licencia(tipo="creative_commons", descripcion="Requiere atribución"),
]
session.add_all(licencias)
session.flush()
for l in licencias:
    log_insert(f"INSERT INTO licencia (id, tipo, descripcion) VALUES ({l.id}, '{l.tipo}', '{l.descripcion}');")

# 8. Sellos
sellos = [SelloDiscografico(nombre=f"Sello {i}") for i in range(1, 6)]
session.add_all(sellos)
session.flush()
for s in sellos:
    log_insert(f"INSERT INTO sello_discografico (id, nombre) VALUES ({s.id}, '{s.nombre}');")

# 9. Álbumes (10 por artista)
albums = []
for i, artista in enumerate(artistas):
    for j in range(10):
        albums.append(Album(artista_id=artista.id, titulo=f"Álbum {i*10+j+1}", anio=2015+j))
session.add_all(albums)
session.flush()
log_insert("-- INSERT INTO album")
for a in albums:
    log_insert(f"INSERT INTO album (id, artista_id, titulo, anio) VALUES ({a.id}, {a.artista_id}, '{a.titulo}', {a.anio});")

# 10. Canciones (10 por álbum)
canciones = []
for i, album in enumerate(albums):
    for j in range(10):
        canciones.append(
            Cancion(
                album_id=album.id,
                nombre=f"Canción {i*10+j+1}",
                duracion=f"00:0{random.randint(3,5)}:{random.randint(10,59):02d}",
                clave=random.choice(["C", "G", "F", "D"]),  # Solo claves mayores
                licencia_id=random.choice(licencias).id
            )
        )
session.add_all(canciones)
session.flush()
log_insert("-- INSERT INTO cancion")
for c in canciones:
    log_insert(f"INSERT INTO cancion (id, album_id, nombre, duracion, clave, licencia_id) VALUES ({c.id}, {c.album_id}, '{c.nombre}', '{c.duracion}', '{c.clave}', {c.licencia_id});")

# 11. Playlist
playlists = [Playlist(usuario_id=u.id, nombre=f"Playlist {i+1}") for i, u in enumerate(usuarios)]
session.add_all(playlists)
session.flush()
for p in playlists:
    log_insert(f"INSERT INTO playlist (id, usuario_id, nombre) VALUES ({p.id}, {p.usuario_id}, '{p.nombre}');")

# 12. Colaboraciones
colabs = [Colaboracion(artista_id=artistas[i % len(artistas)].id, cancion_id=c.id, tipo_colaboracion="voz") for i, c in enumerate(canciones[:5])]
session.add_all(colabs)
for c in colabs:
    log_insert(f"INSERT INTO colaboracion (artista_id, cancion_id, tipo_colaboracion) VALUES ({c.artista_id}, {c.cancion_id}, '{c.tipo_colaboracion}');")

# 13. Canción-Género (asignar géneros aleatorios de los 5 existentes)
cancion_generos = [CancionGenero(cancion_id=c.id, genero_id=random.choice(generos).id) for c in canciones]
session.add_all(cancion_generos)
for cg in cancion_generos:
    log_insert(f"INSERT INTO cancion_genero (cancion_id, genero_id) VALUES ({cg.cancion_id}, {cg.genero_id});")

# 14. Playlist-Canción
playlist_cancion = [PlaylistCancion(playlist_id=playlists[i % len(playlists)].id, cancion_id=c.id) for i, c in enumerate(canciones[:5])]
session.add_all(playlist_cancion)
for pc in playlist_cancion:
    log_insert(f"INSERT INTO playlist_cancion (playlist_id, cancion_id) VALUES ({pc.playlist_id}, {pc.cancion_id});")

# 15. Grabaciones
grabaciones = [Grabacion(artista_id=a.id, estudio_id=estudios[i % len(estudios)].id, fecha=random_date()) for i, a in enumerate(artistas)]
session.add_all(grabaciones)
session.flush()
for g in grabaciones:
    log_insert(f"INSERT INTO grabacion (id, artista_id, estudio_id, fecha) VALUES ({g.id}, {g.artista_id}, {g.estudio_id}, '{g.fecha}');")

# 16. Instrumento-Grabación
session.add_all([
    InstrumentoGrabacion(grabacion_id=grabaciones[i % len(grabaciones)].id, instrumento_id=instrumentos[i % len(instrumentos)].id)
    for i in range(5)
])
for ig in session.query(InstrumentoGrabacion).all():
    log_insert(f"INSERT INTO instrumento_grabacion (grabacion_id, instrumento_id) VALUES ({ig.grabacion_id}, {ig.instrumento_id});")

# 17. Archivos multimedia
archivos = [ArchivoMultimedia(cancion_id=c.id, tipo="audio", formato="mp3", url=f"http://ejemplo.com/{i}") for i, c in enumerate(canciones[:5])]
session.add_all(archivos)
for a in archivos:
    log_insert(f"INSERT INTO archivo_multimedia (id, cancion_id, tipo, formato, url) VALUES ({a.id}, {a.cancion_id}, '{a.tipo}', '{a.formato}', '{a.url}');")

# 18. Historial de cambios
historial = [HistorialCambios(cancion_id=c.id, fecha=random_date(), estado="mezcla") for c in canciones[:5]]
session.add_all(historial)
for h in historial:
    log_insert(f"INSERT INTO historial_cambios (id, cancion_id, fecha, estado) VALUES ({h.id}, {h.cancion_id}, '{h.fecha}', '{h.estado}');")

# 19. Comentarios
comentarios = [Comentario(usuario_id=u.id, cancion_id=canciones[i % len(canciones)].id, contenido="Comentario", fecha=random_date()) for i, u in enumerate(usuarios)]
session.add_all(comentarios)
for c in comentarios:
    log_insert(f"INSERT INTO comentario (id, usuario_id, cancion_id, contenido, fecha) VALUES ({c.id}, {c.usuario_id}, {c.cancion_id}, '{c.contenido}', '{c.fecha}');")

# 20. Reseñas (200 reseñas - 40 por usuario)
resenas = []
textos_puntaje = {
    1: "Horrible",
    2: "Malo",
    3: "Normal",
    4: "Bueno",
    5: "Excelente"
}

for usuario in usuarios:
    # Seleccionar 40 álbumes aleatorios para este usuario
    albumes_mezclados = random.sample(albums, 40)
    for album in albumes_mezclados:
        puntaje = random.randint(1, 5)
        texto = textos_puntaje[puntaje]
        resenas.append(
            Resena(
                usuario_id=usuario.id,
                album_id=album.id,
                puntaje=puntaje,
                texto=texto
            )
        )

session.add_all(resenas)
log_insert("-- INSERT INTO resena")
for r in resenas:
    log_insert(f"INSERT INTO resena (id, usuario_id, album_id, puntaje, texto) VALUES ({r.id}, {r.usuario_id}, {r.album_id}, {r.puntaje}, '{r.texto}');")

# 21. Métricas
metricas = [MetricaCancion(cancion_id=c.id, reproducciones=1000, likes=100, descargas=50) for c in canciones[:5]]
session.add_all(metricas)
for m in metricas:
    log_insert(f"INSERT INTO metrica_cancion (cancion_id, reproducciones, likes) VALUES ({m.cancion_id}, {m.reproducciones}, {m.likes});")

# 22. Contratos
contratos = [
    Contrato(artista_id=artistas[i].id, productor_id=productores[i].id, fecha_inicio=date(2020, 1, 1), fecha_fin=date(2025, 1, 1))
    for i in range(5)
]
session.add_all(contratos)
for c in contratos:
    log_insert(f"INSERT INTO contrato (id, artista_id, productor_id, fecha_inicio, fecha_fin) VALUES ({c.id}, {c.artista_id}, {c.productor_id}, '{c.fecha_inicio}', '{c.fecha_fin}');")

def save_log():
    with open("inserts.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(insert_log))
    print("📄 Archivo 'inserts.sql' generado.")

# Guardar en BD y en archivo SQL
session.commit()
session.close()
save_log()
print("✅ ¡Datos insertados exitosamente!")