class Utilizador:
    def __init__(self, id_utilizador, nome, idade, sexo, perfil):
        self._id = id_utilizador
        self._nome = nome
        self._idade = idade
        self._sexo = sexo
        self._perfil = perfil
        self._historico = []

    def get_id(self):
        return self._id

    def get_nome(self):
        return self._nome
        
    def get_perfil(self):
        return self._perfil

    def get_idade(self):
        return self._idade
        
    def get_sexo(self):
        return self._sexo

    def adicionar_historico(self, origem, destino, modo, custo):
        self._historico.append((origem, destino, modo, custo))

    def get_historico(self):
        return self._historico

    def __str__(self):
        return f"[{self._id}] {self._nome} | {self._idade} anos | Sexo: {self._sexo} | Perfil: {self._perfil}"

class Segmento:
    def __init__(self, origem, destino, distancia, temp, ar, ruido, zonas_verdes, inclinacao, pavimento, passadeiras, iluminacao):
        self._origem = origem
        self._destino = destino
        self._distancia = distancia
        self._temperatura = temp
        self._qualidade_ar = ar
        self._ruido = ruido
        self._zonas_verdes = zonas_verdes
        self._inclinacao = inclinacao
        self._pavimento = pavimento
        self._passadeiras = passadeiras
        self._iluminacao = iluminacao

    def get_origem(self):
        return self._origem

    def get_destino(self):
        return self._destino

    def get_distancia(self):
        return self._distancia

    def get_temperatura(self):
        return self._temperatura

    def get_qualidade_ar(self):
        return self._qualidade_ar

    def get_ruido(self):
        return self._ruido

    def get_zonas_verdes(self):
        return self._zonas_verdes

    def get_inclinacao(self):
        return self._inclinacao

    def get_pavimento(self):
        return self._pavimento

    def get_passadeiras(self):
        return self._passadeiras

    def get_iluminacao(self):
        return self._iluminacao

    def __str__(self):
        return f"Segmento de {self._origem} para {self._destino} ({self._distancia}m)"


class RedeUrbana:
    def __init__(self):
        self._grafo = {}

    def adicionar_ponto(self, ponto):
        if ponto not in self._grafo:
            self._grafo[ponto] = []

    def adicionar_segmento(self, segmento):
        origem = segmento.get_origem()
        destino = segmento.get_destino()

        self.adicionar_ponto(origem)
        self.adicionar_ponto(destino)

        self._grafo[origem].append(segmento)

        segmento_inverso = Segmento(
            destino,
            origem,
            segmento.get_distancia(),
            segmento.get_temperatura(),
            segmento.get_qualidade_ar(),
            segmento.get_ruido(),
            segmento.get_zonas_verdes(),
            0 if segmento.get_inclinacao() > 0 else segmento.get_inclinacao(),
            segmento.get_pavimento(),
            segmento.get_passadeiras(),
            segmento.get_iluminacao()
        )
        self._grafo[destino].append(segmento_inverso)

    def obter_conexoes(self, ponto):
        return self._grafo.get(ponto, [])

    def __str__(self):
        resultado = "Rede Urbana:\n"
        for ponto, segmentos in self._grafo.items():
            resultado += f"- {ponto} liga a: {', '.join([seg.get_destino() for seg in segmentos])}\n"
        return resultado
