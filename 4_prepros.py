from sqlalchemy import create_engine
from geopy.distance import geodesic
import pandas as pd
import numpy as np


# Arruma variaveis numericas
def ajusta_numeros(var):
    return var.str.replace(r"\D+", "").replace("", 0, regex=True).astype(float)

# Ajusta variaveis de valores
def ajusta_valores(var):
    return var.str.replace(r"\D+", "", regex=True).replace("", np.nan, regex=True).astype(float)

# Cria uma variavel para indicar tipo de imovel
def tipo_imovel(var):
    if "partamento" in var:
        return "Apartamento"
    elif "Flat" in var:
        return "Flat" 
    elif "obertura" in var:
        return "Cobertura"
    elif "Casa" in var:
        return "Casa" 
    elif "Kitnet" in var:
        return "Kitnet" 
    else:
        return "Comercial"
        

if __name__ == "__main__":

    # Carrega os dados
    eng = create_engine("sqlite:///data/dados.db")
    imoveis = pd.read_sql_table("tab_imoveis", eng).drop_duplicates()

    # Arruma variaveis
    colunas = ["metragem", "quartos", "banheiros", "vagas"]
    imoveis[colunas] = imoveis[colunas].apply(ajusta_numeros)

    imoveis[["aluguel", "condominio"]] = imoveis[["aluguel", "condominio"]].apply(ajusta_valores, axis=1)
    imoveis["tipo_imovel"] = imoveis.anuncio.apply(tipo_imovel)

    imoveis["tipo_via"] = "Outros"
    imoveis.loc[imoveis.endereco.str.contains("Rua"), "tipo_via"] = "Rua"
    imoveis.loc[imoveis.endereco.str.contains("Avenida"), "tipo_via"] = "Avenida"

    amenidades = imoveis.amenidades.str.split("\n", expand=True).stack().value_counts()[1:40]
    nomes = amenidades.index.str.lower().str.strip().str.replace("(-| )", "_", regex=True).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    for i in range(len(nomes)):
        imoveis[nomes[i]] = np.where(imoveis.amenidades.str.contains(amenidades.index[i]), 1, 0)

    imoveis.insert(0, "id", imoveis.link.str.partition("id-")[2].str.replace("/", "", regex=True))
    imoveis.insert(1, "url", imoveis.link)
    imoveis = imoveis.drop(["link", "amenidades"], axis=1)

    imoveis = imoveis.assign(preco = (imoveis.aluguel + imoveis.condominio))
    imoveis = imoveis.assign(precom2 = imoveis.preco / imoveis.metragem)
    imoveis["preco_cat"] = "Mais que 4 mil"
    imoveis.loc[imoveis.preco.between(0, 2000), "preco_cat"] = "Menos que 2 mil"
    imoveis.loc[imoveis.preco.between(2000, 3000), "preco_cat"] = "2 a 3 mil"
    imoveis.loc[imoveis.preco.between(3000, 4000), "preco_cat"] = "3 a 4 mil"

    # Join das coordenadas dos imoveis
    imoveis = pd.merge(imoveis, pd.read_sql_table("tab_enderecos", eng).drop_duplicates(),\
        how = "left", on = "endereco")

    # Remove anuncios vazios (sem geocoordenadas)
    imoveis = imoveis.loc[~np.isnan(imoveis.lat),]

    def distancia(ponto, df2, tipo):
        df2 = df2[df2.tipo == tipo]
        res = df2.apply(lambda x : geodesic(ponto, (x.lat, x.lng)).km, axis=1)
        return min(res)

    # Cria variaveis de distancia
    locais = pd.read_sql_table("tab_locais", eng)
    locais.loc[locais.tipo == "Centro de educação infantil", "tipo"] = "CEI" 
    locais = locais.drop_duplicates()
    colunas = ["distancia_" + x for x in ["metro", "hospital", "shopping", "cei", "mercado"]]
    for i in range(len(locais.tipo.unique())):
        imoveis[colunas[i]] = imoveis.apply(lambda x: distancia((x.lat, x.lng), \
            locais, locais.tipo.unique()[i]), axis=1)

    # Limpa a base (apenas apes e casas)
    imoveis = imoveis.dropna(subset = ["condominio", "aluguel", "metragem"])
    imoveis = imoveis.query("tipo_imovel in ['Apartamento', 'Casa'] & condominio < 10000 & vagas < 20 & distancia_metro < 5 & precom2 < 1000")

    # Salva os dados numa nova tabela
    imoveis.drop("", axis=1).to_sql("tab_dados", eng, if_exists="replace", index=False)