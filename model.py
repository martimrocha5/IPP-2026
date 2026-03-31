class MotorAnalise:
    def __init__(self):
        self._regras_perfil = {
            "idoso": {"inclinacao": 4, "ruido": 2},
            "pessoa com mobilidade reduzida": {"inclinacao": 6, "pavimento_irregular": 50},
            "adulto saudável": {"zonas_verdes": -2}
        }
        
        self._regras_modo = {
            "padrao": {},
            "relaxar": {"zonas_verdes": -3, "ruido": 4},
            "exercicio": {"inclinacao": -2, "distancia_mult": -0.5},
            "ar_puro": {"qualidade_ar": 5}
        }

    def calcular_peso_segmento(self, segmento, utilizador, modo="padrao"):
        peso_base = segmento.get_distancia()
        penalizacao = 0
        perfil = utilizador.get_perfil().lower()

        if perfil in self._regras_perfil:
            regras = self._regras_perfil[perfil]
            penalizacao += segmento.get_inclinacao() * regras.get("inclinacao", 0)
            penalizacao += segmento.get_ruido() * regras.get("ruido", 0)
            penalizacao += segmento.get_zonas_verdes() * regras.get("zonas_verdes", 0)
            
            if segmento.get_pavimento().lower() == "irregular":
                penalizacao += regras.get("pavimento_irregular", 0)

        if modo in self._regras_modo:
            regras_m = self._regras_modo[modo]
            penalizacao += segmento.get_zonas_verdes() * regras_m.get("zonas_verdes", 0)
            penalizacao += segmento.get_ruido() * regras_m.get("ruido", 0)
            penalizacao += segmento.get_inclinacao() * regras_m.get("inclinacao", 0)
            penalizacao += segmento.get_qualidade_ar() * regras_m.get("qualidade_ar", 0)
            penalizacao += peso_base * regras_m.get("distancia_mult", 0)

        peso_final = peso_base + penalizacao
        return max(1, peso_final)