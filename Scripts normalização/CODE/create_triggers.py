import psycopg2
from DML.config import DB_CONFIG
 
def create_triggers():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
    
    cur.execute("""
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
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Triggers criadas com sucesso.")
 
 