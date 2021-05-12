from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from config import settings
from random import randint
from time import sleep
import pandas as pd
import sqlite3


class vivareal:

    def __init__(self, url):
        
        # Inicia o driver e acessa a url
        self.url = url
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.get(self.url)

        # Conecta ao db
        self.conn = sqlite3.connect("data/dados.db")
        self.cursor = self.conn.cursor()

    # Metodo para passar para a prox pagina
    def proxima_pagina(self):
        try:
            passada = self.driver.current_url
            elem = self.driver.find_element_by_xpath('//*[@title="Próxima página"]')
            self.driver.execute_script("arguments[0].click();", elem)
            sleep(randint(10, 30))
            if passada == self.driver.current_url:
                return False
        except:
            return False
        return True 
     
    # Metodo para extrair span
    def pega_innerhtml(self, seletor):
        elem = self.driver.find_elements_by_css_selector(".js-card-title .property-card__content")
        x = [i.find_elements_by_css_selector(seletor) for i in elem]
        res = []
        for i in range(len(x)):
            try:
                res.append(x[i][0].get_attribute("innerHTML"))
            except:
                res.append("")
        return res

    # Metodo para extrair links de anuncios
    def pega_link(self, seletor):
        elem = self.driver.find_elements_by_css_selector(seletor)
        return [i.get_attribute("href") for i in elem]

    # Metodo para extrair texto
    def pega_texto(self, seletor):
        elem = self.driver.find_elements_by_css_selector(".js-card-title .property-card__content")
        x = [i.find_elements_by_css_selector(seletor) for i in elem]
        res = []
        for i in range(len(x)):
            try:
                res.append(x[i][0].text)
            except:
                res.append("")
        return res

    # Metodo para parsear a pagina
    def extrai_df(self):
        df = pd.DataFrame({
            "anuncio" : self.pega_innerhtml(".js-card-title .js-card-title"),
            "endereco" : self.pega_innerhtml(".js-see-on-map .property-card__address"),
            "metragem" : self.pega_innerhtml(".js-card-title .js-property-card-detail-area"),
            "quartos" : self.pega_innerhtml(".js-card-title .js-property-detail-rooms .js-property-card-value"),
            "banheiros" : self.pega_innerhtml(".js-card-title .js-property-detail-bathroom .js-property-card-value"),
            "vagas" : self.pega_innerhtml(".js-card-title .js-property-detail-garages .js-property-card-value"),
            "aluguel" : self.pega_innerhtml(".js-card-title p:nth-child(1)"),
            "amenidades" : self.pega_texto(".property-card__amenities"),
            "condominio" : self.pega_texto(".js-condo-price"),
            "link" : self.pega_link(".property-card__content-link")
            })
        df["data_captura"] = pd.to_datetime("today").strftime('%Y-%m-%d')
        return df 
    
    # Scraper
    def scraper(self):
        pag = True
        query = "INSERT OR IGNORE INTO tab_imoveis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        while pag:
            print("Página: " + self.driver.current_url)
            self.cursor.executemany(query, self.extrai_df().to_records(index = False))
            self.conn.commit()
            pag = self.proxima_pagina()
        self.cursor.close()


if __name__ == "__main__":

    # Raspa os dados
    vivareal(settings.url).scraper()
