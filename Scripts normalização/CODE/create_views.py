import psycopg2
from DML.config import DB_CONFIG
 
def create_views():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()
    
    cur.execute("""
        CREATE OR REPLACE VIEW view_metacritic_top3_per_genre AS
        SELECT *
        FROM (
            SELECT
                g.appid,
                g.name,
                ge.genre_name AS genre,
                d.metacritic_score,
                d.metacritic_url,
                ROW_NUMBER() OVER (
                    PARTITION BY ge.genre_name
                    ORDER BY d.metacritic_score DESC NULLS LAST
                ) AS metacritic_rank
            FROM games g
            JOIN detalhes d
                ON d.id_game = g.appid
            JOIN genres_game gg
                ON gg.id_game = g.appid
            JOIN genres ge
                ON ge.id = gg.id_genre
            WHERE d.metacritic_score IS NOT NULL
        ) AS ranked
        WHERE metacritic_rank <= 3
        ORDER BY genre, metacritic_rank;


        CREATE OR REPLACE VIEW vw_games_languages_suport AS
        SELECT 
            g.appid,
            g.name,

            COUNT(DISTINCT lg.id_language) AS total_languages,

            STRING_AGG(DISTINCT l.language_name, ', ') AS interface_languages,
            CASE 
                WHEN COUNT(DISTINCT lg.id_language) >= 10 THEN 'Excellent support'
                WHEN COUNT(DISTINCT lg.id_language) >= 5 THEN 'Good support'
                ELSE 'Limited support'
            END AS support_rating

        FROM games g
        LEFT JOIN languages_game lg
            ON g.appid = lg.id_game
        LEFT JOIN languages l 
            ON l.id = lg.id_language

        GROUP BY g.appid, g.name
        ORDER BY total_languages DESC;


        CREATE OR REPLACE VIEW vw_global_ranking AS
        SELECT
            g.appid,
            g.name,
            d.metacritic_score,
            d.recommendations,
            d.owners_min,
            d.owners_max,
            d.average_playtime_forever,
            
            CASE
                WHEN (d.positive + d.negative) > 0 
                THEN d.positive::numeric / (d.positive + d.negative)
                ELSE NULL
            END AS positive_ratio,

            (

                COALESCE(d.score_rank, 0) * 3 +
                COALESCE(d.metacritic_score, 0) * 2 +
                COALESCE(d.user_score, 0) * 2 +
                COALESCE(d.recommendations, 0) * 0.5 +
                COALESCE(d.average_playtime_forever, 0) / 20 +
                COALESCE(d.owners_max, 0) / 2000 +
                COALESCE(d.positive - d.negative, 0)
            ) AS global_score

        FROM games g
        JOIN detalhes d ON d.id_game = g.appid
        ORDER BY global_score DESC
        LIMIT 100;

        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Views criadas com sucesso.")
 
 