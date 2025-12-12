-- SEM A PROCEDURE QUE CRIAMOS

CREATE OR REPLACE FUNCTION trg_add_mature_tag_improved()
RETURNS trigger AS $$
DECLARE
    mature_tag_id INT;
BEGIN

    IF NEW.appid IS NULL THEN
        RAISE NOTICE
            'trg_add_mature_tag_improved: NEW.appid é NULL. Pulando.';
        RETURN NEW;
    END IF;

    SELECT id INTO mature_tag_id
    FROM tags
    WHERE LOWER(TRIM(tag_name)) = 'mature'
    LIMIT 1;


    IF mature_tag_id IS NULL THEN
        SELECT id INTO mature_tag_id
        FROM tags
        WHERE LOWER(tag_name) LIKE '%mature%'
        ORDER BY id
        LIMIT 1;
    END IF;

    IF mature_tag_id IS NULL THEN
        RAISE NOTICE
            'trg_add_mature_tag_improved: Tag "mature" não encontrada. Pulando appid %.',
            NEW.appid;
        RETURN NEW;
    END IF;

    INSERT INTO tags_game (id_tag, id_game)
    VALUES (mature_tag_id, NEW.appid)
    ON CONFLICT (id_tag, id_game) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_games_add_mature
AFTER INSERT ON games
FOR EACH ROW
WHEN (NEW.required_age IS NOT NULL AND NEW.required_age >= 18)
EXECUTE FUNCTION trg_add_mature_tag_improved();
