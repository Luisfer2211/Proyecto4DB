from sqlalchemy import create_engine, text
from getpass import getpass

with open("contraseña.txt", "r", encoding="utf-8") as f:
    password = f.read().strip()
DATABASE_URI = f"postgresql://postgres:{password}@localhost:5432/produccion_musical_db"
engine = create_engine(DATABASE_URI)

funciones_sql = [
    # 1. Función para validar que comentarios no estén vacíos
    """
    CREATE OR REPLACE FUNCTION validar_contenido_comentario()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.contenido IS NULL OR LENGTH(TRIM(NEW.contenido)) = 0 THEN
            RAISE EXCEPTION '❌ El contenido del comentario no puede estar vacío.';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # 2. Función para registrar historial automáticamente
    """
    CREATE OR REPLACE FUNCTION registrar_historial_al_insertar_cancion()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO historial_cambios (cancion_id, fecha, estado)
        VALUES (NEW.id, CURRENT_DATE, 'demo');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # 3. Función para restringir cambios de estado (solo puede avanzar)
    """
    CREATE OR REPLACE FUNCTION validar_estado_historial()
    RETURNS TRIGGER AS $$
    DECLARE
        estados TEXT[] := ARRAY['demo', 'mezcla', 'master', 'final'];
        idx_old INT;
        idx_new INT;
    BEGIN
        idx_old := array_position(estados, OLD.estado);
        idx_new := array_position(estados, NEW.estado);

        IF idx_new < idx_old THEN
            RAISE EXCEPTION '❌ No se puede retroceder de estado en el historial de mezcla.';
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
]

triggers_sql = [
    # 1. Trigger para validar contenido en comentarios
    """
    DROP TRIGGER IF EXISTS trigger_validar_contenido_comentario ON comentario;
    CREATE TRIGGER trigger_validar_contenido_comentario
    BEFORE INSERT ON comentario
    FOR EACH ROW EXECUTE FUNCTION validar_contenido_comentario();
    """,

    # 2. Trigger que registra historial al insertar nueva canción
    """
    DROP TRIGGER IF EXISTS trigger_registrar_historial_cancion ON cancion;
    CREATE TRIGGER trigger_registrar_historial_cancion
    AFTER INSERT ON cancion
    FOR EACH ROW EXECUTE FUNCTION registrar_historial_al_insertar_cancion();
    """,

    # 3. Trigger que valida que los estados en historial solo avancen
    """
    DROP TRIGGER IF EXISTS trigger_validar_estado_historial ON historial_cambios;
    CREATE TRIGGER trigger_validar_estado_historial
    BEFORE UPDATE ON historial_cambios
    FOR EACH ROW EXECUTE FUNCTION validar_estado_historial();
    """
]

# Ejecutar todo
with engine.connect() as conn:
    print("🧠 Creando funciones...")
    for sql in funciones_sql:
        conn.execute(text(sql))

    print("⚙️  Creando triggers...")
    for sql in triggers_sql:
        conn.execute(text(sql))

    print("✅ ¡Funciones y triggers creados exitosamente!")

    # Guardar todo en triggers.sql
    with open("triggers.sql", "w", encoding="utf-8") as f:
        for sql in funciones_sql + triggers_sql:
            f.write(sql.strip() + ";\n\n")
    print("📝 Archivo 'triggers.sql' generado.")
