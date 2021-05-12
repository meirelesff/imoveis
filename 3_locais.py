from config import settings
import pandas as pd
import googlemaps
import settings
import sqlite3


# Funcao para pegar dados do maps place 
def pega_locais(busca, location, radius, apikeys):

    gmaps = googlemaps.Client(key=api_keys)
    gmps = gmaps.places(busca, location = location, radius = radius, language = "pt-BR")

    parsd = pd.DataFrame.from_dict(gmps["results"])
    df = parsd[["place_id", "name", "formatted_address"]]
    df["lat"] = parsd[["geometry"]].apply(lambda x: x[0]["location"]["lat"], axis=1)
    df["lng"] = parsd[["geometry"]].apply(lambda x: x[0]["location"]["lng"], axis=1)
    df.loc[:, "tipo"] = busca
    return df

# Funcao para popular tabela de locais
def popular_tab_locais(locais, location, radius, api_keys):

    conn = sqlite3.connect("data/dados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM tab_locais")
    tab_status = cursor.fetchall()[0][0]
    
    if tab_status == 0:
        query = "INSERT OR IGNORE INTO tab_locais VALUES (?, ?, ?, ?, ?, ?)"
        for i in locais:
            print("Locais: " + i)
            local = pega_locais(i, location, radius, api_keys)
            cursor.executemany(query, x.to_records(index = False))
        conn.commit()
        conn.close()

    else:
        return None


if __name__ == "__main__":

    # Pega os locais de interesse
    api_keys = settings.api_key
    locais = settings.locais
    centroide = settings.centroide
    raio = settings.raio
    popular_tab_locais(locais, centroide, raio, api_keys)
    