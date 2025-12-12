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