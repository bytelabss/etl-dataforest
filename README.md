# ETL Data Forest

## Sobre os Dados

### Mapa de Solos IBGE

Base de dados contendo os tipos de solos no território brasileiro. A intenção é servir para classificar a área cadastrada para o plantio dos pinheiros e eucaliptos.

[Solos_5000mil.zip](https://www.ibge.gov.br/geociencias/informacoes-ambientais/pedologia/15829-solos.html?=&t=downloads)

### Bases de dados do AMBDATA

Diversas bases de dados contendo informações sobre preciptação, altidude, declive, temperatura, vegetação, entre outras coisas. A intenção é servir para classificar a área cadastrada para o plantio dos pinheiros e eucaliptos.

[DOCS](http://www.dpi.inpe.br/Ambdata/download.php)
[Download](http://www.dpi.inpe.br/amb_data/Brasil/BR_all_LLwgs84.zip)

### Malha municipal 2023 IBGE

Base de dados contendo os limites dos Municípios coletada em 2023. Serviu para a análise dos dados.

[Malha municipal -> municipio_2023 -> Brasil -> BR_Municipios_2023.zip](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html?=&t=downloads)

## Instalação e Configuração

Caso prefira usar pyenv para gerenciar as suas versões do Python, siga as instruções em [pyenv installation](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation):

Instale a versão correta do python para esta aplicação:
  ```sh
  pyenv install 3.13.2
  pyenv global 3.13.2
  ```

Em seguida, instale o `pip` e o `virtualenv`:
  ```sh
  pip install --upgrade pip virtualenv
  ```

Agora, crie e ative um ambiente virtual e em seguida instale as dependências do projeto:
  ```sh
  virtualenv .venv --prompt='dataforest'
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

Crie uma cópia do arquivo `.env.example`:
   ```sh
   cp .env.example .env
   ```

Abra o arquivo `.env` e edite os valores conforme necessário para o seu ambiente.

Certifique-se de não commitar o arquivo `.env`, pois ele pode conter informações sensíveis, como credenciais de banco de dados ou chaves de API.


## Configuração do Banco de Dados

Este projeto utiliza PostgreSQL com PostGIS para manipulação de dados geoespaciais.

Execute os seguintes comandos para criar o banco de dados e configurar o usuário:
```sh
sudo -u postgres psql
```

No prompt do PostgreSQL, execute:

```sql
-- Criar o usuário
CREATE USER dataforest WITH ENCRYPTED PASSWORD 'dataforest';

-- Criar o banco de dados e definir o usuário como proprietário
CREATE DATABASE dataforest OWNER dataforest;

-- Saia do PostgreSQL
\q
```

Agora, conecte-se ao banco de dados e ative a extensão PostGIS:

```sh
sudo -u postgres psql
```

No prompt do PostgreSQL, execute:

```sql
-- Conectar ao banco de dados
\c dataforest

-- Habilitar PostGIS
CREATE EXTENSION postgis;
```

Para verificar a instalação:

```sql
SELECT postgis_full_version();

-- Saia do PostgreSQL
\q
```


## Atualizando o banco de dados

```sh
alembic upgrade head
```


## Criando uma nova migração

Apenas crie ou altere modelos e use o seguinte comando para criar uma nova migration:
  ```sh
  alembic revision --autogenerate
  ```


## Executando a Aplicação

```sh
flask run
```

O servidor estará rodando em `http://127.0.0.1:5000/` com recarga automática ao modificar o código.


## Comandos Adicionais

Para desativar o ambiente virtual, execute:
  ```sh
  deactivate
  ```

Se novas dependências forem adicionadas, atualize o `requirements.txt`:
  ```sh
  pip freeze > requirements.txt
  ```