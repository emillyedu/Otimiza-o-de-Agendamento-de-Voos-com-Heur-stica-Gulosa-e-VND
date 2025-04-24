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

    return pistas

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

    melhor_solucao = None
    melhor_custo = float('inf')
    melhor_custo_grasp = None

    for _ in range(iteracoes):
        pistas_iniciais = escalonar_voos_construcao(voos, t, num_pistas, alpha=0.4)
        custo_grasp = calcular_custo_total(pistas_iniciais)

        pistas_otimizadas, tempo_vnd = busca_local_vnd(pistas_iniciais, t)
        custo_vnd = calcular_custo_total(pistas_otimizadas)

        if custo_vnd < melhor_custo:
            melhor_solucao = pistas_otimizadas
            melhor_custo = custo_vnd
            melhor_custo_grasp = custo_grasp

    data_final_grasp = datetime.now()
    tempo_grasp = (data_final_grasp - data_inicial_grasp).total_seconds()*1000

    return melhor_solucao, melhor_custo, melhor_custo_grasp, tempo_grasp, tempo_vnd

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

    n, num_pistas, r, c, p, t, valor_otimo = ler_entrada(entrada)
    voos = [Voo(id=i, r=r[i], c=c[i], p=p[i]) for i in range(n)]

    melhor_solucao, melhor_custo, melhor_custo_grasp, tempo_grasp, tempo_vnd = grasp_vns(voos, t, num_pistas)

    gap_grasp = calcular_gap(melhor_custo_grasp, valor_otimo)
    gap_vnd = calcular_gap(melhor_custo, valor_otimo)

    with open(saida, 'w') as f:
        f.write(f"{melhor_custo}\n")
        for pista in melhor_solucao:
            ids = " ".join(str(voo.id + 1) for voo in pista)
            f.write(f"{ids}\n")
        
        f.write("\nResumo dos Resultados:\n")
        f.write(f"Custo GRASP: {melhor_custo_grasp}\n")
        f.write(f"GAP GRASP: {gap_grasp:.2f}%\n")
        f.write(f"Tempo GRASP (ms): {tempo_grasp:.2f}\n")
        f.write(f"Custo GRASP + VND: {melhor_custo}\n")
        f.write(f"GAP GRASP + VND: {gap_vnd:.2f}%\n")
        f.write(f"Tempo GRASP + VND (ms): {tempo_vnd:.2f}\n")

    # df = pd.DataFrame({
    # 'Valor ótimo': [valor_otimo],
    # 'Custo GRASP': [melhor_custo_grasp],
    # 'GAP GRASP': [gap_grasp],
    # 'Tempo GRASP (ms)': [tempo_grasp],
    # 'Custo final + VND': [melhor_custo],
    # 'GAP GRASP + VND:': [gap_vnd],
    # 'Tempo GRASP + VND (ms)': [tempo_vnd]
    # }, index=['instancia1'])

    # print(df)

    print(f"\nResumo dos Resultados:")
    print(f"Valor ótimo: {valor_otimo}")
    print(f"Valor GRASP: {melhor_custo_grasp}")
    print(f"GAP GRASP: {gap_grasp:.2f}%")
    print(f"Tempo GRASP (ms): {tempo_grasp:.2f}")
    print(f"Valor GRASP + VND: {melhor_custo}")
    print(f"GAP GRASP + VND: {gap_vnd:.2f}%")
    print(f"Tempo GRASP + VND (ms): {tempo_vnd:.2f}")

if __name__ == "__main__":
    main()
