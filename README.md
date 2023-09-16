# API de restaurante

Uma API para controle de comandas de restaurantes

### Pré-requisitos

Certifique-se de ter o seguinte instalado em sua máquina:

- Python 3.x (https://www.python.org/downloads/)
- pip (geralmente instalado com o Python)
- git (opcional, necessário apenas se você desejar clonar um repositório)

## Configurando o Ambiente Virtual

### Windows

Execute o seguinte comando para criar um ambiente virtual:

```
python -m venv venv
```

Isso criará um ambiente virtual chamado "venv" no diretório atual.

Para ativar o ambiente virtual, execute o seguinte comando:

```
venv\Scripts\activate
```

### Linux

Execute o seguinte comando para criar um ambiente virtual:

```
python3 -m venv venv
```

Isso criará um ambiente virtual chamado "venv" no diretório atual.

Para ativar o ambiente virtual, execute o seguinte comando:

```
source venv/bin/activate
```

## Instalando Dependências

Com o ambiente virtual ativado, você pode instalar as dependências do projeto. Certifique-se de estar no diretório do projeto antes de prosseguir.

Execute o seguinte comando para instalar o FastAPI e outras dependências:

```
pip install -r requirements.txt
```

## Executando o Projeto

No mesmo terminal onde o ambiente virtual está ativado, execute o seguinte comando:

```
uvicorn main:app --reload
```

O servidor FastAPI será iniciado e estará acessível em http://localhost:8000.
