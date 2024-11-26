from flask import Flask, render_template, request, jsonify
import os
import json
from google.cloud import vision
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)

# Configuração para Google Vision API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "protecaopet-c2d6fde921be.json"

# Dados fictícios para bairros de Recife
data = [
    {"bairro": "Boa Viagem", "denuncias": 15, "renda": 5000, "lat": -8.120, "lng": -34.915},
    {"bairro": "Casa Amarela", "denuncias": 30, "renda": 2000, "lat": -8.038, "lng": -34.908},
    {"bairro": "Afogados", "denuncias": 20, "renda": 3000, "lat": -8.078, "lng": -34.920},
    {"bairro": "Torre", "denuncias": 10, "renda": 4000, "lat": -8.040, "lng": -34.925},
    {"bairro": "Espinheiro", "denuncias": 5, "renda": 7000, "lat": -8.043, "lng": -34.898},
]

# Preparação do modelo k-NN
X = np.array([[d["denuncias"], d["renda"]] for d in data])
y = ["Alto" if d["denuncias"] > 20 else "Médio" if d["denuncias"] > 10 else "Baixo" for d in data]
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, y)

# Página inicial
@app.route("/")
def home():
    return render_template("index.html")

# Mapa com áreas de risco
@app.route("/map")
def map_view():
    classified_data = [
        {**d, "risco": knn.predict([[d["denuncias"], d["renda"]]])[0]} for d in data
    ]

    # Gera os dados do gráfico
    grafico_dados = [
        {"bairro": d["bairro"], "denuncias": d["denuncias"], "risco": knn.predict([[d["denuncias"], d["renda"]]])[0]}
        for d in data
    ]

    return render_template("map.html", data=classified_data, grafico_dados=grafico_dados)


# Reconhecimento de imagens com Google Vision API
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
        client = vision.ImageAnnotatorClient()
        with open(filepath, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)

        # Processa os resultados da API Vision
        labels = response.label_annotations
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

        return render_template("recognize.html", result=result)

    return render_template("recognize.html")

# API para gráficos (exemplo de dados)
@app.route("/api/denuncias")
def api_denuncias():
    bairros = [{"bairro": d["bairro"], "denuncias": d["denuncias"]} for d in data]
    return jsonify(bairros)

if __name__ == "__main__":
    app.run(debug=True)
