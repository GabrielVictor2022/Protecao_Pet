# Proteção Pet

Este projeto visa mapear áreas de risco para o abandono de animais na cidade de Recife, utilizando tecnologias como **Flask**, **Leaflet** e **Chart.js**. A aplicação permite visualizar um mapa com indicadores de risco e realizar o reconhecimento de imagens para identificar animais, integrando com a **Google Vision API**.

## Funcionalidades

- **Mapa de Risco**: Exibe os bairros de Recife com marcadores que indicam o risco de abandono de animais, calculado com base em denúncias e renda da área.
- **Gráfico de Denúncias**: Apresenta um gráfico de barras com o número de denúncias por bairro.
- **Reconhecimento de Imagens**: Permite o upload de imagens para identificar animais utilizando a API do Google Vision.

## Tecnologias Utilizadas

- **Flask**: Framework web para desenvolvimento do backend.
- **Google Vision API**: Integração para reconhecimento de animais em imagens.
- **Leaflet**: Biblioteca para criação de mapas interativos.
- **Chart.js**: Biblioteca para criação de gráficos interativos.

## Estrutura do Projeto

- `app.py`: Código principal da aplicação Flask, contendo as rotas e lógica de integração com a Google Vision API.
- `templates/`: Diretório contendo os arquivos HTML.
  - `index.html`: Página principal com links para as funcionalidades.
  - `map.html`: Página que exibe o mapa com os bairros e o gráfico de denúncias.
  - `recognize.html`: Página para upload e reconhecimento de imagens de animais.
- `static/`: Diretório para assets estáticos, como imagens e arquivos JavaScript.
- `vision-credentials.json`: Arquivo de credenciais para a Google Vision API (não incluído no repositório por motivos de segurança).

## Instalação e Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/protecao-pet.git
   cd protecao-pet
