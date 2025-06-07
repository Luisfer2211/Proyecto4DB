from sqlalchemy import create_engine, Column, Integer, String, Interval
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Text
from sqlalchemy import Float  # Asegúrate de tener esto importado

promedio_puntaje = Column(Float)


with open("contraseña.txt", "r", encoding="utf-8") as f:
    password = f.read().strip()
DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/produccion_musical_db"
engine = create_engine(DATABASE_URI)

Base = declarative_base()

class VistaCancionesCompletas(Base):
    __tablename__ = 'vista_canciones_completas'

    cancion_id = Column(Integer, primary_key=True)
    nombre_cancion = Column(String)
    album = Column(String)
    artista_id = Column(Integer)
    artista = Column(String)
    genero = Column(String)
    duracion = Column(Interval)
    clave = Column(ENUM('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', name='clave_musical'))

class VistaResenasAlbum(Base):
    __tablename__ = 'vista_resenas_album'

    resena_id = Column(Integer, primary_key=True)
    critico = Column(String)
    album = Column(String)
    anio = Column(Integer)
    artista_id = Column(Integer)
    artista = Column(String)
    puntaje = Column(Integer)
    texto = Column(Text)

class VistaAlbumesDetalles(Base):
    __tablename__ = "vista_albumes_detalles"
    __table_args__ = {"extend_existing": True}
    
    album_id = Column(Integer, primary_key=True)
    titulo_album = Column(String)
    anio = Column(Integer)
    artista = Column(String)
    total_canciones = Column(Integer)
    promedio_puntaje = Column(Float)

