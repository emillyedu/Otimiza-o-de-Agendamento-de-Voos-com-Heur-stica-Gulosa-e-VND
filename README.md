# ✈️ Otimização de Agendamento de Voos com Heurística Gulosa e VND

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

---
