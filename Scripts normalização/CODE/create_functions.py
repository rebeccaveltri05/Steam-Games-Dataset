import psycopg2
from DML.config import DB_CONFIG
 
def create_functions():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
	
    cur.execute("""
        CREATE OR REPLACE FUNCTION fn_similarity(gameA INT, gameB INT)
		RETURNS NUMERIC AS $$
		DECLARE
			shared_tags INT := 0;
			shared_genres INT := 0;
			shared_categories INT := 0;
			total_tags INT := 0;
			total_genres INT := 0;
			total_categories INT := 0;
			score NUMERIC := 0;
		BEGIN
			SELECT COUNT(*) INTO shared_tags
			FROM tags_game tg1
			JOIN tags_game tg2 ON tg1.id_tag = tg2.id_tag
			WHERE tg1.id_game = gameA AND tg2.id_game = gameB;

			SELECT COUNT(*) INTO total_tags
			FROM (
				SELECT id_tag FROM tags_game WHERE id_game = gameA
				UNION
				SELECT id_tag FROM tags_game WHERE id_game = gameB
			) AS t(id_tag);

			SELECT COUNT(*) INTO shared_genres
			FROM genres_game gg1
			JOIN genres_game gg2 ON gg1.id_genre = gg2.id_genre
			WHERE gg1.id_game = gameA AND gg2.id_game = gameB;

			SELECT COUNT(*) INTO total_genres
			FROM (
				SELECT id_genre FROM genres_game WHERE id_game = gameA
				UNION
				SELECT id_genre FROM genres_game WHERE id_game = gameB
			) AS g(id_genre);

			SELECT COUNT(*) INTO shared_categories
			FROM categories_game cg1
			JOIN categories_game cg2 ON cg1.id_category = cg2.id_category
			WHERE cg1.id_game = gameA AND cg2.id_game = gameB;

			SELECT COUNT(*) INTO total_categories
			FROM (
				SELECT id_category FROM categories_game WHERE id_game = gameA
				UNION
				SELECT id_category FROM categories_game WHERE id_game = gameB
			) AS c(id_category);
			score :=
				  0.5 * CASE WHEN total_tags = 0 THEN 0 ELSE shared_tags::NUMERIC / total_tags END
				+ 0.3 * CASE WHEN total_genres = 0 THEN 0 ELSE shared_genres::NUMERIC / total_genres END
				+ 0.2 * CASE WHEN total_categories = 0 THEN 0 ELSE shared_categories::NUMERIC / total_categories END;

			RETURN score;
		END;
		$$ LANGUAGE plpgsql;
		
		CREATE OR REPLACE FUNCTION fn_platform_stats(p_platform os_enum)
		RETURNS TABLE (
			total_games INT,
			avg_price NUMERIC,
			total_reviews INT,
			user_score NUMERIC,
			free_games INT,
			paid_games INT
		) AS $$
		BEGIN
			RETURN QUERY
			SELECT 
				COUNT(*)::INT AS total_games,

				ROUND(AVG(g.price), 2) AS avg_price,

				SUM(d.positive + d.negative)::INT AS total_reviews,

				CASE 
					WHEN SUM(d.positive + d.negative) = 0 THEN 0
					ELSE ROUND((SUM(d.positive)::NUMERIC / SUM(d.positive + d.negative)) * 100, 2)
				END AS user_score,

				SUM(CASE WHEN g.price = 0 THEN 1 ELSE 0 END)::INT AS free_games,

				SUM(CASE WHEN g.price > 0 THEN 1 ELSE 0 END)::INT AS paid_games

			FROM operation_systems_games osg
			JOIN operation_systems os ON osg.id_so = os.id
			JOIN games g ON g.appid = osg.id_game
			LEFT JOIN detalhes d ON d.id_game = g.appid
			WHERE os.so_name = p_platform;
		END;
		$$ LANGUAGE plpgsql;
        
        CREATE OR REPLACE FUNCTION fn_filter_games_by_price(
            p_min_price NUMERIC,
            p_max_price NUMERIC,
            p_min_reviews INT,
            p_order_by TEXT
        )
        RETURNS TABLE(
            appid INT,
            name TEXT,
            price NUMERIC,
            total_reviews INT
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                g.appid,
                g.name,
                g.price,
                (d.positive + d.negative) AS total_reviews
            FROM games g
            LEFT JOIN detalhes d ON d.id_game = g.appid
            WHERE g.price >= p_min_price
              AND g.price <= p_max_price
              AND (d.positive + d.negative) >= p_min_reviews
            ORDER BY
                CASE WHEN p_order_by = 'price' THEN g.price END ASC,
                CASE WHEN p_order_by = 'reviews' THEN (d.positive + d.negative) END DESC;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Funções criadas com sucesso.")
 
 