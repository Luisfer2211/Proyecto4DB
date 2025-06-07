CREATE OR REPLACE FUNCTION validar_contenido_comentario()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.contenido IS NULL OR LENGTH(TRIM(NEW.contenido)) = 0 THEN
            RAISE EXCEPTION '❌ El contenido del comentario no puede estar vacío.';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;;

CREATE OR REPLACE FUNCTION registrar_historial_al_insertar_cancion()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO historial_cambios (cancion_id, fecha, estado)
        VALUES (NEW.id, CURRENT_DATE, 'demo');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;;

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
    $$ LANGUAGE plpgsql;;

DROP TRIGGER IF EXISTS trigger_validar_contenido_comentario ON comentario;
    CREATE TRIGGER trigger_validar_contenido_comentario
    BEFORE INSERT ON comentario
    FOR EACH ROW EXECUTE FUNCTION validar_contenido_comentario();;

DROP TRIGGER IF EXISTS trigger_registrar_historial_cancion ON cancion;
    CREATE TRIGGER trigger_registrar_historial_cancion
    AFTER INSERT ON cancion
    FOR EACH ROW EXECUTE FUNCTION registrar_historial_al_insertar_cancion();;

DROP TRIGGER IF EXISTS trigger_validar_estado_historial ON historial_cambios;
    CREATE TRIGGER trigger_validar_estado_historial
    BEFORE UPDATE ON historial_cambios
    FOR EACH ROW EXECUTE FUNCTION validar_estado_historial();;

