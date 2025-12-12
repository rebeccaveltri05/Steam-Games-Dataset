CREATE OR REPLACE FUNCTION trg_add_mature_tag_improved()
RETURNS trigger AS $$
BEGIN
 
    IF NEW.required_age >= 18 THEN
        CALL pr_safe_link_tag(NEW.appid, 'mature'); --PROCEDURE QUE CRIAMOS
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_games_add_mature
AFTER INSERT ON games
FOR EACH ROW
WHEN (NEW.required_age IS NOT NULL AND NEW.required_age >= 18)
EXECUTE FUNCTION trg_add_mature_tag_improved();