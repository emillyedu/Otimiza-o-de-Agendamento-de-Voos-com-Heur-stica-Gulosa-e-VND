// Projeto de Otimização de Pousos com Heurística Gulosa e VND Aprimorado
#include <iostream>
#include <vector>
#include <fstream>
#include <algorithm>
#include <tuple>
#include <random>

using namespace std;

// Estrutura que representa um voo
struct Voo {
    int id; // Identificador do voo
    int r;  // Tempo mais cedo em que o voo pode pousar (release time)
    int c;  // Tempo ideal de pouso (target time)
    int p;  // Penalidade por unidade de tempo de atraso
};

// Estrutura que representa uma pista de pouso
struct Pista {
    vector<int> voos;         // Lista de IDs dos voos alocados nesta pista
    int tempo_disponivel = 0; // Próximo tempo disponível para pouso na pista
};



// Calcula o custo de pousar um voo em um determinado horário
//custo só existe se o voo pousar depois do fim da janela (c). 
//Se pousar antes ou exatamente no tempo c, o custo é zero.
int calcular_custo_voo(int inicio, int c, int p) {
    // Se o voo pousar após o tempo ideal, calcula o atraso vezes a penalidade
    return max(0, inicio - c) * p;
}

// Calcula o custo total da solução (soma dos custos de todos os voos em todas as pistas)
int calcular_custo_total(const vector<Pista>& pistas, const vector<Voo>& voos, int t) {
    int total = 0; // Inicializa o custo total com zero

    // Para cada pista
    for (const auto& pista : pistas) {
        int tempo = 0; // Tempo atual na pista

        // Para cada voo alocado na pista
        for (int id : pista.voos) {
            // Determina o tempo de pouso: o maior entre o tempo atual e o release time do voo
            int inicio = max(tempo, voos[id].r);

            // Soma o custo de atraso desse voo ao custo total
            total += calcular_custo_voo(inicio, voos[id].c, voos[id].p);

            // Atualiza o tempo na pista considerando o intervalo obrigatório entre pousos
            tempo = inicio + t;
        }
    }

    // Retorna o custo total calculado
    return total;
}

// Função de comparação para ordenar os voos com base em sua prioridade
// A prioridade é medida pela penalidade dividida pela largura da janela (c - r)
bool comparar_voo_prioridade(const Voo& a, const Voo& b) {
    // Calcula a prioridade do voo 'a'. Usa max(1, ...) para evitar divisão por zero
    double prioridade_a = static_cast<double>(a.p) / max(1, a.c - a.r);
    
    // Calcula a prioridade do voo 'b'
    double prioridade_b = static_cast<double>(b.p) / max(1, b.c - b.r);
    
    // Retorna true se 'a' tiver maior prioridade que 'b'
    return prioridade_a > prioridade_b;
}

// Heurística gulosa para alocar voos nas pistas
vector<Pista> guloso(const vector<Voo>& voos, int num_pistas, int t) {
    // Inicializa um vetor com o número de pistas fornecido
    vector<Pista> pistas(num_pistas);
    
    // Cria uma cópia dos voos para ordenação
    auto ordenado = voos;
    
    // Ordena os voos com base na prioridade (do mais urgente para o menos)
    sort(ordenado.begin(), ordenado.end(), comparar_voo_prioridade);
    
    // Aloca os voos um a um
    for (const auto& voo : ordenado) {
        int melhor_tempo = INT32_MAX; // Menor tempo encontrado até agora
        int melhor_pista = -1;        // Índice da melhor pista

        // Verifica cada pista para encontrar onde o voo pode pousar mais cedo
        for (int i = 0; i < num_pistas; i++) {
            // O voo pode pousar no máximo entre o tempo disponível da pista e seu release time
            int tempo = max(pistas[i].tempo_disponivel, voo.r);

            // Se essa pista permitir pousar mais cedo, atualiza a escolha
            if (tempo < melhor_tempo) {
                melhor_tempo = tempo;
                melhor_pista = i;
            }
        }

        // Atribui o voo à melhor pista encontrada
        pistas[melhor_pista].voos.push_back(voo.id);

        // Atualiza o tempo disponível da pista após o pouso desse voo
        pistas[melhor_pista].tempo_disponivel = melhor_tempo + t;
    }

    // Retorna a alocação final dos voos nas pistas
    return pistas;
}


// Movimento 1: Troca simples entre dois voos de pistas diferentes
bool troca_simples(vector<Pista>& pistas) {
    // Percorre todas as combinações de pares de pistas (i, j)
    for (int i = 0; i < pistas.size(); i++) {
        for (int j = i + 1; j < pistas.size(); j++) {
            // Garante que ambas as pistas tenham pelo menos um voo para trocar
            if (!pistas[i].voos.empty() && !pistas[j].voos.empty()) {
                // Escolhe o voo do meio da pista i
                int idx_i = pistas[i].voos.size() / 2;

                // Escolhe o voo do meio da pista j
                int idx_j = pistas[j].voos.size() / 2;

                // Troca os voos entre as pistas
                swap(pistas[i].voos[idx_i], pistas[j].voos[idx_j]);

                // Retorna true indicando que uma troca foi feita
                return true;
            }
        }
    }
    // Se nenhuma troca foi possível, retorna false
    return false;
}


// Movimento 2: Move um voo da frente de uma pista para o final de outra
bool mover_voo(vector<Pista>& pistas) {
    // Percorre todos os pares de pistas (i, j), incluindo todas as combinações possíveis
    for (int i = 0; i < pistas.size(); i++) {
        for (int j = 0; j < pistas.size(); j++) {
            // Evita mover para a mesma pista e garante que a origem tenha voos
            if (i != j && !pistas[i].voos.empty()) {
                // Pega o primeiro voo da pista i
                int voo = pistas[i].voos.front();

                // Remove esse voo da pista i
                pistas[i].voos.erase(pistas[i].voos.begin());

                // Adiciona o voo ao final da pista j
                pistas[j].voos.push_back(voo);

                // Retorna true indicando que o movimento foi realizado
                return true;
            }
        }
    }
    // Se nenhum movimento foi possível, retorna false
    return false;
}

// Movimento 3: Inverte a ordem dos voos em uma das pistas
bool inverter_pista(vector<Pista>& pistas) {
    // Percorre todas as pistas
    for (auto& pista : pistas) {
        // Verifica se a pista tem mais de um voo (senão não faz sentido inverter)
        if (pista.voos.size() > 1) {
            // Inverte a ordem dos voos nessa pista
            reverse(pista.voos.begin(), pista.voos.end());

            // Retorna true indicando que o movimento foi feito
            return true;
        }
    }
    // Se nenhuma inversão foi possível, retorna false
    return false;
}

// Aplica um dos três movimentos de vizinhança, baseado no tipo passado
bool aplicar_vizinhanca(vector<Pista>& pistas, int tipo) {
    switch (tipo) {
        // tipo 0: faz troca simples
        case 0: return troca_simples(pistas);

        // tipo 1: move um voo entre pistas
        case 1: return mover_voo(pistas);

        // tipo 2: inverte uma pista
        case 2: return inverter_pista(pistas);

        // tipo inválido: não faz nada
        default: return false;
    }
}

// Função que aplica o VND (Variable Neighborhood Descent) para melhorar a solução
vector<Pista> VND(vector<Pista> pistas, const vector<Voo>& voos, int t) {
    // Começa com a primeira vizinhança (k = 0)
    int k = 0;

    // Calcula o custo atual da solução
    int custo_atual = calcular_custo_total(pistas, voos, t);

    // Enquanto não tiver testado todas as 3 vizinhanças
    while (k < 3) {
        // Cria uma cópia da solução atual para testar a vizinhança
        auto pistas_temp = pistas;

        // Tenta aplicar a vizinhança k
        if (aplicar_vizinhanca(pistas_temp, k)) {

            // Calcula o custo da nova solução
            int novo_custo = calcular_custo_total(pistas_temp, voos, t);

            // Se a nova solução for melhor
            if (novo_custo < custo_atual) {
                // Atualiza a solução principal
                pistas = pistas_temp;
                custo_atual = novo_custo;

                // Volta a testar a primeira vizinhança
                k = 0;
            } else {
                // Senão, tenta a próxima vizinhança
                k++;
            }
        } else {
            // Se o movimento da vizinhança não foi possível, pula pra próxima
            k++;
        }
    }

    // Retorna a melhor solução encontrada
    return pistas;
}


int main() {
    // Declara as variáveis: número de voos (n), tempo mínimo entre pousos (t), e número de pistas
    int n, t, num_pistas;

    // Lê esses valores da entrada padrão
    cin >> n >> num_pistas >> t;

    // Cria um vetor para armazenar os voos
    vector<Voo> voos(n);

    // Lê os dados de cada voo: r (início da janela), c (fim da janela), p (penalidade)
    for (int i = 0; i < n; ++i) {
        cin >> voos[i].r >> voos[i].c >> voos[i].p;
        voos[i].id = i;  // Atribui um ID único para cada voo (posição no vetor)
    }

    // Gera uma solução inicial usando o algoritmo guloso
    auto pistas_iniciais = guloso(voos, num_pistas, t);

    // Aplica o VND para tentar melhorar a solução inicial
    auto pistas_final = VND(pistas_iniciais, voos, t);

    // Calcula o custo total da solução final (depois do VND)
    int custo_final = calcular_custo_total(pistas_final, voos, t);

    // Imprime o custo total da solução final
    cout << "Custo final: " << custo_final << endl;

    // Para cada pista, imprime os IDs dos voos alocados nela
    for (int i = 0; i < pistas_final.size(); ++i) {
        cout << "Pista " << i << ": ";
        for (int id : pistas_final[i].voos) {
            cout << id << " ";
        }
        cout << endl;
    }

    // Fim do programa
    return 0;
}
