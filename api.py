from flask import Flask, request, jsonify
from flask_cors import CORS
from grafo import MapaGrafo, dijkstra

app = Flask(__name__)
CORS(app) 

# Instanciamos o mapa globalmente, mas agora ele começa VAZIO.
meu_mapa = MapaGrafo()

# Função auxiliar para quando o usuário escolher "Usar Mapa Padrão"
def popular_mapa_padrao():
    meu_mapa.grafo = {} # Limpa tudo antes de popular
    meu_mapa.adicionar_aresta('A', 'B', distancia=5, tempo=10)
    meu_mapa.adicionar_aresta('A', 'C', distancia=2, tempo=3)
    meu_mapa.adicionar_aresta('C', 'B', distancia=1, tempo=2)
    meu_mapa.adicionar_aresta('B', 'D', distancia=2, tempo=2)
    meu_mapa.adicionar_aresta('C', 'D', distancia=6, tempo=8)
    meu_mapa.adicionar_aresta('D', 'E', distancia=3, tempo=4)

# Deixamos o mapa padrão ativado ao ligar o servidor, só por garantia
popular_mapa_padrao()


# ==========================================
# NOVOS ENDPOINTS: FASE 1 (CONSTRUÇÃO DO MAPA)
# ==========================================

@app.route('/mapa_padrao', methods=['POST'])
def carregar_padrao():
    # Se o front pedir o mapa pronto, nós populamos
    popular_mapa_padrao()
    return jsonify({"sucesso": True, "mensagem": "Mapa padrão carregado."}), 200

@app.route('/resetar_mapa', methods=['POST'])
def resetar_mapa():
    # Se o front disser "Criar do Zero", nós apagamos o dicionário
    meu_mapa.grafo = {}
    return jsonify({"sucesso": True, "mensagem": "Mapa zerado com sucesso."}), 200

@app.route('/adicionar_rua', methods=['POST'])
def adicionar_rua():
    # Imita a pergunta do terminal: "Origem, Destino, Distância..."
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    distancia = float(dados.get('distancia', 1))
    tempo = float(dados.get('tempo', 1))
    bidirecional = dados.get('bidirecional', True)
    
    # A mesma trava de segurança que fizemos no teste.py:
    if destino in meu_mapa.grafo.get(origem, {}):
        return jsonify({"sucesso": False, "mensagem": f"Rua entre {origem} e {destino} já existe!"}), 400
        
    meu_mapa.adicionar_aresta(origem, destino, distancia, tempo, bidirecional)
    return jsonify({"sucesso": True, "mensagem": f"Rua {origem}-{destino} adicionada!"}), 200


# ==========================================
# ENDPOINTS ANTIGOS: FASE 2 (SIMULAÇÃO DE GPS)
# ==========================================

@app.route('/calcular_rota', methods=['POST'])
def rota_api():
    dados = request.json
    inicio = dados.get('inicio')
    fim = dados.get('fim')
    
    # NOVO: Agora a API aceita que o React mande o critério!
    criterio = dados.get('criterio', 'distancia') 
    
    # Trava de segurança para nós inexistentes
    if inicio not in meu_mapa.grafo or fim not in meu_mapa.grafo:
        return jsonify({"sucesso": False, "mensagem": "Origem ou Destino não existem no mapa."}), 404
        
    rota, custo = dijkstra(meu_mapa, inicio, fim, criterio)
    
    if rota:
        return jsonify({"sucesso": True, "rota": rota, "custo": custo}), 200
    else:
        return jsonify({"sucesso": False, "mensagem": "Rota impossível (Bloqueada)"}), 404

@app.route('/bloquear_rua', methods=['POST'])
def bloquear_api():
    dados = request.json
    origem = dados.get('origem')
    destino = dados.get('destino')
    
    # Trava de segurança para evitar bloquear rua que não existe
    if origem not in meu_mapa.grafo or destino not in meu_mapa.grafo.get(origem, {}):
        return jsonify({"sucesso": False, "mensagem": "Rua não existe para ser bloqueada."}), 404
        
    meu_mapa.bloquear_aresta(origem, destino)
    return jsonify({"sucesso": True, "mensagem": "Rua bloqueada com sucesso."}), 200

@app.route('/mapa', methods=['GET'])
def obter_mapa():
    # Essa rota é muito útil para o React "enxergar" as ruas criadas no backend
    return jsonify(meu_mapa.grafo), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)