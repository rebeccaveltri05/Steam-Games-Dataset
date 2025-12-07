import psycopg2
import ijson
from DML.config import DB_CONFIG, PATH_ROOT
from DML.util import *

JSON_PATH = PATH_ROOT / "games.json"

def treat_str(value, can_be_null=True):
    """
    Se can_be_null=True: Retorna None se a string for vazia (vira NULL no banco).
    Se can_be_null=False: Retorna string vazia ou string tratada (evita NULL constraint violation).
    """
    if value is None:
        return None if can_be_null else ""
    
    s_value = str(value).strip()
    
    if s_value == "":
        return None if can_be_null else ""
    
    return s_value

def safe_int_nullable(value):
    """Retorna None se falhar (para campos como score_rank que podem ser NULL)"""
    if not value or value == "":
        return None
    try:
        return int(float(value))
    except:
        return None
def insert_enums(cur):
    os_lista = ['windows', 'mac', 'linux']

    for os_name in os_lista:
        cur.execute(
            """
            INSERT INTO operation_systems (so_name)
            VALUES (%s)
            ON CONFLICT (so_name) DO NOTHING
            """,
            (os_name,)
        )
# =====================================================================
# INSERT PRINCIPAL (tabela games) 
# =====================================================================
def insert_game(cur, appid, game):
    
    # Tratamentos Prévios
    # release_date: Se falhar a conversão, retornamos None
    data_lancamento = string_to_postgres_date(game.get("release_date", ""))
    
    own_min, own_max = parse_owners(game.get("estimated_owners"))

    # Montagem do Dicionário com a Lógica de NULL
    clean_data = {
        # === TABELA GAMES (NOT NULL estritos) ===
        "appid": appid,
        "name": treat_str(game.get("name"), can_be_null=False), # Nunca será NULL
        "release_date": data_lancamento, 
        "required_age": safe_int(game.get("required_age"), default=0),
        "price": safe_float(game.get("price"), default=0.0),
        
        # about_the_game:se vier vazio, mandamos string vazia ou "No description"
        "about_the_game": treat_str(game.get("about_the_game"), can_be_null=False) or "No description available",
        
        "header_image": treat_str(game.get("header_image"), can_be_null=False),
        
        # website: Pode ser NULL
        "website": treat_str(game.get("website"), can_be_null=True), 

        # === TABELA DETALHES (Maioria Nullable) ===
        "id_game": appid,
        "owners_min": own_min,
        "owners_max": own_max,
        "peak_ccu": safe_int(game.get("peak_ccu"), default=0),
        "dlc_count": safe_int(game.get("dlc_count"), default=0),
        
        # Tempos de jogo: 0 faz mais sentido que NULL se não tiver dados
        "average_playtime_forever": safe_int(game.get("average_playtime_forever"), default=0),
        "average_playtime_2weeks": safe_int(game.get("average_playtime_2weeks"), default=0),
        "median_playtime_forever": safe_int(game.get("median_playtime_forever"), default=0),
        "median_playtime_2weeks": safe_int(game.get("median_playtime_2weeks"), default=0),
        
        # Campos de Texto Opcionais (Viram NULL se vazios)
        "notes": treat_str(game.get("notes"), can_be_null=True),
        "support_url": treat_str(game.get("support_url"), can_be_null=True),
        "support_email": treat_str(game.get("support_email"), can_be_null=True),
        "metacritic_url": treat_str(game.get("metacritic_url"), can_be_null=True),
        
        # Scores e Ranks (Devem ser NULL se não existirem)
        # Use safe_int_nullable aqui, pois 0 mudaria a média estatística
        "metacritic_score": safe_int_nullable(game.get("metacritic_score")),
        "score_rank": safe_int_nullable(game.get("score_rank")),
        "user_score": safe_int_nullable(game.get("user_score")),
        
        # Contadores (0 é ok)
        "recommendations": safe_int(game.get("recommendations"), default=0),
        "achievements": safe_int(game.get("achievements"), default=0),
        "positive": safe_int(game.get("positive"), default=0),
        "negative": safe_int(game.get("negative"), default=0),
    }

    # Definição das colunas
    cols_games = ["appid", "name", "release_date", "required_age", "price", 
                  "about_the_game", "header_image", "website"]
    
    cols_details = ["id_game", "owners_min", "owners_max", "peak_ccu", "dlc_count",
                    "average_playtime_forever", "average_playtime_2weeks", 
                    "median_playtime_forever", "median_playtime_2weeks", "notes", 
                    "recommendations", "achievements", "support_url", "support_email", 
                    "metacritic_score", "metacritic_url", "positive", "negative", 
                    "user_score", "score_rank"]

    # Extraindo valores na ordem correta
    vals_games = [clean_data[c] for c in cols_games]
    vals_details = [clean_data[c] for c in cols_details]

    # SQL Insert
    sql_games = f"""
        INSERT INTO games ({",".join(cols_games)})
        VALUES ({",".join(["%s"] * len(vals_games))})
        ON CONFLICT (appid) DO NOTHING;
    """
    
    sql_details = f"""
        INSERT INTO detalhes ({",".join(cols_details)})
        VALUES ({",".join(["%s"] * len(vals_details))})
        ON CONFLICT (id_game) DO NOTHING;
    """

    cur.execute(sql_games, vals_games)
    cur.execute(sql_details, vals_details)