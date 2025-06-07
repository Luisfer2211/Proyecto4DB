from sqlalchemy import create_engine, text

with open("contraseña.txt", "r", encoding="utf-8") as f:
    password = f.read().strip()
DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/produccion_musical_db"
engine = create_engine(DATABASE_URI)

views_sql = [
    # 1. Vista de canciones con su artista, álbum y género
    """
    CREATE OR REPLACE VIEW vista_canciones_completas AS
    SELECT
        c.id AS cancion_id,
        c.nombre AS nombre_cancion,
        a.titulo AS album,
        ar.id AS artista_id,
        u.nombre AS artista,
        g.nombre AS genero,
        c.duracion,
        c.clave
    FROM cancion c
    JOIN album a ON c.album_id = a.id
    JOIN artista ar ON a.artista_id = ar.id
    JOIN usuario u ON ar.usuario_id = u.id
    LEFT JOIN cancion_genero cg ON cg.cancion_id = c.id
    LEFT JOIN genero g ON cg.genero_id = g.id;
    """,

    # 2. Vista de reseñas con información del álbum, artista y puntaje promedio
    """
    CREATE OR REPLACE VIEW vista_resenas_album AS
    SELECT
        r.id AS resena_id,
        u.nombre AS critico,
        a.titulo AS album,
        a.anio,
        ar.id AS artista_id,
        ua.nombre AS artista,
        r.puntaje,
        r.texto
    FROM resena r
    JOIN usuario u ON r.usuario_id = u.id
    JOIN album a ON r.album_id = a.id
    JOIN artista ar ON a.artista_id = ar.id
    JOIN usuario ua ON ar.usuario_id = ua.id;
    """

    #3. Vista de albumes con su artista y 
    """
    CREATE OR REPLACE VIEW vista_albumes_detalles AS
SELECT
  a.id AS album_id,
  a.titulo AS titulo_album,
  a.anio,
  u.nombre AS artista,
  COUNT(c.id) AS total_canciones,
  ROUND(AVG(r.puntaje), 2) AS promedio_puntaje
FROM album a
JOIN artista ar ON a.artista_id = ar.id
JOIN usuario u ON ar.usuario_id = u.id
LEFT JOIN cancion c ON c.album_id = a.id
LEFT JOIN resena r ON r.album_id = a.id
GROUP BY a.id, a.titulo, a.anio, u.nombre;
    """
]

with engine.connect() as conn:
    for view in views_sql:
        conn.execute(text(view))
    conn.commit()

    # Guardar archivo
    with open("views.sql", "w", encoding="utf-8") as f:
        for v in views_sql:
            f.write(v.strip() + ";\n\n")

    print("✅ Vistas creadas y archivo 'views.sql' generado.")
