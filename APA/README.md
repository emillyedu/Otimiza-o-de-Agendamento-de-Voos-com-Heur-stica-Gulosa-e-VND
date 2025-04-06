# ✈️ Otimização de Agendamento de Voos com GRASP e VND

Este projeto implementa uma solução heurística para o problema de agendamento de pousos de voos em múltiplas pistas, com o objetivo de **minimizar o custo total de atrasos**. A abordagem utiliza a meta-heurística **GRASP (Greedy Randomized Adaptive Search Procedure)** para geração de soluções iniciais, seguida de uma otimização por **VND (Variable Neighborhood Descent)** para melhorar a qualidade da solução.

---

## 📌 Descrição do Problema

Cada voo possui as seguintes informações:
- `r`: horário mais cedo possível para pousar (release time),
- `c`: tempo necessário para concluir o pouso (duração do pouso),
- `p`: penalidade por unidade de tempo de atraso.

Além disso, existe:
- Um número fixo `m` de pistas disponíveis para os pousos,
- Uma matriz `t` de tempos de separação entre dois voos consecutivos (dependendo da ordem de pouso).

**Objetivo:** Escalonar os voos entre as pistas, respeitando os tempos de separação, de forma a minimizar o custo total, onde o custo é definido como o **atraso multiplicado pela penalidade**.

---

## 📥 Entrada

A entrada deve estar em um arquivo `.txt` e conter as seguintes informações:

```
n
m
r1 r2 ... rn
c1 c2 ... cn
p1 p2 ... pn
t[0][0] t[0][1] ... t[0][n-1]
t[1][0] t[1][1] ... t[1][n-1]
...
t[n-1][0] ...        t[n-1][n-1]
```

### Onde:
- `n`: número de voos
- `m`: número de pistas
- `r`: lista com os tempos mais cedo para pouso de cada voo
- `c`: lista com os tempos de duração dos pousos
- `p`: lista com as penalidades de atraso
- `t[i][j]`: tempo de separação obrigatório entre o voo `i` e o `j`, caso `j` venha após `i` na mesma pista

### Exemplo de entrada:
```
5
2
0 2 4 3 1
5 6 8 5 4
10 8 6 12 9
0 2 3 4 2
2 0 1 3 2
3 1 0 2 2
4 3 2 0 1
2 2 2 1 0
```

---

## ⚙️ Funcionamento do Algoritmo

### 1. **GRASP - Geração de Solução Inicial**
- Geração aleatória e adaptativa de soluções com uma lista de candidatos restrita controlada por um parâmetro `alpha` (balanceando aleatoriedade e escolha gulosa).
- Escolha do melhor posicionamento do voo com base no tempo de início mais cedo possível considerando a matriz de separação.

### 2. **VND - Otimização por Busca Local com Vizinhanças Variáveis**
- Após gerar uma solução inicial, aplica-se VND com três vizinhanças distintas:
  - **V1:** Troca de dois voos entre pistas diferentes.
  - **V2:** Troca de posição de dois voos na mesma pista.
  - **V3:** Movimento de um voo de uma pista para outra.

- A cada melhoria encontrada em alguma vizinhança, a busca é reiniciada a partir dessa nova solução.

### 3. **Cálculo do Custo Total**
- Para cada voo, calcula-se o tempo de atraso como `max(0, fim - r - c)`
- Multiplica-se esse atraso pela penalidade `p` e acumula-se o valor para obter o custo total.

---

## 📤 Saída

A saída é gravada em um arquivo `.txt` com o seguinte formato:

```
<valor_total_do_custo>
<lista_de_voos_na_pista_0>
<lista_de_voos_na_pista_1>
...
<lista_de_voos_na_pista_m-1>
```

### Exemplo:
```
48
1 4
2 3 5
```

> Cada número representa o ID do voo (começando em 1).

---

## ▶️ Execução

O programa deve ser executado via terminal com dois argumentos: o nome do arquivo de entrada e o nome do arquivo de saída.

```bash
python main.py entrada.txt saida.txt
```

---

## 📚 Dependências

Nenhuma dependência externa é necessária. O código é compatível com **Python 3.x** e utiliza apenas bibliotecas padrão.

---

## 🎓 Projeto Acadêmico

Este projeto foi desenvolvido para fins educacionais, como parte da disciplina de Análise e Projeto de Algoritmos (2024.2) sob orientação do Prof. Lucídio Cabral.

---



































<!-- # ✈️ Otimização de Agendamento de Voos com GRASP e VND

Este projeto resolve o problema de agendamento de pousos em múltiplas pistas com o objetivo de **minimizar o custo total de atrasos** dos voos. Para isso, é utilizada uma abordagem com:

- Algoritmo **GRASP (Greedy Randomized Adaptive Search Procedure)** para gerar uma solução inicial.
- Otimização por **busca local VND (Variable Neighborhood Descent)** com três tipos de movimentos.

## 🧠 Descrição do Problema

Dado um conjunto de voos, cada um com:
- `r`: horário mais cedo possível para pousar,
- `c`: tempo necessário para o pouso,
- `p`: penalidade por cada unidade de tempo de atraso,

e considerando que:
- Há um número fixo de pistas disponíveis,
- Existe uma matriz `t` com tempos de separação entre pares de voos,

a meta é **distribuir os voos entre as pistas de forma a minimizar o custo total** (atraso ponderado por penalidade).

## 📥 Entrada

A entrada deve estar em um arquivo `.txt` com o seguinte formato:

```
n
m
r1 r2 ... rn
c1 c2 ... cn
p1 p2 ... pn
t11 t12 ... t1n
...
tn1 tn2 ... tnn
```

- `n`: número de voos
- `m`: número de pistas
- `ri`, `ci`, `pi`: dados do i-ésimo voo
- `tij`: tempo mínimo entre o pouso do voo i e do voo j

### Exemplo:
```
5
2
0 2 4 3 1
5 6 8 5 4
10 8 6 12 9
0 1 2 3 4
1 0 1 2 3
2 1 0 1 2
3 2 1 0 1
4 3 2 1 0
```

## ⚙️ Funcionamento

1. **GRASP (Construção Aleatória Gulosa)**
   - Uma lista de candidatos é construída com base em uma métrica de prioridade e escolhida aleatoriamente dentro de uma faixa controlada por `alpha`.

2. **VND (Variable Neighborhood Descent)**
   Aplica busca local com três tipos de vizinhança:
   - Troca de voos entre pistas
   - Troca de voos na mesma pista
   - Movimentação de um voo para outra pista  
   A cada melhora encontrada, reinicia o processo de busca.

## 📤 Saída

A saída será escrita em um arquivo `.txt` com:

```
<valor_custo_total>
<lista_de_voos_pista_1>
<lista_de_voos_pista_2>
...
<lista_de_voos_pista_m>
```

Exemplo:
```
48
1 4 5
2 3
```

*(IDs dos voos começam em 1 na saída)*

## ▶️ Execução

```bash
python main.py entrada.txt saida.txt
```

## 💡 Estratégia Heurística

- O GRASP introduz diversidade nas soluções iniciais.
- O VND explora vizinhanças sistematicamente para evitar mínimos locais.

## 📚 Projeto

Projeto desenvolvido para a disciplina de Análise e Projeto de Algoritmos, 2024.2 – Prof. Lucídio Cabral.












































<!-- # ✈️ Otimização de Agendamento de Voos com Heurística Gulosa e VND

Este projeto resolve o problema de agendamento de pousos em múltiplas pistas com o objetivo de **minimizar o custo total de atrasos** dos voos. Para isso, é utilizada uma abordagem com:

- Algoritmo **guloso inteligente** para gerar uma solução inicial viável.
- Otimização por **busca local VND (Variable Neighborhood Descent)** com três tipos de movimentos.

## Descrição do Problema

Dado um conjunto de voos, cada um com:
- `r`: horário mais cedo possível para pousar,
- `c`: horário ideal de pouso,
- `p`: penalidade por cada unidade de tempo de atraso,

e considerando que:
- Há um número fixo de pistas disponíveis,
- Existe um tempo fixo `t` de separação mínima entre dois pousos na mesma pista,

a meta é **distribuir os voos entre as pistas de forma a minimizar o custo total** (atraso ponderado por penalidade).

## Entrada

A entrada deve ser fornecida via terminal ou redirecionamento de arquivo com o seguinte formato:

```
n m t
r1 c1 p1
r2 c2 p2
...
rn cn pn
```

- `n`: número de voos
- `m`: número de pistas
- `t`: tempo mínimo entre pousos
- `ri`, `ci`, `pi`: dados do i-ésimo voo

### Exemplo:
```
5 2 3
0 5 10
2 6 8
4 8 6
3 5 12
1 4 9
```

## Funcionamento

1. **Guloso Inicial**  
   Ordena os voos por uma métrica de "prioridade" e distribui entre as pistas da forma mais adiantada possível.

2. **VND (Variable Neighborhood Descent)**  
   Aplica busca local com três tipos de movimentos:
   - Troca de voos entre pistas
   - Realocação de voo de uma pista para outra
   - Inversão da ordem de pousos em uma pista  
   A cada melhora encontrada, reinicia o processo.

## Saída

A saída será o custo total da solução e a lista de voos atribuídos a cada pista:

```
Custo final: 48
Pista 0: 0 3 4
Pista 1: 1 2
```

## Estratégias Heurísticas

- O guloso considera a **penalidade relativa à janela de tempo** para priorizar os voos mais sensíveis a atraso.
- Os movimentos de vizinhança são simples, rápidos, e combinados de forma sistemática para escapar de ótimos locais.

## Compilação

Compile com g++:
```bash
g++ -std=c++17 -O2 main.cpp -o otimizador
```

## Execução

```bash
./otimizador < entrada.txt
```

## Projeto

Projeto desenvolvido para a disciplina de Análise e Projeto de Algoritmos, 2024.2 – Prof. Lucídio Cabral.

--- --> --> -->
