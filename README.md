# Steam-Games-Dataset
Repositório dedicado ao controle de versionamento do Banco de Dados "[Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset)".

# Importando Os Dados
1. Crie uma database chamada "Steam Games Dataset" **<sup>*</sup>**
2. Baixe a base de dados em .zip [aqui](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset)
3. Extraia o arquivo "games.json" para a pasta ["import_data"](/import_data)
4. Crie uma venv no local do projeto `py -m venv venv`
5. Abra um terminal e rode `pip install psycopg2-binary ijson`
6. Ajuste a senha do seu usuário no arquivo [util.py](/import_data/util.py)
7. Então rode o script com `python main.py`
> [!NOTE]
> A importação pode demorar alguns minutos.

> [!CAUTION]
> **<sup>*</sup>** O nome da database pode ser qualquer um que desejar, mas então deverá ser alterado no arquivo "util.py" e qualquer outro arquivo que venha a mencionar a database posteriormente. 
