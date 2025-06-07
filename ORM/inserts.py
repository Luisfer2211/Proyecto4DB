from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from getpass import getpass
import random

from models import (
    Base, Usuario, Artista, Productor, Genero, Estudio, Instrumento, Licencia, Album,
    Cancion, Playlist, Colaboracion, CancionGenero, PlaylistCancion, Grabacion,
    InstrumentoGrabacion, ArchivoMultimedia, HistorialCambios, Comentario, Resena,
    MetricaCancion, SelloDiscografico, Contrato
)

# 🔐 Solicitar la contraseña una sola vez
password = getpass("🔐 Ingresa la contraseña de PostgreSQL: ")
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

def save_log():
    with open("inserts.sql", "w", encoding="utf-8") as f:
        f.write("\n".join(insert_log))
    print("📄 Archivo 'inserts.sql' generado.")

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

# 6. Instrumentos
instrumentos = [Instrumento(nombre=f"Instrumento {i}", tipo="Cuerda") for i in range(1, 6)]
session.add_all(instrumentos)
session.flush()

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

# 8. Sellos
sellos = [SelloDiscografico(nombre=f"Sello {i}") for i in range(1, 6)]
session.add_all(sellos)
session.flush()

# 9. Álbumes
albums = [Album(artista_id=artistas[i].id, titulo=f"Álbum {i+1}", anio=2020+i) for i in range(5)]
session.add_all(albums)
session.flush()

# 10. Canciones
canciones = [
    Cancion(album_id=albums[i].id, nombre=f"Canción {i+1}", duracion="00:03:30", clave="C", licencia_id=licencias[i].id)
    for i in range(5)
]
session.add_all(canciones)
session.flush()

# 11. Playlist
playlists = [Playlist(usuario_id=u.id, nombre=f"Playlist {i+1}") for i, u in enumerate(usuarios)]
session.add_all(playlists)
session.flush()

# 12. Colaboraciones
colabs = [Colaboracion(artista_id=artistas[i].id, cancion_id=canciones[i].id, tipo_colaboracion="voz") for i in range(5)]
session.add_all(colabs)

# 13. Canción-Género
cancion_generos = [CancionGenero(cancion_id=c.id, genero_id=generos[i].id) for i, c in enumerate(canciones)]
session.add_all(cancion_generos)

# 14. Playlist-Canción
playlist_cancion = [PlaylistCancion(playlist_id=playlists[i].id, cancion_id=canciones[i].id) for i in range(5)]
session.add_all(playlist_cancion)

# 15. Grabaciones
grabaciones = [Grabacion(artista_id=a.id, estudio_id=estudios[i].id, fecha=random_date()) for i, a in enumerate(artistas)]
session.add_all(grabaciones)
session.flush()

# 16. Instrumento-Grabación
session.add_all([
    InstrumentoGrabacion(grabacion_id=grabaciones[i].id, instrumento_id=instrumentos[i].id)
    for i in range(5)
])

# 17. Archivos multimedia
archivos = [ArchivoMultimedia(cancion_id=c.id, tipo="audio", formato="mp3", url=f"http://ejemplo.com/{i}") for i, c in enumerate(canciones)]
session.add_all(archivos)

# 18. Historial de cambios
historial = [HistorialCambios(cancion_id=c.id, fecha=random_date(), estado="mezcla") for c in canciones]
session.add_all(historial)

# 19. Comentarios
comentarios = [Comentario(usuario_id=u.id, cancion_id=canciones[i].id, contenido="Comentario", fecha=random_date()) for i, u in enumerate(usuarios)]
session.add_all(comentarios)

# 20. Reseñas
resenas = [Resena(usuario_id=u.id, album_id=albums[i].id, puntaje=5, texto="Excelente") for i, u in enumerate(usuarios)]
session.add_all(resenas)

# 21. Métricas
metricas = [MetricaCancion(cancion_id=c.id, reproducciones=1000, likes=100, descargas=50) for c in canciones]
session.add_all(metricas)

# 22. Contratos
contratos = [
    Contrato(artista_id=artistas[i].id, productor_id=productores[i].id, fecha_inicio=date(2020, 1, 1), fecha_fin=date(2025, 1, 1))
    for i in range(5)
]
session.add_all(contratos)

# Guardar en BD y en archivo SQL
session.commit()
session.close()
save_log()
print("✅ ¡Datos insertados exitosamente!")
