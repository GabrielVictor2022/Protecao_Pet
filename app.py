from flask import Flask, render_template, request, jsonify
import os
import json
from google.cloud import vision
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# Configurar a variável de ambiente no código (opcional se já configurado no terminal)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\gabri\OneDrive\Documents\projeto_Protecao_Pet\protecaopet-0ce908d3d876.json"

# Dados de bairros
data = [
    {"bairro": "Boa Viagem", "denuncias": 35, "renda": 7500, "lat": -8.122, "lng": -34.902},
    {"bairro": "Casa Amarela", "denuncias": 25, "renda": 1800, "lat": -8.026, "lng": -34.917},
    {"bairro": "Afogados", "denuncias": 18, "renda": 3200, "lat": -8.0774, "lng": -34.9062},
    {"bairro": "Torre", "denuncias": 12, "renda": 4500, "lat": -8.0450, "lng": -34.909},
    {"bairro": "Espinheiro", "denuncias": 8, "renda": 8000, "lat": -8.043, "lng": -34.891},
    {"bairro": "Pina", "denuncias": 15, "renda": 5000, "lat": -8.095, "lng": -34.886},
    {"bairro": "Jardim São Paulo", "denuncias": 28, "renda": 2200, "lat": -8.081, "lng": -34.943},
    {"bairro": "Ipsep", "denuncias": 10, "renda": 3000, "lat": -8.1074, "lng": -34.9232},
    {"bairro": "Tamarineira", "denuncias": 20, "renda": 3500, "lat": -8.029, "lng": -34.901},
    {"bairro": "Caxangá", "denuncias": 22, "renda": 2800, "lat": -8.0312, "lng": -34.9549},
    {"bairro": "Várzea", "denuncias": 18, "renda": 2600, "lat": -8.046, "lng": -34.963},
    {"bairro": "Ibura", "denuncias": 30, "renda": 1500, "lat": -8.1216, "lng": -34.9421},
    {"bairro": "Graças", "denuncias": 5, "renda": 7200, "lat": -8.047, "lng": -34.899},
]

# Preparação do modelo k-NN com normalização
X = np.array([[d["denuncias"], d["renda"]] for d in data])

# Normaliza os dados de denúncias e renda
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Criação do alvo (rótulos)
y = [
    "Alto" if d["denuncias"] > 30 else
    "Médio" if d["denuncias"] > 15 else
    "Baixo"
    for d in data
]

# Treina o modelo k-NN com os dados normalizados
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_normalized, y)

# Página inicial
@app.route("/")
def home():
    # Gera os dados do gráfico com classificação atualizada
    grafico_dados = [
        {
            "bairro": d["bairro"],
            "denuncias": d["denuncias"],
            "risco": knn.predict(scaler.transform([[d["denuncias"], d["renda"]]]))[0]
        }
        for d in data
    ]
    return render_template("index.html", grafico_dados=grafico_dados)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Mapa com áreas de risco
@app.route("/map")
def map_view():
    classified_data = [
        {
            **d,
            "risco": knn.predict(scaler.transform([[d["denuncias"], d["renda"]]]))[0]
        }
        for d in data
    ]

    # Gera os dados do gráfico
    grafico_dados = [
        {
            "bairro": d["bairro"],
            "denuncias": d["denuncias"],
            "risco": knn.predict(scaler.transform([[d["denuncias"], d["renda"]]]))[0]
        }
        for d in data
    ]

    return render_template("map.html", data=classified_data, grafico_dados=grafico_dados)


# Instancia o cliente Vision API uma vez, fora das funções
client = vision.ImageAnnotatorClient()

@app.route("/recognize", methods=["GET", "POST"])
def recognize_view():
    if request.method == "POST":
        if "image" not in request.files:
            return render_template("recognize.html", error="Nenhuma imagem enviada.")
        file = request.files["image"]

        if file.filename == "":
            return render_template("recognize.html", error="Nenhuma imagem selecionada.")

        # Salva a imagem localmente
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Configuração da API Vision
        with open(filepath, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        # Reconhecimento básico de rótulos
        response = client.label_detection(image=image)
        labels = response.label_annotations
        result = None

        for label in labels:
            if label.description.lower() in ["dog", "cat"]:
                result = {
                    "animal": label.description,
                    "caracteristicas": {
                        "cor": "Indefinido",
                        "tamanho": "Médio",
                        "raça": "Indefinida",
                    },
                }
                break
        else:
            result = {"animal": "Não identificado", "caracteristicas": {}}

        # Adiciona a análise de propriedades de cores
        color_response = client.image_properties(image=image)
        colors = color_response.image_properties_annotation.dominant_colors.colors
        if colors:
            dominant_color = colors[0].color
            result["caracteristicas"]["cor"] = f"rgb({int(dominant_color.red)}, {int(dominant_color.green)}, {int(dominant_color.blue)})"

        return render_template("recognize.html", result=result)

    return render_template("recognize.html")


# API para gráficos (exemplo de dados)
@app.route("/api/denuncias")
def api_denuncias():
    bairros = [{"bairro": d["bairro"], "denuncias": d["denuncias"]} for d in data]
    return jsonify(bairros)

if __name__ == "__main__":
    app.run(debug=True)
