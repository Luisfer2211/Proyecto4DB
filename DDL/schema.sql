CREATE TABLE estudio (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	ubicacion TEXT, 
	PRIMARY KEY (id)
);

CREATE TABLE genero (
	id SERIAL NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE TABLE instrumento (
	id SERIAL NOT NULL, 
	nombre VARCHAR(50), 
	tipo VARCHAR(50), 
	PRIMARY KEY (id)
);

CREATE TABLE licencia (
	id SERIAL NOT NULL, 
	tipo licencia_tipo NOT NULL, 
	descripcion TEXT, 
	PRIMARY KEY (id)
);

CREATE TABLE sello_discografico (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE usuario (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	rol rol_usuario NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE artista (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	bio TEXT, 
	redes JSON, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id)
);

CREATE TABLE playlist (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	nombre VARCHAR(100), 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id)
);

CREATE TABLE productor (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	experiencia TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id)
);

CREATE TABLE album (
	id SERIAL NOT NULL, 
	artista_id INTEGER, 
	titulo VARCHAR(100) NOT NULL, 
	anio INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(artista_id) REFERENCES artista (id)
);

CREATE TABLE contrato (
	id SERIAL NOT NULL, 
	artista_id INTEGER, 
	productor_id INTEGER, 
	fecha_inicio DATE, 
	fecha_fin DATE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(artista_id) REFERENCES artista (id), 
	FOREIGN KEY(productor_id) REFERENCES productor (id)
);

CREATE TABLE grabacion (
	id SERIAL NOT NULL, 
	artista_id INTEGER, 
	estudio_id INTEGER, 
	fecha DATE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(artista_id) REFERENCES artista (id), 
	FOREIGN KEY(estudio_id) REFERENCES estudio (id)
);

CREATE TABLE cancion (
	id SERIAL NOT NULL, 
	album_id INTEGER, 
	nombre VARCHAR(100) NOT NULL, 
	duracion INTERVAL, 
	clave clave_musical, 
	licencia_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(album_id) REFERENCES album (id), 
	FOREIGN KEY(licencia_id) REFERENCES licencia (id)
);

CREATE TABLE instrumento_grabacion (
	grabacion_id INTEGER NOT NULL, 
	instrumento_id INTEGER NOT NULL, 
	PRIMARY KEY (grabacion_id, instrumento_id), 
	FOREIGN KEY(grabacion_id) REFERENCES grabacion (id), 
	FOREIGN KEY(instrumento_id) REFERENCES instrumento (id)
);

CREATE TABLE resena (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	album_id INTEGER, 
	puntaje INTEGER CHECK (puntaje BETWEEN 1 AND 5), 
	texto TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id), 
	FOREIGN KEY(album_id) REFERENCES album (id)
);

CREATE TABLE archivo_multimedia (
	id SERIAL NOT NULL, 
	cancion_id INTEGER, 
	tipo VARCHAR(50), 
	formato formato_archivo, 
	url TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

CREATE TABLE cancion_genero (
	cancion_id INTEGER NOT NULL, 
	genero_id INTEGER NOT NULL, 
	PRIMARY KEY (cancion_id, genero_id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id), 
	FOREIGN KEY(genero_id) REFERENCES genero (id)
);

CREATE TABLE colaboracion (
	artista_id INTEGER NOT NULL, 
	cancion_id INTEGER NOT NULL, 
	tipo_colaboracion VARCHAR(50), 
	PRIMARY KEY (artista_id, cancion_id), 
	FOREIGN KEY(artista_id) REFERENCES artista (id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

CREATE TABLE comentario (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	cancion_id INTEGER, 
	contenido TEXT, 
	fecha DATE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

CREATE TABLE historial_cambios (
	id SERIAL NOT NULL, 
	cancion_id INTEGER, 
	fecha DATE NOT NULL, 
	estado estado_mezcla, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

CREATE TABLE metrica_cancion (
	cancion_id INTEGER NOT NULL, 
	reproducciones INTEGER, 
	likes INTEGER, 
	descargas INTEGER, 
	PRIMARY KEY (cancion_id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

CREATE TABLE playlist_cancion (
	playlist_id INTEGER NOT NULL, 
	cancion_id INTEGER NOT NULL, 
	PRIMARY KEY (playlist_id, cancion_id), 
	FOREIGN KEY(playlist_id) REFERENCES playlist (id), 
	FOREIGN KEY(cancion_id) REFERENCES cancion (id)
);

