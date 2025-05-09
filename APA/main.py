from datetime import datetime
import sys
import random
import copy
import pandas as pd

class Voo:
    def __init__(self, id, r, c, p):
        self.id = id
        self.r = r
        self.c = c
        self.p = p
        self.inicio = None
        self.fim = None
        self.pista = None

    def __repr__(self):
        return f"Voo({self.id + 1}, r={self.r}, c={self.c}, p={self.p})"

def ler_entrada(nome_arquivo):
    with open(nome_arquivo, 'r') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    n = int(linhas[0])
    num_pistas = int(linhas[1])
    r = list(map(int, linhas[2].split()))
    c = list(map(int, linhas[3].split()))
    p = list(map(int, linhas[4].split()))
    t = [list(map(int, linha.split())) for linha in linhas[5:5 + n]]

    valor_otimo = int(linhas[5 + n])
    return n, num_pistas, r, c, p, t, valor_otimo

def escalonar_voos_construcao(voos, t, num_pistas, alpha=0.3):
    inicio_tempo = datetime.now()
    pistas = [[] for _ in range(num_pistas)]
    fim_pista = [0] * num_pistas
    voos_restantes = voos[:]
    random.shuffle(voos_restantes)

    while voos_restantes:
        candidatos = []
        for voo in voos_restantes:
            melhor_pista = None
            melhor_inicio = float('inf')
            for i in range(num_pistas):
                if not pistas[i]:
                    inicio = max(voo.r, 0)
                else:
                    ultimo = pistas[i][-1]
                    tempo_espera = t[ultimo.id][voo.id]
                    inicio = max(voo.r, fim_pista[i] + tempo_espera)
                if inicio < melhor_inicio:
                    melhor_inicio = inicio
                    melhor_pista = i
            candidatos.append((voo, melhor_pista, melhor_inicio))

        candidatos.sort(key=lambda x: x[2])
        limite = max(1, int(alpha * len(candidatos)))
        escolhido = random.choice(candidatos[:limite])

        voo, pista, inicio = escolhido
        voo.pista = pista
        voo.inicio = inicio
        voo.fim = inicio + voo.c
        pistas[pista].append(voo)
        fim_pista[pista] = voo.fim
        voos_restantes.remove(voo)
    final_time = datetime.now()

    tempo_guloso = (final_time - inicio_tempo).total_seconds()*1000
# tempo_grasp = (data_final_grasp - data_inicial_grasp).total_seconds()*1000
    return pistas, tempo_guloso

def calcular_custo_total(pistas):
    custo_total = 0
    for pista in pistas:
        for voo in pista:
            atraso = max(0, voo.fim - voo.r - voo.c)
            custo = atraso * voo.p
            custo_total += custo
    return custo_total

def recalcular_tempos(pistas, t):
    fim_pista = [0] * len(pistas)
    for i, pista in enumerate(pistas):
        for j, voo in enumerate(pista):
            if j == 0:
                inicio = max(voo.r, 0)
            else:
                anterior = pista[j-1]
                tempo_espera = t[anterior.id][voo.id]
                inicio = max(voo.r, anterior.fim + tempo_espera)
            voo.inicio = inicio
            voo.fim = inicio + voo.c
            voo.pista = i
            fim_pista[i] = voo.fim

def gerar_vizinhos_troca_entre_pistas(pistas, t):
    vizinhos = []
    for i in range(len(pistas)): 
        for j in range(i+1, len(pistas)):
            for vi in range(len(pistas[i])):
                for vj in range(len(pistas[j])):
                    nova_pistas = copy.deepcopy(pistas)
                    nova_pistas[i][vi], nova_pistas[j][vj] = nova_pistas[j][vj], nova_pistas[i][vi]
                    recalcular_tempos(nova_pistas, t)
                    vizinhos.append(nova_pistas)
    return vizinhos

def gerar_vizinhos_troca_mesma_pista(pistas, t):
    vizinhos = []
    for i in range(len(pistas)):
        for vi in range(len(pistas[i])):
            for vj in range(vi+1, len(pistas[i])):
                nova_pistas = copy.deepcopy(pistas)
                nova_pistas[i][vi], nova_pistas[i][vj] = nova_pistas[i][vj], nova_pistas[i][vi]
                recalcular_tempos(nova_pistas, t)
                vizinhos.append(nova_pistas)
    return vizinhos

def gerar_vizinhos_mover_entre_pistas(pistas, t):
    vizinhos = []
    for i in range(len(pistas)):
        for j in range(len(pistas)):
            if i == j:
                continue
            for vi in range(len(pistas[i])):
                for pos in range(len(pistas[j]) + 1):
                    nova_pistas = copy.deepcopy(pistas)
                    voo = nova_pistas[i].pop(vi)
                    nova_pistas[j].insert(pos, voo)
                    recalcular_tempos(nova_pistas, t)
                    vizinhos.append(nova_pistas)
    return vizinhos

def busca_local_vnd(pistas, t):
    data_inicial_vnd = datetime.now()
    vizinhancas = [
        gerar_vizinhos_troca_entre_pistas,
        gerar_vizinhos_troca_mesma_pista,
        gerar_vizinhos_mover_entre_pistas
    ]

    melhor = pistas
    melhor_custo = calcular_custo_total(melhor)
    k = 0

    while k < len(vizinhancas):
        vizinhos = vizinhancas[k](melhor, t)
        encontrou_melhor = False

        for vizinho in vizinhos:
            custo = calcular_custo_total(vizinho)
            if custo < melhor_custo:
                melhor = vizinho
                melhor_custo = custo
                encontrou_melhor = True
                k = 0
                break

        if not encontrou_melhor:
            k += 1

    data_final_vnd = datetime.now()
    tempo_vnd = (data_final_vnd - data_inicial_vnd).total_seconds()*1000

    return melhor, tempo_vnd

def grasp_vns(voos, t, num_pistas, iteracoes=10):
    data_inicial_grasp = datetime.now()

    melhor_solucao_pistas = None
    melhor_custo = float('inf')
    # melhor_custo_grasp = None

    for _ in range(iteracoes):
        # Guloso
        pistas_iniciais, tempo_guloso= escalonar_voos_construcao(voos, t, num_pistas, alpha=0.4)
        custo_guloso = calcular_custo_total(pistas_iniciais)

        pistas_otimizadas, tempo_vnd = busca_local_vnd(pistas_iniciais, t)
        custo_vnd = calcular_custo_total(pistas_otimizadas)

        if custo_vnd < melhor_custo:
            melhor_solucao_pistas = pistas_otimizadas
            melhor_custo = custo_vnd
            # melhor_custo_guloso = custo_guloso

    data_final_grasp = datetime.now()
    tempo_grasp = (data_final_grasp - data_inicial_grasp).total_seconds()*1000

    return melhor_solucao_pistas, melhor_custo, tempo_grasp

def calcular_gap(valor_heuristica, valor_otimo):
    if valor_otimo == 0:
        raise ValueError("O valor ótimo não pode ser zero.")
    gap = ((valor_heuristica - valor_otimo) / valor_otimo) * 100
    return gap

def main():
    pd.set_option('display.max_columns', None)
    
    if len(sys.argv) < 3:
        print("Uso: python main.py entrada.txt saida.txt")
        return

    entrada = sys.argv[1]
    saida = sys.argv[2]

    # r - quando começa
    # c - quanto tempo leva
    # p - penalidade
    # t - tempo de espera entre voos

    n, num_pistas, r, c, p, t, valor_otimo = ler_entrada(entrada)
    voos = [Voo(id=i, r=r[i], c=c[i], p=p[i]) for i in range(n)]


    #CHAMADA DO GULOSO
    pistas_guloso, tempo_guloso = escalonar_voos_construcao(voos, t, num_pistas, alpha=0.4)
    custo_guloso = calcular_custo_total(pistas_guloso)

    # CHAMADA DO VND
    melhor_solucao_VND, tempo_vnd = busca_local_vnd(pistas_guloso, t)
    custo_vnd = calcular_custo_total(melhor_solucao_VND)

    # CHAMADA DO  GRASP
    melhor_solucao_pistas_grasp, melhor_custo_grasp, tempo_grasp = grasp_vns(voos, t, num_pistas)
    # melhor_solucao, melhor_custo_vnd, melhor_custo_guloso,tempo_grasp, tempo_vnd, tempo_guloso

    gap_grasp = calcular_gap(melhor_custo_grasp, valor_otimo)
    gap_vnd = calcular_gap(custo_vnd, valor_otimo)
    gap_guloso = calcular_gap(custo_guloso, valor_otimo)

    with open(saida, 'w') as f:
        f.write(f"{melhor_custo_grasp}\n")
        for pista in melhor_solucao_pistas_grasp:
            ids = " ".join(str(voo.id + 1) for voo in pista)
            f.write(f"{ids}\n")
        
        f.write("\nResumo dos Resultados:\n")

        f.write(f"Valor otimo: {valor_otimo}\n")

        f.write(f"\nGULOSO:\n")
        f.write(f"Alocacao de voos:{pistas_guloso}\n")
        f.write(f"Custo guloso: {custo_guloso}\n")
        f.write(f"GAP guloso: {gap_guloso:.2f}%\n")
        f.write(f"Tempo Guloso (ms): {tempo_guloso:.2f}\n")

        f.write(f"______________________________________________________________\t")

        f.write(f"\nVND:\n")
        f.write(f"Alocacao de voos:{melhor_solucao_VND}\n")
        f.write(f"Custo VND: {custo_vnd}\n")
        f.write(f"GAP VND: {gap_vnd:.2f}%\n")
        f.write(f"Tempo VND (ms): {tempo_vnd:.2f}\n")

        f.write(f"______________________________________________________________\t")

        f.write(f"\nGRASP:\n")
        f.write(f"Alocacao de voos:{melhor_solucao_pistas_grasp}\n")
        f.write(f"Custo GRASP: {melhor_custo_grasp}\n")
        f.write(f"GAP GRASP: {gap_grasp:.2f}%\n")
        f.write(f"Tempo GRASP (ms): {tempo_grasp:.2f}\n")





        # # f.write(f"Valor ótimo: {valor_otimo}")
        # f.write(f"Custo guloso: {melhor_custo_guloso}\n")
        # f.write(f"GAP guloso: {gap_grasp:.2f}%\n")
        # f.write(f"Tempo Guloso (ms): {tempo_guloso:.2f}\n")
        # f.write(f"Custo VND: {melhor_custo_vnd}\n")
        # f.write(f"GAP VND: {gap_vnd:.2f}%\n")
        # f.write(f"Tempo VND (ms): {tempo_vnd:.2f}\n")
        # f.write(f"Tempo GRASP (ms): {tempo_grasp:.2f}\n")


    print(f"\n CALCULO CONCLUÍDO, VERIFIQUE O ARQUIVO")
    
    # print(f"Valor ótimo: {valor_otimo}")
    # print(f"Custo guloso: {melhor_custo_guloso}")
    # print(f"GAP guloso: {gap_grasp:.2f}%")
    # print(f"Tempo guloso (ms): {tempo_guloso:.2f}")
    # print(f"Custo VND: {melhor_custo_vnd}")
    # print(f"GAP VND: {gap_vnd:.2f}%")
    # print(f"Tempo VND (ms): {tempo_vnd:.2f}")
    # print(f"Tempo GRASP (ms): {tempo_grasp:.2f}")


if __name__ == "__main__":
    main()