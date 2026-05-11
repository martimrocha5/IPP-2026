import heapq

class MotorAnalise:
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
        peso_base = segmento.get_distancia()
        peso_final = self.calcular_peso_segmento(segmento, utilizador, modo)
        
        penalizacao = peso_final - peso_base
        indice = max(0, 100 - (penalizacao / 5))
        return round(indice, 1)


class MotorRecomendacao:
    def __init__(self, motor_analise):
        self._motor = motor_analise

    def encontrar_melhor_caminho(self, rede, origem, destino, utilizador, modo="padrao"):
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
    
    def encontrar_todos_caminhos(self, rede, origem, destino, utilizador, modo="padrao"):
        todos_caminhos = []
        visitados = set()

        def dfs(nodo_atual, caminho_atual, custo_atual):
            if nodo_atual == destino:
                todos_caminhos.append((list(caminho_atual), custo_atual))
                return
            
            visitados.add(nodo_atual)
            
            for segmento in rede.obter_conexoes(nodo_atual):
                vizinho = segmento.get_destino()
                if vizinho not in visitados:
                    peso = self._motor.calcular_peso_segmento(segmento, utilizador, modo)
                    caminho_atual.append(segmento)
                    dfs(vizinho, caminho_atual, custo_atual + peso)
                    caminho_atual.pop()
            
            visitados.remove(nodo_atual)

        dfs(origem, [], 0)
        return todos_caminhos
