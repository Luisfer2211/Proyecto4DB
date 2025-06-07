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
    LEFT JOIN genero g ON cg.genero_id = g.id;;

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
GROUP BY a.id, a.titulo, a.anio, u.nombre;;

