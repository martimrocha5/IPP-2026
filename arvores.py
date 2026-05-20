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
        self._tamanho = 0

    def inserir(self, utilizador):
        if self._raiz is None:
            self._raiz = NodoUtilizador(utilizador)
        else:
            self._inserir_recursivo(self._raiz, utilizador)
        self._tamanho += 1

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
        # Se o ID já existe, não insere (evita duplicados)

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

    def listar_todos(self):
        resultado = []
        self._inorder(self._raiz, resultado)
        return resultado

    def _inorder(self, nodo, resultado):
        if nodo is not None:
            self._inorder(nodo._esq, resultado)
            resultado.append(nodo.get_utilizador())
            self._inorder(nodo._dir, resultado)

    def remover(self, id_utilizador):
        """Remove um utilizador da árvore por ID.
        
        Args:
            id_utilizador: ID do utilizador a remover.
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado.
        """
        self._raiz, removido = self._remover_recursivo(self._raiz, id_utilizador)
        if removido:
            self._tamanho -= 1
        return removido

    def _remover_recursivo(self, nodo, id_utilizador):
        """Remove um nodo da árvore recursivamente."""
        if nodo is None:
            return None, False

        nodo_id = nodo.get_utilizador().get_id()

        if id_utilizador < nodo_id:
            nodo._esq, removido = self._remover_recursivo(nodo._esq, id_utilizador)
            return nodo, removido
        elif id_utilizador > nodo_id:
            nodo._dir, removido = self._remover_recursivo(nodo._dir, id_utilizador)
            return nodo, removido
        else:
            # Nodo encontrado - remover
            if nodo._esq is None:
                return nodo._dir, True
            elif nodo._dir is None:
                return nodo._esq, True
            else:
                # Nodo com dois filhos: encontrar sucessor inorder
                pai_sucessor = nodo
                sucessor = nodo._dir
                while sucessor._esq is not None:
                    pai_sucessor = sucessor
                    sucessor = sucessor._esq
                
                nodo_novo = type(nodo)(sucessor.get_utilizador())
                nodo_novo._esq = nodo._esq
                
                if pai_sucessor == nodo:
                    nodo_novo._dir, _ = self._remover_recursivo(nodo._dir, sucessor.get_utilizador().get_id())
                else:
                    pai_sucessor._esq, _ = self._remover_recursivo(pai_sucessor._esq, sucessor.get_utilizador().get_id())
                    nodo_novo._dir = nodo._dir
                
                return nodo_novo, True

    def __len__(self):
        return self._tamanho
