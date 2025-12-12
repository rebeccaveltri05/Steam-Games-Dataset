CREATE OR REPLACE FUNCTION fn_limit_tags_per_game()
RETURNS TRIGGER AS $$
DECLARE
    qtd_tags_atuais INT;
    LIMITE_TAGS CONSTANT INT := 20;
BEGIN
    SELECT COUNT(*) INTO qtd_tags_atuais
    FROM tags_game
    WHERE id_game = NEW.id_game;

    
    IF qtd_tags_atuais >= LIMITE_TAGS THEN
        RAISE EXCEPTION 'Limite atingido: o jogo % já possui o máximo de % tags permitidas.', NEW.id_game, LIMITE_TAGS;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_check_tag_limit
BEFORE INSERT ON tags_game
FOR EACH ROW
EXECUTE FUNCTION fn_limit_tags_per_game();
