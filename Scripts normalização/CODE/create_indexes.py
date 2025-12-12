import psycopg2
from DML.config import DB_CONFIG
 
def create_indexes():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO public;")
    conn.commit()

    cur.execute("""
        CREATE INDEX idx_games_name_lower ON games (lower(name));
        CREATE INDEX idx_games_price ON games (price);
        CREATE INDEX idx_detalhes_metacritic ON detalhes (metacritic_score DESC);
        CREATE INDEX idx_detalhes_user_score ON detalhes (user_score DESC);
        CREATE INDEX idx_reviews_id_game ON reviews_game (id_game);
        CREATE INDEX idx_screenshots_appid ON screenshots (appid);
        CREATE INDEX idx_movies_appid ON movies (appid);
        CREATE INDEX idx_tags_game_id_game ON tags_game (id_game);
        CREATE INDEX idx_genres_game_id_game ON genres_game (id_game);
        CREATE INDEX idx_categories_game_id_game ON categories_game (id_game);
        CREATE INDEX idx_developers_game_id_game ON developers_game (id_game);
        CREATE INDEX idx_publishers_game_id_game ON publishers_game (id_game);
        CREATE INDEX idx_languages_game_id_game ON languages_game (id_game);
        CREATE INDEX idx_audio_languages_game_id_game ON audio_languages_game (id_game);
        CREATE INDEX idx_operation_systems_games_id_game ON operation_systems_games (id_game);
        CREATE INDEX idx_developers_name_lower ON developers (lower(developer_name));
        CREATE INDEX idx_publishers_name_lower ON publishers (lower(publisher_name));
        CREATE INDEX idx_categories_name_lower ON categories (lower(category_name));
        CREATE INDEX idx_genres_name_lower ON genres (lower(genre_name));
        CREATE INDEX idx_tags_name_lower ON tags (lower(tag_name));
        CREATE INDEX idx_author_name_lower ON author (lower(author_name));
        CREATE INDEX idx_language_name_lower ON languages (lower(language_name));
        CREATE INDEX idx_audio_language_name_lower ON audio_languages (lower(audio_language_name));
        """
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Indíces criados com sucesso.")
 
 