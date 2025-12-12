import psycopg2
from DML.config import DB_CONFIG
 
def create_procedures():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
    
    cur.execute("""
        CREATE OR REPLACE PROCEDURE pr_apply_publisher_discount(p_publisher_name TEXT, p_percentual_desconto NUMERIC)
        AS $$
        DECLARE
            var_publisher_id INT;
            var_count INT;
        BEGIN

            IF p_percentual_desconto <= 0 OR p_percentual_desconto > 90 THEN
                RAISE EXCEPTION 'Erro: O desconto deve ser entre 1%% e 90%%. Valor fornecido: %', p_percentual_desconto;
            END IF;

            SELECT id INTO var_publisher_id
            FROM publishers
            WHERE lower(publisher_name) = lower(p_publisher_name);

            IF var_publisher_id IS NULL THEN
                RAISE EXCEPTION 'Publisher "%" não encontrado.', p_publisher_name;
            END IF;

            UPDATE games g
            SET price = price - (price * (p_percentual_desconto / 100.0))
            FROM publishers_game pg
            WHERE g.appid = pg.id_game AND pg.id_publisher = var_publisher_id
            AND g.price > 0;

            GET DIAGNOSTICS var_count = ROW_COUNT;
            
            RAISE NOTICE 'Promoção aplicada! % jogos da % receberam %%% de desconto.', var_count, p_publisher_name, p_percentual_desconto;
        END;
        $$
        LANGUAGE plpgsql;
                
        CREATE OR REPLACE PROCEDURE pr_safe_link_tag(p_appid INT, p_tag_name TEXT)
        AS $$
        DECLARE
            var_tag_id INT;
            var_clean_tag TEXT;
        BEGIN
                
            var_clean_tag := lower(trim(p_tag_name));

            SELECT id INTO var_tag_id
            FROM tags
            WHERE lower(tag_name) = var_clean_tag;

            IF var_tag_id IS NULL THEN
                INSERT INTO tags (tag_name) VALUES (var_clean_tag)
                RETURNING id INTO var_tag_id;
                RAISE NOTICE 'Nova tag "%" criada no sistema.', var_clean_tag;
            END IF;

            BEGIN
                INSERT INTO tags_game (id_tag, id_game)
                VALUES (var_tag_id, p_appid);
            EXCEPTION 
                WHEN unique_violation THEN
                    RAISE NOTICE 'O jogo % já possui a tag "%". Nada a fazer.', p_appid, var_clean_tag;
            END;
        END;
        $$
        LANGUAGE plpgsql;    

        CREATE OR REPLACE PROCEDURE verify_game_integrity(p_game INT)
        AS $$
        DECLARE
            var_exists BOOL;
            var_det BOOL;
            var_cat INT;
            var_gen INT;
            var_lang INT;
            var_os INT;
            var_dev INT;
            var_pub INT;
            var_tag INT;
        BEGIN

            SELECT EXISTS(SELECT 1 FROM games WHERE appid = p_game) INTO var_exists;

            IF NOT var_exists THEN
                RAISE EXCEPTION 'O jogo % não existe na tabela games.', p_game;
            END IF;

            SELECT EXISTS(SELECT 1 FROM detalhes WHERE id_game = p_game) INTO var_det;

            IF NOT var_det THEN
                RAISE NOTICE 'AVISO: Jogo % não possui entrada na tabela detalhes.', p_game;
            ELSE
                RAISE NOTICE 'Detalhes encontrados para o jogo %.', p_game;
            END IF;

            SELECT COUNT(*) INTO var_cat FROM categories_game WHERE id_game = p_game;
            SELECT COUNT(*) INTO var_gen FROM genres_game WHERE id_game = p_game;
            SELECT COUNT(*) INTO var_lang FROM languages_game WHERE id_game = p_game;
            SELECT COUNT(*) INTO var_os FROM operation_systems_games WHERE id_game = p_game;

            RAISE NOTICE 'Categorias encontradas: %', var_cat;
            IF var_cat = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui categorias.', p_game;
            END IF;

            RAISE NOTICE 'Gêneros encontrados: %', var_gen;
            IF var_gen = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui gêneros.', p_game;
            END IF;

            RAISE NOTICE 'Idiomas encontrados: %', var_lang;
            IF var_lang = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui idiomas cadastrados.', p_game;
            END IF;

            RAISE NOTICE 'Sistemas operacionais encontrados: %', var_os;
            IF var_os = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui sistemas operacionais cadastrados.', p_game;
            END IF;

            SELECT COUNT(*) INTO var_dev FROM developers_game WHERE id_game = p_game;
            SELECT COUNT(*) INTO var_pub FROM publishers_game WHERE id_game = p_game;
            SELECT COUNT(*) INTO var_tag FROM tags_game WHERE id_game = p_game;

            RAISE NOTICE 'Developers encontrados: %', var_dev;
            IF var_dev = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui desenvolvedores vinculados.', p_game;
            END IF;

            RAISE NOTICE 'Publishers encontrados: %', var_pub;
            IF var_pub = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui publishers vinculados.', p_game;
            END IF;

            RAISE NOTICE 'Tags encontradas: %', var_tag;
            IF var_tag = 0 THEN
                RAISE NOTICE 'AVISO: Jogo % não possui tags cadastradas.', p_game;
            END IF;

            RAISE NOTICE 'Verificação completa concluída para o jogo %.', p_game;
        END;
        $$
        LANGUAGE plpgsql;      
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Procedures criadas com sucesso.")
 
 