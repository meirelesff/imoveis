from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import create_engine
from sklearn import linear_model
import pandas as pd
import numpy as np


# Carrega e filtra os dados
eng = create_engine("sqlite:///data/dados.db")
dados = pd.read_sql_table("tab_dados", eng)

# Roda um ols e extrai os residuos
cols = ["quartos", "banheiros", "metragem", "vagas", "academia", "elevador", "churrasqueira",\
    "playground", "varanda", "distancia_metro", "distancia_hospital", "distancia_cei",\
        "distancia_shopping", "distancia_mercado"]
mod = linear_model.LinearRegression()
res = mod.fit(dados[cols], dados[["preco"]])
r2_score(dados[["preco"]], res.predict(dados[cols]))
dados["residuo"] = res.predict(dados[cols]) - dados[["preco"]]

# Salva os dados numa nova tabela
dados.to_sql("tab_superset", eng, if_exists="replace", index=False)