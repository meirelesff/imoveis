# Imóveis baratos

A ideia desse projeto é *buscar imóveis para locação em uma dado lugar que estejam com preços abaixo da média do mercado.*

Como isso é feito? Resumidamente, a *pipeline* consiste em extrair e geocodificar dados de milhares de imóveis disponíveis para locação no website do [Vivareal](https://www.vivareal.com.br/) usando Selenium e a API do Google Maps; armazenar e pré-processar esses dados em um banco local com Sqlite; estimar um modelo linear simples com esses dados; e, finalmente, usar os resíduos do modelo para descobrir quais estão abaixo do preço médio de mercado dadas algumas de suas características observáveis -- metragem, número de quartos, itens do condomínio, distância em kilômetros em relação ao metrô ou hospital mais próximos, entre outros.

O resultado é uma tabela na qual cada entrada é um anúncio e, as colunas, indicam *features* como características do imóvel, distância em relação a locais de interesse e, mais importante, um *score* indicando se o imóvel está ou não abaixo do preço predito para imóveis com características similares na mesma região.

## Pré-requisitos

Para rodar o código, o ideal é ter uma instalação do [Python 3.8](https://www.python.org/downloads/) e cadastro no Google Cloud para poder usar a [API de geocodificação do Google Maps(https://developers.google.com/maps/documentation/geocoding/overview)].


## Configuração

### Dependências

Antes de rodar a *pipeline*, crie um ambiente virtual para instalar dependências com:

``` Bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Isso feito, é preciso salvar a [API key](https://developers.google.com/maps/documentation/javascript/get-api-key) do Google Maps em um arquivo chamado `.secrets.toml`. É possível fazer isso com:

``` Bash
echo 'api_key = "sua_api_key"' > .secrets.toml
```

### Parâmetros

Para extrair dados de imóveis, é necessário passar a URL de uma página de imóveis do Vivareal para o arquivo `settings.toml`. Por exemplo, essa é a URL de imóveis na Vila Mariana, em São Paulo:

```
https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-sul/vila-mariana/
```

Note que é possível pegar dados de imóveis de toda a zona sul da capital paulista com um simples mudança:

```
https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-sul
```

Ou imóveis de uma cidade toda:

```
https://www.vivareal.com.br/aluguel/rj/rio-de-janeiro/
```

Ainda no arquivo `settings.toml` é possível configurar uma lista de locais de interesse -- locais que serão usados para situar a localização de cada imóvel raspado --; o ponto central a partir do qual se deve buscar esses locais de referência; e o raio, em kilômetros, da busca.

## Uso

Tudo configurado, para rodar a *pipeline* com:

``` Bash
make run
```

O terminal deverá reportar detalhes sobre o andamento da raspagem e, passado algum tempo, é possível explorar os dados resultados, que ficarão salvos no banco em `data/dados.db`, tab `tab_superset` (idealmente, o melhor é explorar esses dados usando [Apache Superset](https://superset.apache.org/), particularmente com a lib [Deck.gl](https://deck.gl/) para plotar os imóveis; no Makefile do projeto, há um target vazio que pode ser usado para iniciar o Superset com `make superset`).