# import sys
# import random
# import copy

# class Voo:
#     def __init__(self, id, r, c, p):
#         self.id = id
#         self.r = r
#         self.c = c
#         self.p = p
#         self.inicio = None
#         self.fim = None
#         self.pista = None

#     def __repr__(self):
#         return f"Voo({self.id + 1}, r={self.r}, c={self.c}, p={self.p})"

# def ler_entrada(nome_arquivo):
#     with open(nome_arquivo, 'r') as f:
#         linhas = [linha.strip() for linha in f if linha.strip()]

#     n = int(linhas[0])
#     num_pistas = int(linhas[1])
#     r = list(map(int, linhas[2].split()))
#     c = list(map(int, linhas[3].split()))
#     p = list(map(int, linhas[4].split()))
#     t = [list(map(int, linha.split())) for linha in linhas[5:5 + n]]

#     return n, num_pistas, r, c, p, t

# def escalonar_voos_grasp(voos, t, num_pistas, alpha=0.3):
#     pistas = [[] for _ in range(num_pistas)]
#     # quando a pista esta liberada de novo
#     fim_pista = [0] * num_pistas

#     # copia da lisa de voos
#     voos_restantes = voos[:]
#     # Embaralha os voos na lista
#     random.shuffle(voos_restantes)

#     # Em qual pista e quando colocar cada voo.
#     while voos_restantes:
#         # Para cada voo não agendado vamos escolher a melhor pista e o melhor tempo de inicio
#         candidatos = []
#         for voo in voos_restantes:
#             melhor_pista = None
#             # Começa com um valor muito alto e vai diminuindo quando encontramos valores menores.
#             melhor_inicio = float('inf')
#             #  Para cada pista, calcula o melhor horário possível para o voo
#             for i in range(num_pistas):
#                 # Se não há voos na pista ainda, ele pode começar assim que o horário mínimo r permitir
#                 if not pistas[i]:
#                     inicio = max(voo.r, 0)
#                 else:
#                     # Calcula quando o voo pode começar, respeitando o tempo de espera entre o voo anterior e esse. Usa a matriz t, que indica o tempo de espera obrigatório entre pares de voos.
#                     ultimo = pistas[i][-1] # último voo agendado nessa pista
#                     tempo_espera = t[ultimo.id][voo.id] # tempo de espera entre os voos
#                     inicio = max(voo.r, fim_pista[i] + tempo_espera)
#                 if inicio < melhor_inicio:
#                     melhor_inicio = inicio
#                     melhor_pista = i
#             # Para cada voo, salvamos sua melhor pista e o horário mais cedo possível.
#             candidatos.append((voo, melhor_pista, melhor_inicio))

#         # Ordena os candidatos pelo menor valor de inicio, a posição 3 da tupla de voos
#         candidatos.sort(key=lambda x: x[2])
#         # Seleciona os candidatos com os melhores horários, respeitando o limite alpha
#         limite = max(1, int(alpha * len(candidatos)))
#         # Seleciona aleatoriamente um voo dentre os melhores candidatos (os primeiros da lista).
#         escolhido = random.choice(candidatos[:limite])

#         voo, pista, inicio = escolhido
#         voo.pista = pista
#         voo.inicio = inicio
#         voo.fim = inicio + voo.c
#         # Adiciona o voo à lista de voos da pista.
#         pistas[pista].append(voo)
#         # Atualiza o fim da pista com o horário de fim do voo.
#         fim_pista[pista] = voo.fim
#         # Remove o voo da lista de voos restantes.
#         voos_restantes.remove(voo)

#     return pistas

# def calcular_custo_total(pistas):
#     custo_total = 0
#     for pista in pistas:
#         for voo in pista:
#             atraso = max(0, voo.fim - voo.r - voo.c)
#             custo = atraso * voo.p
#             custo_total += custo
#     return custo_total

# def recalcular_tempos(pistas, t):
#     fim_pista = [0] * len(pistas)
#     for i, pista in enumerate(pistas):
#         for j, voo in enumerate(pista):
#             if j == 0:
#                 inicio = max(voo.r, 0)
#             else:
#                 anterior = pista[j-1]
#                 tempo_espera = t[anterior.id][voo.id]
#                 inicio = max(voo.r, anterior.fim + tempo_espera)
#             voo.inicio = inicio
#             voo.fim = inicio + voo.c
#             voo.pista = i
#             fim_pista[i] = voo.fim

# def gerar_vizinhos(pistas, t):
#     vizinhos = []

#     # V1: Troca entre pistas
#     for i in range(len(pistas)):
#         for j in range(i+1, len(pistas)):
#             for vi in range(len(pistas[i])):
#                 for vj in range(len(pistas[j])):
#                     nova_pistas = copy.deepcopy(pistas)
#                     nova_pistas[i][vi], nova_pistas[j][vj] = nova_pistas[j][vj], nova_pistas[i][vi]
#                     recalcular_tempos(nova_pistas, t)
#                     vizinhos.append(nova_pistas)

#     # V2: Troca dentro da mesma pista
#     for i in range(len(pistas)):
#         for vi in range(len(pistas[i])):
#             for vj in range(vi+1, len(pistas[i])):
#                 nova_pistas = copy.deepcopy(pistas)
#                 nova_pistas[i][vi], nova_pistas[i][vj] = nova_pistas[i][vj], nova_pistas[i][vi]
#                 recalcular_tempos(nova_pistas, t)
#                 vizinhos.append(nova_pistas)

#     # V3: Mover voo de uma pista para outra
#     for i in range(len(pistas)):
#         for j in range(len(pistas)):
#             if i == j: continue
#             for vi in range(len(pistas[i])):
#                 for pos in range(len(pistas[j]) + 1):
#                     nova_pistas = copy.deepcopy(pistas)
#                     voo = nova_pistas[i].pop(vi)
#                     nova_pistas[j].insert(pos, voo)
#                     recalcular_tempos(nova_pistas, t)
#                     vizinhos.append(nova_pistas)

#     return vizinhos

# # melhorar a solução inicial, procurando vizinhos com menor custo total (menos atraso). os vizinhos são soluções parecidas com a atual, mas com pequenas mudanças.
# def busca_local(pistas, t):
#     melhor = pistas
#     # pega o custo da solução atual
#     melhor_custo = calcular_custo_total(pistas)

#     melhorou = True
#     while melhorou:
#         melhorou = False
#         # gera vizinhos da solução atual
#         vizinhos = gerar_vizinhos(melhor, t)
#         for vizinho in vizinhos:
#             # calcula o custo do vizinho
#             custo = calcular_custo_total(vizinho)
#             # se o custo do vizinho for menor que o custo atual, atualiza a solução atual
#             if custo < melhor_custo:
#                 melhor = vizinho
#                 melhor_custo = custo
#                 melhorou = True
#                 break
#     # Retorna o melhor vizinho encontrado, que é a solução otimizada.
#     return melhor

# def grasp_vns(voos, t, num_pistas, iteracoes=30):
#     melhor_solucao = None
#     melhor_custo = float('inf')

#     for _ in range(iteracoes):
#         # Gera uma solução inicial usando GRASP com a lista de pistas e seus voos alocados nela.
#         pistas_iniciais = escalonar_voos_grasp(voos, t, num_pistas, alpha=0.4)
#         # Procura melhorar a solução inicial usando busca local, que tenta encontrar vizinhos com menor custo total.
#         pistas_otimizadas = busca_local(pistas_iniciais, t)
#         # Recalcula os tempos de cada voo na solução otimizada.
#         custo = calcular_custo_total(pistas_otimizadas)

#         if custo < melhor_custo:
#             melhor_solucao = pistas_otimizadas
#             melhor_custo = custo

#     return melhor_solucao, melhor_custo

# def main():
#     if len(sys.argv) < 3:
#         print("Uso: python main.py entrada.txt saida.txt")
#         return

#     entrada = sys.argv[1]
#     saida = sys.argv[2]

#     n, num_pistas, r, c, p, t = ler_entrada(entrada)
#     voos = [Voo(id=i, r=r[i], c=c[i], p=p[i]) for i in range(n)]

#     melhor_solucao, melhor_custo = grasp_vns(voos, t, num_pistas)

#     with open(saida, 'w') as f:
#         f.write(f"{melhor_custo}\n")
#         for pista in melhor_solucao:
#             ids = " ".join(str(voo.id + 1) for voo in pista)
#             f.write(f"{ids}\n")

# if __name__ == "__main__":
#     main()










































import sys
import random
import copy

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

    return n, num_pistas, r, c, p, t

def escalonar_voos_grasp(voos, t, num_pistas, alpha=0.3):
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

# VND - Vizinhança 1
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

# VND - Vizinhança 2
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

# VND - Vizinhança 3
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

# VND de verdade
def busca_local_vnd(pistas, t):
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

    return melhor

def grasp_vns(voos, t, num_pistas, iteracoes=30):
    melhor_solucao = None
    melhor_custo = float('inf')

    for _ in range(iteracoes):
        pistas_iniciais = escalonar_voos_grasp(voos, t, num_pistas, alpha=0.4)
        pistas_otimizadas = busca_local_vnd(pistas_iniciais, t)
        custo = calcular_custo_total(pistas_otimizadas)

        if custo < melhor_custo:
            melhor_solucao = pistas_otimizadas
            melhor_custo = custo

    return melhor_solucao, melhor_custo

def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py entrada.txt saida.txt")
        return

    entrada = sys.argv[1]
    saida = sys.argv[2]

    n, num_pistas, r, c, p, t = ler_entrada(entrada)
    voos = [Voo(id=i, r=r[i], c=c[i], p=p[i]) for i in range(n)]

    melhor_solucao, melhor_custo = grasp_vns(voos, t, num_pistas)

    with open(saida, 'w') as f:
        f.write(f"{melhor_custo}\n")
        for pista in melhor_solucao:
            ids = " ".join(str(voo.id + 1) for voo in pista)
            f.write(f"{ids}\n")

if __name__ == "__main__":
    main()
