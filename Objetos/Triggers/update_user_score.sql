CREATE OR REPLACE FUNCTION update_user_score_before()
RETURNS TRIGGER AS $$
DECLARE
    pos INTEGER := COALESCE(NEW.positive, 0);
    neg INTEGER := COALESCE(NEW.negative, 0);
    total INTEGER;
BEGIN
       IF TG_OP = 'UPDATE' THEN
        IF (OLD.positive IS NOT DISTINCT FROM NEW.positive) AND
           (OLD.negative IS NOT DISTINCT FROM NEW.negative) THEN
            RETURN NEW;
        END IF;
    END IF;

    total := pos + neg;

    IF total = 0 THEN
        NEW.user_score := NULL;
    ELSE
        
        NEW.user_score := ROUND((pos::numeric * 100) / total)::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_user_score
BEFORE INSERT OR UPDATE ON detalhes
FOR EACH ROW
EXECUTE FUNCTION update_user_score_before();
