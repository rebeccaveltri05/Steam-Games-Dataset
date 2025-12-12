import psycopg2
from DML.config import DB_CONFIG
 
def create_dw_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS dw;")
    conn.commit()
    cur.execute("SET search_path TO dw;")
    conn.commit()
    
    cur.execute("""        
        DROP TABLE IF EXISTS dw.dim_tempo CASCADE;
        CREATE TABLE dw.dim_tempo (
            sk_tempo SERIAL PRIMARY KEY,
            data_completa DATE UNIQUE,
            ano INT,
            mes INT,
            trimestre INT,
            eh_data_festiva BOOLEAN
        );

        DROP TABLE IF EXISTS dw.dim_publisher CASCADE;
        CREATE TABLE dw.dim_publisher (
            sk_publisher SERIAL PRIMARY KEY,
            id_origem INT,       
            nome_publisher VARCHAR(255)
        );

        DROP TABLE IF EXISTS dw.dim_jogo CASCADE;
        CREATE TABLE dw.dim_jogo (
            sk_jogo SERIAL PRIMARY KEY,
            appid_origem INT UNIQUE,
            nome_jogo VARCHAR(255),
            faixa_etaria INT,
            
            genero_principal VARCHAR(50),      
            plataformas_texto VARCHAR(50),    
            categoria_avaliacao VARCHAR(50)  
        );


        DROP TABLE IF EXISTS dw.fato_performance_steam CASCADE;
        CREATE TABLE dw.fato_performance_steam (
            id_fato SERIAL PRIMARY KEY,
            
            sk_tempo INT REFERENCES dw.dim_tempo(sk_tempo),
            sk_publisher INT REFERENCES dw.dim_publisher(sk_publisher),
            sk_jogo INT REFERENCES dw.dim_jogo(sk_jogo),
            
            -- Métricas Financeiras
            preco_unitario NUMERIC(10,2),
            donos_estimados INT,             
            receita_estimada NUMERIC(15,2),    
            
            -- Métricas de Engajamento e Feedback
            tempo_medio_jogo_minutos INT,
            pico_usuarios INT,
            qtd_reviews_total INT,
            score_usuario_bruto INT  
        );       
        """
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Tabelas DW criadas com sucesso.")
 
 