from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import GoogleV3
from config import settings
import pandas as pd
import numpy as np
import logging
import sqlite3


class geo_vivareal:

    def __init__(self):
        # Conecta ao db
        self.conn = sqlite3.connect("data/dados.db")
        self.cursor = self.conn.cursor()

        # Recupera apikey do google
        self.api_key = settings.api_key

        # Pega os enderecos capturados
        query = "SELECT endereco FROM tab_imoveis WHERE endereco NOT IN (SELECT endereco FROM tab_enderecos);"
        self.cursor.execute(query)
        enderecos = [i[0] for i in self.cursor.fetchall()]
        self.enderecos = list(set(enderecos))

    # Funcao de geocode
    def geocoda(self, endereco):
        geolocator = GoogleV3(api_key=self.api_key, timeout=5)
        try:
            return geolocator.geocode(endereco)

        except GeocoderTimedOut:
            logging.info("GeocoderTimedOut: Tentando novamente...")
            sleep(2)
            return geocoda(self, endereco)

        except GeocoderServiceError as e:
            logging.info("Conexão recusada: GeocoderServiceError.")
            logging.error(e)
            return None

        except Exception as e:
            logging.info("Erro inesperado: {}".format(e))
            return None

    # Parser
    def parser(self, geocodificado, endereco):
        res = pd.DataFrame({
            "endereco" : [endereco],
            "cep" : str(geocodificado.address.split(", ")[-2]),
            "bairro" : geocodificado.address.split(", ")[1],
            "lat" : float(geocodificado.latitude),
            "lng" : float(geocodificado.longitude)
        })
        query = "INSERT OR IGNORE INTO tab_enderecos VALUES (?, ?, ?, ?, ?)"
        self.cursor.executemany(query, res.to_records(index = False))
        self.conn.commit()

    # Bulk geocode
    def bulk_geocode(self):
        if not self.enderecos:
            print("Sem novos endereços")
            return None
        
        end_unq = self.enderecos
        for i in range(len(end_unq)):
            print("Endereço: " + end_unq[i])
            res = self.geocoda(end_unq[i])
            if res == None:
                continue
            self.parser(res, end_unq[i])
        self.cursor.close()


if __name__ == "__main__":

    # Pega os enderecos
    geo_vivareal().bulk_geocode()
