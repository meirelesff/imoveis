import sqlite3
import os

if not os.path.exists("data"):
        os.makedirs("data")

conn = sqlite3.connect("data/dados.db")
cursor = conn.cursor()

# Cria tabela de imoveis
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS tab_imoveis (
        anuncio TEXT,
        endereco TEXT,
        metragem TEXT,
        quartos TEXT,
        banheiros TEXT,
        vagas TEXT,
        aluguel TEXT,
        amenidades TEXT,
        condominio TEXT,
        link TEXT,
        data_captura DATE
);
""")

# Cria tabela de enderecos
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS tab_enderecos (
        endereco TEXT, 
        cep TEXT, 
        bairro TEXT,
        lat FLOAT,
        lng FLOAT
)
""")

# Cria tabela de locais
cursor.execute(
"""
CREATE TABLE IF NOT EXISTS tab_locais (
        place_id TEXT, 
        name TEXT, 
        formatted_address TEXT,
        lat FLOAT,
        lng FLOAT,
        tipo TEXT
)
""")

cursor.close()

        
