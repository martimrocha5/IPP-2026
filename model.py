import heapq

class MotorAnalise:
    """Motor de análise para cálculo de índices de conforto baseados em variáveis ambientais e de acessibilidade.
    
    Aplica penalizações e valorizações conforme o perfil do utilizador e modo de deslocação escolhido.
    """
    
    def __init__(self):

        self._regras_perfil = {
            "idoso": {
                "inclinacao": 4,   
                "ruido": 2         
            },
            "pessoa com mobilidade reduzida": {
                "inclinacao": 6,          
                "pavimento_irregular": 50  
            },
            "adulto saudável": {
                "zonas_verdes": -2  
            }
        }

        self._regras_modo = {
            "padrao":    {},
            "relaxar":   {"zonas_verdes": -3, "ruido": 4},
            "exercicio": {"inclinacao": -2, "distancia_mult": -0.5},
            "ar_puro":   {"qualidade_ar": 5}
        }

    def calcular_peso_segmento(self, segmento, utilizador, modo="padrao"):
        """Calcula o peso de um segmento aplicando penalizações conforme o perfil e modo.
        
        Args:
            segmento: Segmento de rua
            utilizador: Utilizador (perfil influencia cálculo)
            modo: Modo de deslocação (padrao, relaxar, exercicio, ar_puro)
            
        Returns:
            float: Peso final do segmento (distância + penalizações)
        """
        peso_base = segmento.get_distancia()
        penalizacao = 0
        perfil = utilizador.get_perfil().lower()

        if perfil in self._regras_perfil:
            regras = self._regras_perfil[perfil]
            penalizacao += segmento.get_inclinacao()   * regras.get("inclinacao", 0)
            penalizacao += segmento.get_ruido()        * regras.get("ruido", 0)
            penalizacao += segmento.get_zonas_verdes() * regras.get("zonas_verdes", 0)

            if segmento.get_pavimento().lower() == "irregular":
                penalizacao += regras.get("pavimento_irregular", 0)

        if modo in self._regras_modo:
            regras_m = self._regras_modo[modo]
            penalizacao += segmento.get_zonas_verdes() * regras_m.get("zonas_verdes", 0)
            penalizacao += segmento.get_ruido()        * regras_m.get("ruido", 0)
            penalizacao += segmento.get_inclinacao()   * regras_m.get("inclinacao", 0)
            penalizacao += segmento.get_qualidade_ar() * regras_m.get("qualidade_ar", 0)
            penalizacao += peso_base                   * regras_m.get("distancia_mult", 0)

        peso_final = peso_base + penalizacao
        return max(1, peso_final)  
    
    def calcular_indice_conforto(self, segmento, utilizador, modo="padrao"):
        """Calcula um índice de conforto (0-100) para um segmento.
        
        Args:
            segmento: Segmento de rua
            utilizador: Utilizador
            modo: Modo de deslocação
            
        Returns:
            float: Índice de conforto (0-100)
        """
        peso_base = segmento.get_distancia()
        peso_final = self.calcular_peso_segmento(segmento, utilizador, modo)
        
        penalizacao = peso_final - peso_base
        indice = max(0, 100 - (penalizacao / 5))
        return round(indice, 1)


class MotorRecomendacao:
    """Motor de recomendação de percursos usando algoritmos Dijkstra e DFS.
    
    Encontra a melhor rota ou múltiplas alternativas entre dois pontos na rede urbana.
    """
    
    def __init__(self, motor_analise):
        self._motor = motor_analise

    def encontrar_melhor_caminho(self, rede, origem, destino, utilizador, modo="padrao"):
        """Encontra o melhor caminho usando algoritmo Dijkstra.
        
        Args:
            rede: RedeUrbana
            origem: Ponto inicial
            destino: Ponto final
            utilizador: Utilizador (influencia cálculo de peso)
            modo: Modo de deslocação
            
        Returns:
            tuple: (caminho, custo) ou (None, inf) se não houver caminho
        """
        distancias = {origem: 0}
        caminhos = {origem: []}
        fila_prioridade = [(0, origem)]
        visitados = set()

        while fila_prioridade:
            custo_atual, nodo_atual = heapq.heappop(fila_prioridade)

            if nodo_atual in visitados:
                continue
            visitados.add(nodo_atual)

            if nodo_atual == destino:
                return caminhos[destino], custo_atual

            for segmento in rede.obter_conexoes(nodo_atual):
                vizinho = segmento.get_destino()
                if vizinho in visitados:
                    continue

                peso_segmento = self._motor.calcular_peso_segmento(segmento, utilizador, modo)
                novo_custo = custo_atual + peso_segmento

                if vizinho not in distancias or novo_custo < distancias[vizinho]:
                    distancias[vizinho] = novo_custo
                    caminhos[vizinho] = list(caminhos[nodo_atual]) + [segmento]
                    heapq.heappush(fila_prioridade, (novo_custo, vizinho))

        return None, float('inf')
    
    def encontrar_todos_caminhos(self, rede, origem, destino, utilizador, modo="padrao", max_caminhos=10):
        """Encontra múltiplos caminhos entre origem e destino usando DFS com limite.
        
        Args:
            rede: RedeUrbana
            origem: Ponto inicial
            destino: Ponto final
            utilizador: Utilizador para cálculo de peso
            modo: Modo de deslocação (padrao, relaxar, exercicio, ar_puro)
            max_caminhos: Limite de caminhos a encontrar (evita busca infinita)
            
        Returns:
            Lista de tuplos (caminho, custo)
        """
        todos_caminhos = []
        
        def dfs(nodo_atual, caminho_atual, custo_atual, visitados_locais):
            # Limite de caminhos encontrados
            if len(todos_caminhos) >= max_caminhos:
                return
                
            if nodo_atual == destino:
                todos_caminhos.append((list(caminho_atual), custo_atual))
                return
            
            # Adicionar à lista local para esta recursão
            visitados_locais.add(nodo_atual)
            
            for segmento in rede.obter_conexoes(nodo_atual):
                vizinho = segmento.get_destino()
                if vizinho not in visitados_locais:
                    peso = self._motor.calcular_peso_segmento(segmento, utilizador, modo)
                    caminho_atual.append(segmento)
                    dfs(vizinho, caminho_atual, custo_atual + peso, visitados_locais.copy())
                    caminho_atual.pop()
            
            visitados_locais.discard(nodo_atual)

        dfs(origem, [], 0, set())
        return sorted(todos_caminhos, key=lambda x: x[1])  # Ordena por custo
