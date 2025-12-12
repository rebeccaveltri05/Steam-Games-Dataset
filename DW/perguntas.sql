--Quais gêneros de jogos apresentam a maior receita estimada acumulada nos últimos 5 anos?

SELECT 
    j.genero_principal,
    SUM(f.receita_estimada) AS receita_total_acumulada,
    COUNT(f.sk_jogo) AS qtd_jogos_lancados
FROM dw.fato_performance_steam f
JOIN dw.dim_jogo j ON f.sk_jogo = j.sk_jogo
JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
WHERE t.ano >= (EXTRACT(YEAR FROM CURRENT_DATE) - 5)
GROUP BY j.genero_principal
ORDER BY receita_total_acumulada DESC;

-- Qual é o preço médio dos jogos lançados pelas principais Publishers e como isso afeta a sua base de jogadores estimada?
SELECT 
    p.nome_publisher,
    COUNT(f.sk_jogo) AS total_jogos,
    ROUND(AVG(f.preco_unitario), 2) AS preco_medio_jogo,
    ROUND(AVG(f.donos_estimados), 0) AS media_jogadores_por_jogo,
    SUM(f.donos_estimados) AS base_total_estimada
FROM dw.fato_performance_steam f
JOIN dw.dim_publisher p ON f.sk_publisher = p.sk_publisher
GROUP BY p.nome_publisher
HAVING COUNT(f.sk_jogo) > 5
ORDER BY base_total_estimada DESC 
LIMIT 20;

-- Existe uma tendência de queda ou aumento na quantidade de lançamentos Indie por trimestre?
SELECT 
    t.ano,
    t.trimestre,
    COUNT(f.sk_jogo) AS qtd_lancamentos_indie
FROM dw.fato_performance_steam f
JOIN dw.dim_jogo j ON f.sk_jogo = j.sk_jogo
JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
WHERE j.genero_principal ILIKE '%Indie%'
GROUP BY t.ano, t.trimestre
ORDER BY t.ano DESC, t.trimestre ASC;

/*
Lançar jogos durante períodos festivos (nov/dez) 
realmente garante uma receita média superior, ou o excesso de lançamento 
acaba diminuindo o retorno individual por jogo?
 */
SELECT 
    CASE 
        WHEN t.eh_data_festiva = TRUE THEN 'Período festivo (nov/dez)'
        ELSE 'Período comum (jan-out)'
    END AS tipo_periodo,
    
    COUNT(f.sk_jogo) AS total_lancamentos,
    
    ROUND(AVG(f.receita_estimada), 2) AS receita_media_por_jogo,
    
    ROUND(AVG(f.tempo_medio_jogo_minutos) / 60.0, 2) AS tempo_medio_horas
    
FROM dw.fato_performance_steam f
JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.eh_data_festiva
ORDER BY receita_media_por_jogo DESC;


 /*Existe alguma relação negativa entre a quantidade de lançamentos em um
mês e a receita média por jogo? Ou seja, meses com muitos lançamentos
fazem com que a receita se distribua mais*/
SELECT 
    t.ano,
    t.mes,
    COUNT(f.sk_jogo) AS total_lancamentos_no_mes,
    ROUND(AVG(f.receita_estimada), 2) AS receita_media_por_jogo
FROM dw.fato_performance_steam f
JOIN dw.dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes
HAVING COUNT(f.sk_jogo) > 10
ORDER BY total_lancamentos_no_mes DESC ;


/*A nota dos usuários (user score) tem correlação direta com a receita
estimada? Ou seja, jogos bem avaliados vendem necessariamente mais?
*/
SELECT 
    FLOOR(f.score_usuario_bruto / 10) * 10 AS faixa_de_nota,
    
    COUNT(f.sk_jogo) AS qtd_jogos,
    
    ROUND(AVG(f.receita_estimada), 2) AS receita_media,
    
    ROUND(AVG(f.donos_estimados), 0) AS media_vendas_unidades
    
FROM dw.fato_performance_steam f
WHERE f.score_usuario_bruto > 0 
GROUP BY 1
ORDER BY 1 DESC;


-- Qual é a taxa de rejeição (avaliações negativas) média para jogos com preço a partir de $49?
SELECT 
    COUNT(sk_jogo) AS qtd_jogos_analisados,
    ROUND(AVG(preco_unitario), 2) AS preco_medio,
    
    -- Como não temos as colunas separadas, usamos o inverso do score
    -- Se a nota é 80% positiva, então rejeição é 20%
    ROUND(AVG(100 - score_usuario_bruto), 2) AS taxa_rejeicao_media_percentual
    
FROM dw.fato_performance_steam
WHERE preco_unitario > 49
AND score_usuario_bruto > 0;


/* Como é a divisão dos status de avaliações entre os jogos?
   Os jogos predominam mais em qual status? E qual é a relação com a receita média?
 */
SELECT 
    j.categoria_avaliacao,
    COUNT(f.sk_jogo) AS quantidade_jogos,

    ROUND(
        (COUNT(f.sk_jogo)::NUMERIC / (SELECT COUNT(*) FROM dw.fato_performance_steam)) * 100, 2) AS porcentagem_do_total, 
        
    ROUND(AVG(f.receita_estimada), 2) AS receita_media
    
FROM dw.fato_performance_steam f
JOIN dw.dim_jogo j ON f.sk_jogo = j.sk_jogo
GROUP BY j.categoria_avaliacao
ORDER BY receita_media DESC;


/* 
Jogos que suportam múltiplos sistemas operacionais (windows + linux + mac) 
possuem um tempo médio de jogo e média de donos superior?”
*/
SELECT 
    CASE 
        WHEN plataformas_texto ILIKE '%windows%' 
             AND plataformas_texto ILIKE '%mac%' 
             AND plataformas_texto ILIKE '%linux%' 
        THEN 'Suporte Total (Win+Mac+Linux)'
        ELSE 'Suporte Parcial / Exclusivo'
    END AS categoria_plataforma,
    
    COUNT(f.sk_jogo) AS qtd_jogos,
    
    ROUND(AVG(f.tempo_medio_jogo_minutos) / 60.0, 2) AS tempo_medio_horas,
    
    ROUND(AVG(f.donos_estimados), 0) AS media_donos
    
FROM dw.fato_performance_steam f
JOIN dw.dim_jogo j ON f.sk_jogo = j.sk_jogo
GROUP BY 1
ORDER BY tempo_medio_horas DESC;






