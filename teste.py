# Importamos a classe e a função do arquivo que criamos anteriormente
# Certifique-se de que o outro arquivo se chama 'grafo.py'
from grafo import MapaGrafo, dijkstra
import argparse


def criar_mapa_padrao():
    """Cria e retorna um mapa exemplo com os nós A, B, C, D, E."""
    meu_mapa = MapaGrafo()
    meu_mapa.adicionar_aresta('A', 'B', distancia=5, tempo=10)
    meu_mapa.adicionar_aresta('A', 'C', distancia=2, tempo=3)
    meu_mapa.adicionar_aresta('C', 'B', distancia=1, tempo=2)
    meu_mapa.adicionar_aresta('B', 'D', distancia=2, tempo=2)
    meu_mapa.adicionar_aresta('C', 'D', distancia=6, tempo=8)
    meu_mapa.adicionar_aresta('D', 'E', distancia=3, tempo=4)
    return meu_mapa


def rodar_testes():
    meu_mapa = criar_mapa_padrao()

    print("==========================================")
    print("🚦 SIMULADOR DE ROTAS - TESTE NO TERMINAL 🚦")
    print("==========================================\n")

    print("--- TESTE 1: Rota Normal (Critério: Distância) ---")
    rota, custo = dijkstra(meu_mapa, inicio='A', fim='E', criterio='distancia')

    if rota:
        print(f"📍 Melhor rota encontrada: {' -> '.join(rota)}")
        print(f"📏 Custo total (Distância): {custo}\n")
    else:
        print("❌ Nenhuma rota encontrada.\n")

    print("--- TESTE 2: Acidente relatado! A rua entre C e B foi interditada. ---")
    print("Recalculando rota...\n")

    meu_mapa.bloquear_aresta('C', 'B')

    rota_bloqueada, custo_bloqueado = dijkstra(meu_mapa, inicio='A', fim='E', criterio='distancia')

    if rota_bloqueada:
        print(f"📍 Nova rota encontrada: {' -> '.join(rota_bloqueada)}")
        print(f"📏 Novo custo total (Distância): {custo_bloqueado}\n")
    else:
        print("❌ Nenhuma rota encontrada. Você está preso!\n")


def simular_interativo():
    """Permite ao usuário informar pontos, arestas e bloqueios via terminal."""
    
    # ---------------------------------------------------------
    # FUNÇÕES AUXILIARES DE TRATAMENTO DE ERROS
    # ---------------------------------------------------------
    def ler_inteiro(pergunta, minimo=0, maximo=None):
        while True:
            texto = input(pergunta).strip()
            try:
                valor = int(texto)
                if minimo is not None and valor < minimo:
                    print(f'Digite um número maior ou igual a {minimo}.')
                    continue
                if maximo is not None and valor > maximo:
                    print(f'O mapa possui apenas {maximo} rua(s). Digite um valor até {maximo}.')
                    continue
                return valor
            except ValueError:
                print('Valor inválido. Digite apenas números inteiros.')

    def ler_float(pergunta):
        while True:
            texto = input(pergunta).strip().replace(',', '.')
            try:
                return float(texto)
            except ValueError:
                print('Valor numérico inválido. Tente novamente.')

    def ler_sim_nao(pergunta, padrao='s'):
        resposta = input(pergunta).strip().lower()
        if not resposta:
            resposta = padrao
        return resposta in ('s', 'sim')

    print('==========================================')
    print('🧭 SIMULADOR DE ROTAS (MODO INTERATIVO)')
    print('==========================================')
    
    usar_padrao = ler_sim_nao('Deseja carregar o mapa padrão de teste (Nós A até E)? (s/n): ', padrao='s')
    
    if usar_padrao:
        meu_mapa = criar_mapa_padrao()
        print("✅ Mapa padrão carregado com sucesso!")
    else:
        meu_mapa = MapaGrafo()
        print('\nPasso 1: cadastrar as arestas do grafo')

        n = ler_inteiro('Adicionar arestas: quantas arestas você quer? ', minimo=0)

        for i in range(1, n + 1):
            print(f"\nAresta {i}/{n}")
            origem = input('Origem: ').strip().upper()
            destino = input('Destino: ').strip().upper()
            distancia = ler_float('Qual a distância da aresta? ')
            tempo = ler_float('Qual o tempo da aresta? ')
            bidirecional = ler_sim_nao('Bidirecional? (s/n): ', padrao='s')

            meu_mapa.adicionar_aresta(
                origem, destino, distancia=distancia, tempo=tempo, bidirecional=bidirecional
            )

        if not meu_mapa.grafo:
            print('\nGrafo vazio. Execute novamente e adicione pelo menos uma aresta.')
            return

    # ---------------------------------------------------------
    # PASSO 2: BLOQUEIOS (INTERDIÇÕES)
    # ---------------------------------------------------------
    print('\nPasso 2: bloquear ruas (opcional)')
    if ler_sim_nao('Deseja bloquear alguma rua agora? (s/n): ', padrao='n'):
        
        arestas_unicas = set()
        for o, vizinhos in meu_mapa.grafo.items():
            for d in vizinhos:
                arestas_unicas.add(frozenset([o, d]))
        total_arestas = len(arestas_unicas)

        m = ler_inteiro('Quantas ruas deseja bloquear? ', minimo=0, maximo=total_arestas)
        
        bloqueios_realizados = 0
        while bloqueios_realizados < m:
            print(f"\nBloqueio {bloqueios_realizados + 1}/{m}")
            o = input('Origem da rua: ').strip().upper()
            d = input('Destino da rua: ').strip().upper()
            
            # Validação 1: Verifica se a rua existe
            if o not in meu_mapa.grafo or d not in meu_mapa.grafo.get(o, {}):
                print(f'❌ ERRO: A rua entre {o} e {d} não existe no mapa! Tente novamente com ruas válidas.')
                continue 
            
            # --- NOVA VALIDAÇÃO 2: Não deixa bloquear o que já está bloqueado ---
            if meu_mapa.grafo[o][d].get('bloqueado', False):
                print(f'⚠️ AVISO: A rua entre {o} e {d} JÁ ESTÁ bloqueada! Escolha outro trecho.')
                continue # Volta para o início do loop sem gastar a contagem de bloqueios
            # ---------------------------------------------------------------------
            
            meu_mapa.bloquear_aresta(o, d)
            print(f'🚧 Rua entre {o} e {d} bloqueada.')
            bloqueios_realizados += 1

    # ---------------------------------------------------------
    # PASSO 3: CÁLCULO DE ROTAS
    # ---------------------------------------------------------
    print('\nPasso 3: calcular rotas')
    while True:
        inicio = input('Nó de início: ').strip().upper()
        fim = input('Nó de destino: ').strip().upper()
        
        while True:
            criterio_input = input("Critério ('D' para distância ou 'T' para tempo): ").strip().lower()
            
            if criterio_input in ('d', 'distancia'):
                criterio = 'distancia'
                break
            elif criterio_input in ('t', 'tempo'):
                criterio = 'tempo'
                break
            else:
                print("❌ ERRO: Critério inválido. Digite apenas 'D' para distância ou 'T' para tempo.")

        if inicio not in meu_mapa.grafo or fim not in meu_mapa.grafo:
            print('❌ ERRO: O nó de início ou destino não existe no grafo. Verifique as letras.\n')
        else:
            rota, custo = dijkstra(meu_mapa, inicio=inicio, fim=fim, criterio=criterio)
            
            if rota:
                print(f"📍 Melhor rota: {' -> '.join(rota)}")
                print(f"📏 Custo ({criterio}): {custo:.2f}\n")
            else:
                print('🚧 ROTA IMPOSSÍVEL: Todas as ruas de acesso estão bloqueadas ou não há conexão!\n')

        if not ler_sim_nao('Deseja calcular outra rota? (s/n): ', padrao='n'):
            print('Encerrando simulação.')
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulador de rotas')
    parser.add_argument('--tests', '-t', action='store_true', help='Executa os testes automáticos')
    args = parser.parse_args()

    if args.tests:
        rodar_testes()
    else:
        simular_interativo()