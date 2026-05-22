import heapq

# ==========================================
# 1. ESTRUTURA DE DADOS: O GRAFO
# ==========================================
class MapaGrafo:
    def __init__(self):
        # O grafo é representado por um dicionário de dicionários (Lista de Adjacência).
        # A chave principal é o nó de origem. O valor é outro dicionário onde as 
        # chaves são os vizinhos e os valores são as métricas (distância, tempo, etc).
        # Exemplo: { 'A': {'B': {'distancia': 10, 'tempo': 5}, 'C': ...} }
        self.grafo = {}

    def adicionar_no(self, no):
        # Antes de adicionar um nó, verificamos se ele já existe.
        # Isso evita sobrescrever um nó existente e perder suas conexões (arestas).
        if no not in self.grafo:
            self.grafo[no] = {} # Cria o nó sem nenhum vizinho inicialmente.

    def adicionar_aresta(self, origem, destino, distancia, tempo, bidirecional=True):
        # Garante que os nós de origem e destino existam no grafo antes de conectá-los.
        self.adicionar_no(origem)
        self.adicionar_no(destino)
        
        # Cria a conexão da origem para o destino.
        # Salva as informações de peso (distância e tempo) no dicionário aninhado.
        self.grafo[origem][destino] = {'distancia': distancia, 'tempo': tempo}
        
        # Se a rua for de mão dupla, criamos a conexão no sentido inverso também.
        if bidirecional:
            self.grafo[destino][origem] = {'distancia': distancia, 'tempo': tempo}

    def bloquear_aresta(self, origem, destino, bidirecional=True):
        # Verifica se realmente existe uma rua (aresta) entre a origem e o destino
        if destino in self.grafo.get(origem, {}):
            # Adiciona uma nova chave 'bloqueado' com valor True nos atributos da aresta.
            # Isso simula o obstáculo/interdição em tempo real exigido pelo professor.
            self.grafo[origem][destino]['bloqueado'] = True
            
            # Se for mão dupla, aplica o bloqueio no sentido inverso também.
            if bidirecional:
                self.grafo[destino][origem]['bloqueado'] = True
    
    def liberar_aresta(self, origem, destino, bidirecional=True):
        if destino in self.grafo.get(origem, {}):
            self.grafo[origem][destino]['bloqueado'] = False
            if bidirecional:
                self.grafo[destino][origem]['bloqueado'] = False

# ==========================================
# 2. ALGORITMO DE BUSCA: DIJKSTRA
# ==========================================
def dijkstra(mapa, inicio, fim, criterio='distancia'):
    # Fila de prioridade: armazena tuplas no formato (custo_acumulado, no_atual).
    # O módulo heapq garante que sempre vamos tirar o nó com o menor custo primeiro.
    fila = [(0, inicio)]
    
    # Dicionário para rastrear o menor custo conhecido para chegar a cada nó.
    # Inicializamos todos com infinito (float('inf')), pois ainda não sabemos a distância.
    custos = {no: float('inf') for no in mapa.grafo}
    custos[inicio] = 0 # A distância do ponto de partida para ele mesmo é 0.
    
    # Dicionário para reconstruir o caminho no final. 
    # Guarda o "nó pai" (de onde viemos) para chegar ao nó atual com o menor custo.
    caminho_anterior = {no: None for no in mapa.grafo}

    # Enquanto houver caminhos possíveis para explorar na fila...
    while fila:
        # Pega o nó que tem o menor custo acumulado até o momento.
        custo_atual, no_atual = heapq.heappop(fila)

        # Otimização: Se chegamos ao destino final, não precisamos explorar o resto do mapa.
        if no_atual == fim:
            break

        # Se já encontramos um caminho mais rápido para este nó antes, 
        # ignoramos essa iteração para não processar caminhos sub-ótimos.
        if custo_atual > custos[no_atual]:
            continue

        # Explorando os vizinhos do nó atual
        for vizinho, pesos in mapa.grafo[no_atual].items():
            
            # --- CHECAGEM DE OBSTÁCULO ---
            # Se a aresta tem a chave 'bloqueado' como True, ignoramos essa rua.
            # O .get() retorna False se a chave 'bloqueado' não existir (rua normal).
            if pesos.get('bloqueado', False):
                continue # Pula esta rua e vai para o próximo vizinho
                
            # Define qual métrica vamos usar (pode ser 'distancia' ou 'tempo')
            peso_aresta = pesos[criterio]
            
            # Calcula qual seria o custo para chegar no vizinho passando pelo nó atual
            novo_custo = custo_atual + peso_aresta

            # Se esse novo caminho for mais barato que o caminho anterior conhecido para o vizinho...
            if novo_custo < custos[vizinho]:
                custos[vizinho] = novo_custo          # Atualizamos o menor custo
                caminho_anterior[vizinho] = no_atual  # Registramos que viemos pelo 'no_atual'
                
                # Colocamos o vizinho na fila para explorar as conexões dele no futuro
                heapq.heappush(fila, (novo_custo, vizinho))

    # ==========================================
    # 3. RECONSTRUÇÃO DA ROTA
    # ==========================================
    # O algoritmo já rodou, agora precisamos fazer o caminho de trás para frente.
    rota = []
    atual = fim
    
    # Vamos navegando de volta pelos nós "pais" até chegar ao início (que não tem pai, é None)
    while atual is not None:
        rota.insert(0, atual) # Insere no começo da lista para a rota ficar na ordem certa (A -> B -> C)
        atual = caminho_anterior[atual]
        
    # Se o primeiro nó da rota for o nó de início, significa que encontramos um caminho.
    # Caso contrário, o destino é inalcançável e retornamos None.
    return rota if rota[0] == inicio else None, custos[fim]