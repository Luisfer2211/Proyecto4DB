from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Interval, Text, ForeignKey,
    Enum, Table, UniqueConstraint, CheckConstraint, JSON, MetaData
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import CreateTable
from getpass import getpass
import os
from sqlalchemy.schema import CreateTable

# Solicitar contraseña
password = getpass("🔐 Ingresa la contraseña de PostgreSQL: ")
DATABASE_NAME = "produccion_musical_db"
DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/{DATABASE_NAME}"

# Crear base si no existe
from sqlalchemy import create_engine, text
engine_temp = create_engine(f"postgresql://postgres:{password}@localhost:5432/postgres", isolation_level="AUTOCOMMIT")
with engine_temp.connect() as conn:
    result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DATABASE_NAME}'"))
    if not result.scalar():
        conn.execute(text(f"CREATE DATABASE {DATABASE_NAME}"))
        print(f"✅ Base de datos '{DATABASE_NAME}' creada.")
    else:
        print(f"ℹ️ La base de datos '{DATABASE_NAME}' ya existe.")

# Re-conectar al motor real
engine = create_engine(DATABASE_URI, echo=False)
Base = declarative_base()

# Tipos personalizados
estado_mezcla_enum = Enum('demo', 'mezcla', 'master', 'final', name='estado_mezcla', create_type=True)
clave_musical_enum = Enum('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', name='clave_musical', create_type=True)
rol_usuario_enum = Enum('artista', 'productor', 'oyente', 'crítico', name='rol_usuario', create_type=True)
licencia_tipo_enum = Enum('copyright', 'creative_commons', 'uso_libre', name='licencia_tipo', create_type=True)
formato_archivo_enum = Enum('mp3', 'wav', 'flac', 'jpeg', 'png', name='formato_archivo', create_type=True)

# Modelos
class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    rol = Column(rol_usuario_enum, nullable=False)

class Artista(Base):
    __tablename__ = 'artista'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    bio = Column(Text)
    redes = Column(JSON)

class Productor(Base):
    __tablename__ = 'productor'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    experiencia = Column(Text)

class Genero(Base):
    __tablename__ = 'genero'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)

class Estudio(Base):
    __tablename__ = 'estudio'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(Text)

class Instrumento(Base):
    __tablename__ = 'instrumento'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    tipo = Column(String(50))

class Licencia(Base):
    __tablename__ = 'licencia'
    id = Column(Integer, primary_key=True)
    tipo = Column(licencia_tipo_enum, nullable=False)
    descripcion = Column(Text)

class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    artista_id = Column(Integer, ForeignKey('artista.id'))
    titulo = Column(String(100), nullable=False)
    anio = Column(Integer)

class Cancion(Base):
    __tablename__ = 'cancion'
    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey('album.id'))
    nombre = Column(String(100), nullable=False)
    duracion = Column(Interval)
    clave = Column(clave_musical_enum)
    licencia_id = Column(Integer, ForeignKey('licencia.id'))

class Playlist(Base):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    nombre = Column(String(100))

class Colaboracion(Base):
    __tablename__ = 'colaboracion'
    artista_id = Column(Integer, ForeignKey('artista.id'), primary_key=True)
    cancion_id = Column(Integer, ForeignKey('cancion.id'), primary_key=True)
    tipo_colaboracion = Column(String(50))

class CancionGenero(Base):
    __tablename__ = 'cancion_genero'
    cancion_id = Column(Integer, ForeignKey('cancion.id'), primary_key=True)
    genero_id = Column(Integer, ForeignKey('genero.id'), primary_key=True)

class PlaylistCancion(Base):
    __tablename__ = 'playlist_cancion'
    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    cancion_id = Column(Integer, ForeignKey('cancion.id'), primary_key=True)

class Grabacion(Base):
    __tablename__ = 'grabacion'
    id = Column(Integer, primary_key=True)
    artista_id = Column(Integer, ForeignKey('artista.id'))
    estudio_id = Column(Integer, ForeignKey('estudio.id'))
    fecha = Column(Date, nullable=False)

class InstrumentoGrabacion(Base):
    __tablename__ = 'instrumento_grabacion'
    grabacion_id = Column(Integer, ForeignKey('grabacion.id'), primary_key=True)
    instrumento_id = Column(Integer, ForeignKey('instrumento.id'), primary_key=True)

class ArchivoMultimedia(Base):
    __tablename__ = 'archivo_multimedia'
    id = Column(Integer, primary_key=True)
    cancion_id = Column(Integer, ForeignKey('cancion.id'))
    tipo = Column(String(50))
    formato = Column(formato_archivo_enum)
    url = Column(Text)

class HistorialCambios(Base):
    __tablename__ = 'historial_cambios'
    id = Column(Integer, primary_key=True)
    cancion_id = Column(Integer, ForeignKey('cancion.id'))
    fecha = Column(Date, nullable=False)
    estado = Column(estado_mezcla_enum)

class Comentario(Base):
    __tablename__ = 'comentario'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    cancion_id = Column(Integer, ForeignKey('cancion.id'))
    contenido = Column(Text)
    fecha = Column(Date, nullable=False)

class Resena(Base):
    __tablename__ = 'resena'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    album_id = Column(Integer, ForeignKey('album.id'))
    puntaje = Column(Integer, CheckConstraint('puntaje BETWEEN 1 AND 5'))
    texto = Column(Text)

class MetricaCancion(Base):
    __tablename__ = 'metrica_cancion'
    cancion_id = Column(Integer, ForeignKey('cancion.id'), primary_key=True)
    reproducciones = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    descargas = Column(Integer, default=0)

class SelloDiscografico(Base):
    __tablename__ = 'sello_discografico'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)

class Contrato(Base):
    __tablename__ = 'contrato'
    id = Column(Integer, primary_key=True)
    artista_id = Column(Integer, ForeignKey('artista.id'))
    productor_id = Column(Integer, ForeignKey('productor.id'))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

# Crear todas las tablas
Base.metadata.create_all(engine)
print("✅ ¡Estructura de tablas creada exitosamente!")

print("📝 Generando archivo schema.sql...")

with open("schema.sql", "w", encoding="utf-8") as f:
    for table in Base.metadata.sorted_tables:
        create_stmt = str(CreateTable(table).compile(engine)).strip()
        f.write(create_stmt + ";\n\n")

print("✅ Archivo 'schema.sql' generado exitosamente.")
