"""
Módulo de dados: definição das classes de domínio do sistema.

Classes:
    Utilizador  — perfil de um utilizador da rede.
    Segmento    — segmento pedonal entre dois pontos, com indicadores ambientais e de acessibilidade.
    RedeUrbana  — grafo não-dirigido que representa a rede de percursos.
"""


class Utilizador:
    """Representa um utilizador do sistema com perfil e histórico de percursos."""

    def __init__(self, id_utilizador, nome, idade, sexo, perfil):
        """
        Inicializa um utilizador com validação básica de dados.

        Args:
            id_utilizador: Identificador único (ex: 'U00001').
            nome: Nome completo.
            idade: Idade em anos (0–120).
            sexo: 'M', 'F' ou 'OUTRO'.
            perfil: Perfil de mobilidade ('idoso', 'adulto saudável',
                    'pessoa com mobilidade reduzida').

        Raises:
            ValueError: Se a idade ou o sexo forem inválidos.
        """
        if not (0 <= idade <= 120):
            raise ValueError(f"Idade inválida ({idade}). Deve estar entre 0 e 120 anos.")
        if sexo not in ["M", "F", "OUTRO"]:
            raise ValueError(f"Sexo inválido ('{sexo}'). Use M, F ou OUTRO.")

        self._id        = id_utilizador
        self._nome      = nome
        self._idade     = idade
        self._sexo      = sexo
        self._perfil    = perfil
        self._historico = []

    # ── Getters ──────────────────────────────────────────────────────────────
    def get_id(self):       return self._id
    def get_nome(self):     return self._nome
    def get_perfil(self):   return self._perfil
    def get_idade(self):    return self._idade
    def get_sexo(self):     return self._sexo
    def get_historico(self): return self._historico

    def adicionar_historico(self, origem, destino, modo, custo):
        """Regista um percurso realizado no histórico do utilizador."""
        self._historico.append((origem, destino, modo, custo))

    def __str__(self):
        return (f"[{self._id}] {self._nome} | {self._idade} anos | "
                f"Sexo: {self._sexo} | Perfil: {self._perfil}")


# ─────────────────────────────────────────────────────────────────────────────

class Segmento:
    """
    Representa um segmento pedonal entre dois pontos da cidade,
    com indicadores ambientais e de acessibilidade.

    Nota: a inclinação pode ser negativa nos segmentos inversos (descida),
    gerados automaticamente por RedeUrbana.adicionar_segmento().
    """

    def __init__(self, origem, destino, distancia, temp, ar, ruido,
                 zonas_verdes, inclinacao, pavimento, passadeiras, iluminacao, acidente=False):
        """
        Inicializa um segmento com validação dos valores críticos.

        Args:
            origem       : Ponto de partida.
            destino      : Ponto de chegada.
            distancia    : Distância em metros (> 0).
            temp         : Temperatura em ºC.
            ar           : Qualidade do ar (0–100).
            ruido        : Nível de ruído (0–100).
            zonas_verdes : Presença de zonas verdes (0–100).
            inclinacao   : Inclinação em graus (positivo = subida, negativo = descida).
            pavimento    : 'regular' ou 'irregular'.
            passadeiras  : 'sim' ou 'não'.
            iluminacao   : 'boa', 'media' ou 'excelente'.

        Raises:
            ValueError: Se distância ≤ 0, qualidade do ar fora de [0,100],
                        ou pavimento com valor desconhecido.
        """
        if distancia <= 0:
            raise ValueError(f"Distância inválida ({distancia}). Deve ser > 0.")
        if not (0 <= ar <= 100):
            raise ValueError(f"Qualidade do ar inválida ({ar}). Deve estar entre 0 e 100.")
        if pavimento.lower() not in ["regular", "irregular"]:
            raise ValueError(f"Pavimento inválido ('{pavimento}'). Use 'regular' ou 'irregular'.")

        self._origem        = origem
        self._destino       = destino
        self._distancia     = distancia
        self._temperatura   = temp
        self._qualidade_ar  = ar
        self._ruido         = ruido
        self._zonas_verdes  = zonas_verdes
        self._inclinacao    = inclinacao
        self._pavimento     = pavimento
        self._passadeiras   = passadeiras
        self._iluminacao    = iluminacao
        self._acidente      = acidente

    # ── Getters ──────────────────────────────────────────────────────────────
    def get_origem(self):        return self._origem
    def get_destino(self):       return self._destino
    def get_distancia(self):     return self._distancia
    def get_temperatura(self):   return self._temperatura
    def get_qualidade_ar(self):  return self._qualidade_ar
    def get_ruido(self):         return self._ruido
    def get_zonas_verdes(self):  return self._zonas_verdes
    def get_inclinacao(self):    return self._inclinacao
    def get_pavimento(self):     return self._pavimento
    def get_passadeiras(self):   return self._passadeiras
    def get_iluminacao(self):    return self._iluminacao
    def get_acidente(self):      return self._acidente

    def set_acidente(self, estado):
        self._acidente = estado

    def __str__(self):
        return f"Segmento de {self._origem} para {self._destino} ({self._distancia}m)"


# ─────────────────────────────────────────────────────────────────────────────

class RedeUrbana:
    """
    Representa a rede de percursos urbanos como um grafo não-dirigido.

    Os nós são pontos da cidade e as arestas são segmentos de percurso.
    Cada segmento adicionado gera automaticamente um segmento inverso
    com inclinação negada (subida → descida).
    """

    def __init__(self):
        """Inicializa a rede com um grafo vazio (dicionário de adjacências)."""
        self._grafo = {}

    def adicionar_ponto(self, ponto):
        """Adiciona um ponto à rede se ainda não existir."""
        if ponto not in self._grafo:
            self._grafo[ponto] = []

    def adicionar_segmento(self, segmento):
        """
        Adiciona um segmento bidirecional à rede.

        O segmento inverso (destino → origem) é criado automaticamente
        com a inclinação negada: uma subida num sentido é uma descida no outro.

        Args:
            segmento: Objeto Segmento a adicionar.
        """
        origem  = segmento.get_origem()
        destino = segmento.get_destino()

        self.adicionar_ponto(origem)
        self.adicionar_ponto(destino)

        self._grafo[origem].append(segmento)

        # Segmento inverso: inclinação negada (subida → descida e vice-versa)
        segmento_inverso = Segmento(
            destino, origem,
            segmento.get_distancia(),
            segmento.get_temperatura(),
            segmento.get_qualidade_ar(),
            segmento.get_ruido(),
            segmento.get_zonas_verdes(),
            -segmento.get_inclinacao(),   # ← inversão correta
            segmento.get_pavimento(),
            segmento.get_passadeiras(),
            segmento.get_iluminacao(),
            segmento.get_acidente()
        )
        self._grafo[destino].append(segmento_inverso)

    def reportar_acidente(self, origem, destino, estado):
        """Marca ou desmarca um segmento como tendo um acidente, bloqueando o caminho."""
        marcado = False
        if origem in self._grafo:
            for seg in self._grafo[origem]:
                if seg.get_destino() == destino:
                    seg.set_acidente(estado)
                    marcado = True
        if destino in self._grafo:
            for seg in self._grafo[destino]:
                if seg.get_destino() == origem:
                    seg.set_acidente(estado)
                    marcado = True
        return marcado

    def obter_conexoes(self, ponto):
        """Retorna a lista de segmentos que partem de um dado ponto."""
        return self._grafo.get(ponto, [])

    def verificar_conectividade_sem_acidentes(self):
        """
        Verifica se a rede de transportes continua totalmente conectada 
        (todos os nós conseguem chegar a todos os outros) considerando 
        apenas as vias sem acidentes (desbloqueadas).
        """
        pontos = list(self._grafo.keys())
        if not pontos:
            return True
            
        start_node = pontos[0]
        visited = {start_node}
        queue = [start_node]
        
        while queue:
            node = queue.pop(0)
            for seg in self._grafo.get(node, []):
                if not seg.get_acidente():
                    dest = seg.get_destino()
                    if dest not in visited:
                        visited.add(dest)
                        queue.append(dest)
                        
        return len(visited) == len(pontos)

    def remover_segmento(self, origem, destino):
        """Remove um segmento bidirecional da rede (remove em ambas as direções).
        
        Args:
            origem: Ponto de partida.
            destino: Ponto de chegada.
            
        Returns:
            bool: True se removido, False se não encontrado.
        """
        removido = False
        
        if origem in self._grafo:
            original_len = len(self._grafo[origem])
            self._grafo[origem] = [s for s in self._grafo[origem] if s.get_destino() != destino]
            if len(self._grafo[origem]) < original_len:
                removido = True
        
        if destino in self._grafo:
            original_len = len(self._grafo[destino])
            self._grafo[destino] = [s for s in self._grafo[destino] if s.get_destino() != origem]
            if len(self._grafo[destino]) < original_len:
                removido = True
        
        return removido

    def contem_ponto(self, ponto):
        """Verifica se um ponto existe na rede."""
        return ponto in self._grafo

    def listar_pontos(self):
        """Retorna lista de todos os pontos da rede."""
        return list(self._grafo.keys())

    def __str__(self):
        resultado = "Rede Urbana:\n"
        for ponto, segmentos in self._grafo.items():
            destinos = ", ".join(seg.get_destino() for seg in segmentos)
            resultado += f"  - {ponto} → {destinos}\n"
        return resultado
