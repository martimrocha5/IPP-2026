class NodoUtilizador:
    def __init__(self, utilizador):
        self._utilizador = utilizador
        self._esq = None
        self._dir = None

    def get_utilizador(self):
        return self._utilizador

class ArvoreUtilizadores:
    def __init__(self):
        self._raiz = None

    def inserir(self, utilizador):
        if self._raiz is None:
            self._raiz = NodoUtilizador(utilizador)
        else:
            self._inserir_recursivo(self._raiz, utilizador)

    def _inserir_recursivo(self, nodo, utilizador):

        if utilizador.get_id() < nodo.get_utilizador().get_id():
            if nodo._esq is None:
                nodo._esq = NodoUtilizador(utilizador)
            else:
                self._inserir_recursivo(nodo._esq, utilizador)
        elif utilizador.get_id() > nodo.get_utilizador().get_id():
            if nodo._dir is None:
                nodo._dir = NodoUtilizador(utilizador)
            else:
                self._inserir_recursivo(nodo._dir, utilizador)

    def procurar(self, id_utilizador):
        return self._procurar_recursivo(self._raiz, id_utilizador)

    def _procurar_recursivo(self, nodo, id_utilizador):
        if nodo is None:
            return None
        
        nodo_id = nodo.get_utilizador().get_id()
        
        if id_utilizador == nodo_id:
            return nodo.get_utilizador()
        elif id_utilizador < nodo_id:
            return self._procurar_recursivo(nodo._esq, id_utilizador)
        else:
            return self._procurar_recursivo(nodo._dir, id_utilizador)