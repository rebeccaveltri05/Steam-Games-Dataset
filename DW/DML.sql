INSERT INTO dw.dim_tempo(data_completa, ano, mes, trimestre, eh_data_festiva)
SELECT DISTINCT
    release_date AS data_completa,
    EXTRACT(year from release_date) AS ano,
    EXTRACT(month from release_date) AS mes,
    EXTRACT(quarter from release_date) AS trimestre,

    CASE 
        WHEN EXTRACT(month from release_date) IN (11, 12) THEN TRUE 
        ELSE FALSE 
    END AS eh_data_festiva
FROM public.games
WHERE release_date IS NOT NULL
ON CONFLICT (data_completa) DO NOTHING;


INSERT INTO dw.dim_publisher (id_origem, nome_publisher)
SELECT 
    id, 
    publisher_name
FROM public.publishers;


INSERT INTO dw.dim_jogo (
    appid_origem, 
    nome_jogo, 
    faixa_etaria, 
    genero_principal, 
    plataformas_texto, 
    categoria_avaliacao
)
SELECT 
    g.appid,
    g.name,
    g.required_age,
    
    -- apenas o primeiro gênero
    ( SELECT gen.genre_name 
      FROM public.genres gen
      JOIN public.genres_game gg ON gg.id_genre = gen.id
      WHERE gg.id_game = g.appid
      LIMIT 1
    ) AS genero_principal,

    -- subquery para concatenar plataformas (ex: "windows, linux")
    ( SELECT STRING_AGG(os.so_name::text, ', ')
      FROM public.operation_systems os
      JOIN public.operation_systems_games osg ON osg.id_so = os.id
      WHERE osg.id_game = g.appid
    ) AS plataformas_texto,

    -- lógica para criar categoria de avaliação baseada no Score
    CASE 
        WHEN d.user_score >= 95 THEN 'Extremamente Positivo'
        WHEN d.user_score >= 80 THEN 'Muito Positivo'
        WHEN d.user_score >= 70 THEN 'Positivo'
        WHEN d.user_score >= 40 THEN 'Neutro'
        WHEN d.user_score > 0   THEN 'Negativo'
        ELSE 'Sem Avaliação'
    END AS categoria_avaliacao

FROM public.games g
LEFT JOIN public.detalhes d ON d.id_game = g.appid;


INSERT INTO dw.fato_performance_steam (
    sk_tempo, 
    sk_publisher, 
    sk_jogo, 
    preco_unitario, 
    donos_estimados, 
    receita_estimada, 
    tempo_medio_jogo_minutos, 
    pico_usuarios, 
    qtd_reviews_total, 
    score_usuario_bruto
)
SELECT 
    dt.sk_tempo,
    dp.sk_publisher,
    dj.sk_jogo,
    g.price,
    
    --cálculo da estimativa de donos (média aritmética)
    (d.owners_min + d.owners_max) / 2 AS donos_estimados,
    
    --cálculo: receita estimada (donos * preço)
    ((d.owners_min + d.owners_max) / 2) * g.price AS receita_estimada,
    
    d.average_playtime_forever,
    d.peak_ccu,
    (d.positive + d.negative) AS qtd_reviews_total,
    d.user_score

FROM public.games g
JOIN public.detalhes d ON d.id_game = g.appid
JOIN dw.dim_tempo dt ON dt.data_completa = g.release_date
JOIN dw.dim_jogo dj ON dj.appid_origem = g.appid

LEFT JOIN LATERAL (
    SELECT p.id 
    FROM public.publishers p
    JOIN public.publishers_game pg ON pg.id_publisher = p.id
    WHERE pg.id_game = g.appid
    LIMIT 1 -- Pega só o primeiro publisher para não duplicar a linha na Fato
) pub_origem ON true
LEFT JOIN dw.dim_publisher dp ON dp.id_origem = pub_origem.id;