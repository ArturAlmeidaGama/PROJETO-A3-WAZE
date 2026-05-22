from flask import Flask, request, jsonify
from flask_cors import CORS
from grafo import MapaGrafo, dijkstra

# Inicializa o servidor Flask
app = Flask(__name__)
# Permite que o frontend em React converse com este backend
CORS(app) 

# Instanciamos o nosso mapa globalmente para a API usar
meu_mapa = MapaGrafo()

# (Aqui você colocaria aquele mesmo código de criação dos nós A, B, C, D, E
# ou criaria uma função para popular o mapa)
meu_mapa.adicionar_aresta('A', 'B', distancia=5, tempo=10)
meu_mapa.adicionar_aresta('A', 'C', distancia=2, tempo=3)
meu_mapa.adicionar_aresta('C', 'B', distancia=1, tempo=2)
meu_mapa.adicionar_aresta('B', 'D', distancia=2, tempo=2)
meu_mapa.adicionar_aresta('C', 'D', distancia=6, tempo=8)
meu_mapa.adicionar_aresta('D', 'E', distancia=3, tempo=4)

# ==========================================
# ENDPOINTS DA API (Portas de entrada para o React)
# ==========================================

@app.route('/calcular_rota', methods=['POST'])
def rota_api():
    # 1. Recebe os dados que o React enviou (os pontos que o professor escolher)
    dados = request.json
    inicio = dados.get('inicio')
    fim = dados.get('fim')
    
    # 2. Chama a SUA função Dijkstra
    rota, custo = dijkstra(meu_mapa, inicio, fim, criterio='distancia')
    
    # 3. Devolve a resposta em formato JSON para o React desenhar na tela
    if rota:
        return jsonify({"sucesso": True, "rota": rota, "custo": custo}), 200
    else:
        return jsonify({"sucesso": False, "mensagem": "Rota não encontrada"}), 404

@app.route('/bloquear_rua', methods=['POST'])
def bloquear_api():
    # O professor pediu para bloquear uma rua na hora? O React chama essa rota.
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    
    meu_mapa.bloquear_aresta(origem, destino)
    return jsonify({"sucesso": True, "mensagem": f"Rua entre {origem} e {destino} bloqueada!"}), 200

# Executa o servidor na porta 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/liberar_rua', methods=['POST'])
def liberar_api():
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    
    meu_mapa.liberar_aresta(origem, destino)
    return jsonify({"sucesso": True, "mensagem": f"Rua entre {origem} e {destino} liberada!"}), 200

@app.route('/mapa', methods=['GET'])
def obter_mapa():
    # Retorna todo o dicionário do grafo.
    # Assim o React sabe exatamente quais ruas existem e quais estão bloqueadas.
    return jsonify(meu_mapa.grafo), 200