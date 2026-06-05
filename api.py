from flask import Flask, request, jsonify
from flask_cors import CORS
from grafo import MapaGrafo, dijkstra

app = Flask(__name__)
CORS(app) 

meu_mapa = MapaGrafo()

def popular_mapa_padrao():
    meu_mapa.grafo = {} 
    meu_mapa.adicionar_aresta('A', 'B', distancia=5, tempo=10)
    meu_mapa.adicionar_aresta('A', 'C', distancia=2, tempo=3)
    meu_mapa.adicionar_aresta('C', 'B', distancia=1, tempo=2)
    meu_mapa.adicionar_aresta('B', 'D', distancia=2, tempo=2)
    meu_mapa.adicionar_aresta('C', 'D', distancia=6, tempo=8)
    meu_mapa.adicionar_aresta('D', 'E', distancia=3, tempo=4)

popular_mapa_padrao()

@app.route('/mapa_padrao', methods=['POST'])
def carregar_padrao():
    popular_mapa_padrao()
    return jsonify({"sucesso": True, "mensagem": "Mapa padrão carregado."}), 200

@app.route('/resetar_mapa', methods=['POST'])
def resetar_mapa():
    meu_mapa.grafo = {}
    return jsonify({"sucesso": True, "mensagem": "Mapa zerado com sucesso."}), 200

@app.route('/adicionar_rua', methods=['POST'])
def adicionar_rua():
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    distancia = float(dados.get('distancia', 1))
    tempo = float(dados.get('tempo', 1))
    bidirecional = dados.get('bidirecional', True)
    
    if destino in meu_mapa.grafo.get(origem, {}):
        return jsonify({"sucesso": False, "mensagem": f"Rua entre {origem} e {destino} já existe!"}), 400
        
    meu_mapa.adicionar_aresta(origem, destino, distancia, tempo, bidirecional)
    return jsonify({"sucesso": True, "mensagem": f"Rua {origem}-{destino} adicionada!"}), 200

@app.route('/calcular_rota', methods=['POST'])
def rota_api():
    dados = request.json
    inicio = dados.get('inicio')
    fim = dados.get('fim')
    criterio = dados.get('criterio', 'distancia') 
    
    if inicio not in meu_mapa.grafo or fim not in meu_mapa.grafo:
        return jsonify({"sucesso": False, "mensagem": "Origem ou Destino não existem no mapa."}), 404
        
    rota, custo = dijkstra(meu_mapa, inicio, fim, criterio)
    
    if rota:
        # Erro corrigido: apenas "custo": custo
        return jsonify({"sucesso": True, "rota": rota, "custo": custo}), 200
    else:
        return jsonify({"sucesso": False, "mensagem": "Rota impossível"}), 404

@app.route('/bloquear_rua', methods=['POST'])
def bloquear_api():
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    
    # Erro corrigido: removido o "origen_check :="
    if origem not in meu_mapa.grafo or destino not in meu_mapa.grafo.get(origem, {}):
        return jsonify({"sucesso": False, "mensagem": "Rua não existe."}), 404
        
    meu_mapa.bloquear_aresta(origem, destino)
    return jsonify({"sucesso": True, "mensagem": "Rua bloqueada."}), 200

# ==========================================
# NOVA ROTA: LIBERAR RUA (DESBLOQUEIO)
# ==========================================
@app.route('/liberar_rua', methods=['POST'])
def liberar_api():
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    
    if origem not in meu_mapa.grafo or destino not in meu_mapa.grafo.get(origem, {}):
        return jsonify({"sucesso": False, "mensagem": "Rua não existe para ser liberada."}), 404
        
    meu_mapa.liberar_aresta(origem, destino)
    return jsonify({"sucesso": True, "mensagem": "Rua liberada com sucesso."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)