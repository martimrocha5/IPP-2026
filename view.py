class View:
    """Interface de visualização para o sistema de recomendação de percursos."""
    
    ITENS_POR_PAGINA = 10  # Limite de itens por página
    @staticmethod
    def mostrar_ajuda():
        print("""
============================================================
                   COMANDOS DISPONÍVEIS
============================================================
DADOS:
  ins_utilizador <nome> <idade> <sexo> <perfil>
      Regista um novo utilizador.
      Perfis: idoso | pessoa com mobilidade reduzida | adulto saudável

  ins_percurso <origem> <destino> <dist> <temp> <ar> <ruido>
               <verdes> <inclinacao> <pav> <passadeiras> <ilum>
      Regista um novo segmento de percurso.

  list percursos [pagina]        Lista percursos com paginação (10/página)
  list utilizadores [pagina]     Lista utilizadores com paginação

CONSULTA:
  ver <origem> <destino>         Mostra detalhes de um segmento
  procurar <id_utilizador>       Mostra perfil de utilizador
  historico <id_utilizador>      Mostra histórico de percursos

RECOMENDAÇÃO:
  recomendar <origem> <destino> <id_utilizador> [modo] [acompanhante]
      Calcula a melhor rota para o utilizador.
      Modos: padrao | relaxar | exercicio | ar_puro | trabalho
      Acompanhantes: Cadeira de Rodas | Carrinho de Bebé | Andarilho | Carrinho de Mão | Carrinho de Compras | Mala com Rodas

VISUALIZAÇÃO:
  mapa                           Mostra mapa textual da rede
  estatisticas                   Gera gráficos ambientais
  analise_utilizadores           Análise dos utilizadores

FICHEIROS:
  gravar <ficheiro>              Grava dados em JSON
  ler <ficheiro>                 Carrega dados de JSON

SISTEMA:
  ajuda                          Mostra esta mensagem
  sair                           Encerra o programa
============================================================
""")

    @staticmethod
    def mostrar_boas_vindas(total_users):
        print("\n============================================================")
        print("    SISTEMA INICIADO: REDE BRAGA SAUDÁVEL ")
        print(f"   Utilizadores Carregados: {total_users}")
        print("    Malha Urbana Otimizada")
        print("============================================================\n")

    @staticmethod
    def mostrar_mapa():
        mapa = """
         ========================================================================
                      🗺️   REDE URBANA: BRAGA SAUDÁVEL (EXPANDIDA) 🗺️
         ========================================================================
         
                             [Estadio_Municipal]
                                 /          \\
                                /            \\
                     [Estacao_Comboios]    [Jardim_Santa_Barbara]
                        /      |     \\       /       \\
                       /       |      \\     /         \\
                      /        |     [Praca_Republica] ---- [Braga_Parque] ---- [UMinho_Gualtar]
               [Se_Braga]      |      /    |     \\       /     /          /
                  \\   \\        |     /     |      \\     /     /          /
                   \\   \\-------|----/      |       \\   /     /          /
                    \\          |           |      [Hospital_Braga]-----/
                  [Avenida_Liberdade]      |             /
                          \\                |            /
                           \\               |           /
                   [Santuario_Sameiro] ----------- [Bom_Jesus]
                   
         ========================================================================
         Pontos da Rede e suas principais conexões:
         - Estadio_Municipal    <-> Estacao_Comboios, Praca_Republica
         - Estacao_Comboios     <-> Estadio_Municipal, Se_Braga, Praca_Republica, Braga_Parque
         - Se_Braga             <-> Estacao_Comboios, Jardim_Santa_Barbara, Avenida_Liberdade
         - Jardim_Santa_Barbara  <-> Se_Braga, Praca_Republica
         - Praca_Republica      <-> Jardim_Santa_Barbara, Avenida_Liberdade, Estacao_Comboios, 
                                    Estadio_Municipal, Braga_Parque, Hospital_Braga, Bom_Jesus
         - Avenida_Liberdade    <-> Praca_Republica, Se_Braga, Santuario_Sameiro
         - Santuario_Sameiro    <-> Avenida_Liberdade, Bom_Jesus
         - Bom_Jesus            <-> Santuario_Sameiro, Hospital_Braga, Praca_Republica, UMinho_Gualtar
         - Hospital_Braga       <-> UMinho_Gualtar, Braga_Parque, Bom_Jesus, Praca_Republica
         - UMinho_Gualtar       <-> Hospital_Braga, Braga_Parque, Bom_Jesus
         - Braga_Parque         <-> UMinho_Gualtar, Hospital_Braga, Praca_Republica, Estacao_Comboios
         ========================================================================
        """
        print(mapa)



    @staticmethod
    def mostrar_detalhes_segmento(origem, destino, seg):
        if seg is not None:
            print(f"\n--- Detalhes do Percurso: {origem} -> {destino} ---")
            print(f" Distância   : {seg.get_distancia()}m")
            print(f" Ambiente    -> Temp: {seg.get_temperatura()}ºC | "
                  f"Ar: {seg.get_qualidade_ar()} | "
                  f"Ruído: {seg.get_ruido()} | "
                  f"Zonas Verdes: {seg.get_zonas_verdes()}")
            print(f" Acessibilidade -> Inclinação: {seg.get_inclinacao()}° | "
                  f"Pavimento: {seg.get_pavimento()} | "
                  f"Passadeiras: {seg.get_passadeiras()} | "
                  f"Iluminação: {seg.get_iluminacao()}")
            print("-" * 50)
        else:
            print(f"\n Aviso: Não existe segmento direto registado entre '{origem}' e '{destino}'.")

    @staticmethod
    def mostrar_historico(utilizador):
        historico = utilizador.get_historico()
        print(f"\n---  Histórico de: {utilizador.get_nome()} ---")
        if not historico:
            print("Nenhum percurso registado até ao momento.")
        else:
            for i, (origem, destino, modo, custo) in enumerate(historico, 1):
                print(f" {i}. {origem} -> {destino} | Modo: {modo.upper()} | Custo: {custo}")
        print("--------------------------------------------------")

    @staticmethod
    def mostrar_perfil(utilizador):
        print(f"\n---  Detalhes do Perfil ---")
        print(f"ID: {utilizador.get_id()}")
        print(f"Nome: {utilizador.get_nome()}")
        print(f"Idade: {utilizador.get_idade()} anos")
        print(f"Sexo: {utilizador.get_sexo()}")
        print(f"Condição: {utilizador.get_perfil()}")
        print("-----------------------------")

    @staticmethod
    def mostrar_resultado_rota(origem, destino, utilizador, modo, caminho, custo, motor_analise, acompanhante="Nenhum", clima="Sol"):
        print(f"\n============================================================")
        print(f" ROTA RECOMENDADA: {origem} -> {destino}")
        print(f" Utilizador: {utilizador.get_nome()} |  Modo: {modo.upper()}")
        print(f"============================================================")
        
        if caminho:
            print(f" Percurso Otimizado Encontrado!")
            print(f" Custo Total (Dijkstra): {custo}")
            print("\n Itinerário Passo-a-Passo:")
            
            for i, seg in enumerate(caminho, 1):
                conforto = motor_analise.calcular_indice_conforto(seg, utilizador, modo, acompanhante, clima)
                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m) [Conforto: {conforto}/100]")
            
            print("\n Destino atingido com sucesso!")
        else:
            print(f"\n Aviso: Não foi possível encontrar um caminho seguro.")
        print(f"============================================================")

    @staticmethod
    def listar_percursos_paginado(rede, pagina=1):
        """Lista segmentos de rua com paginação."""
        ruas_vistas = set()
        percursos = []
        
        for origem, conexoes in rede._grafo.items():
            for seg in conexoes:
                destino = seg.get_destino()
                id_rua = tuple(sorted([origem, destino]))
                
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    percursos.append(seg)
        
        if not percursos:
            print("Nenhum percurso registado.")
            return
        
        total_paginas = (len(percursos) + View.ITENS_POR_PAGINA - 1) // View.ITENS_POR_PAGINA
        
        if pagina < 1 or pagina > total_paginas:
            print(f"✗ Página inválida. Total de páginas: {total_paginas}")
            return
        
        inicio = (pagina - 1) * View.ITENS_POR_PAGINA
        fim = min(inicio + View.ITENS_POR_PAGINA, len(percursos))
        
        print("\n" + "="*70)
        print(f"LISTA DE PERCURSOS (Página {pagina}/{total_paginas})")
        print("="*70)
        
        for i, seg in enumerate(percursos[inicio:fim], start=inicio+1):
            print(f"\n{i}. {seg.get_origem()} → {seg.get_destino()}")
            print(f"   Distância: {seg.get_distancia()}m")
            print(f"   Ambiente: Temp {seg.get_temperatura()}ºC | Ar {seg.get_qualidade_ar()} | Ruído {seg.get_ruido()}")
            print(f"   Acessibilidade: Inclinação {seg.get_inclinacao()}° | Pavimento {seg.get_pavimento()}")
        
        print("\n" + "="*70)
        if pagina < total_paginas:
            print(f"Use: list percursos {pagina+1} para próxima página")
        if pagina > 1:
            print(f"Use: list percursos {pagina-1} para página anterior")
        print("="*70)

    @staticmethod
    def listar_utilizadores_paginado(arvore, pagina=1):
        """Lista utilizadores com paginação."""
        todos = arvore.listar_todos()
        
        if not todos:
            print("Nenhum utilizador registado.")
            return
        
        total_paginas = (len(todos) + View.ITENS_POR_PAGINA - 1) // View.ITENS_POR_PAGINA
        
        if pagina < 1 or pagina > total_paginas:
            print(f"✗ Página inválida. Total de páginas: {total_paginas}")
            return
        
        inicio = (pagina - 1) * View.ITENS_POR_PAGINA
        fim = min(inicio + View.ITENS_POR_PAGINA, len(todos))
        
        print("\n" + "="*70)
        print(f"LISTA DE UTILIZADORES (Página {pagina}/{total_paginas} - Total: {len(todos)})")
        print("="*70)
        
        for i, user in enumerate(todos[inicio:fim], start=inicio+1):
            print(f"{i}. {user}")
        
        print("\n" + "="*70)
        if pagina < total_paginas:
            print(f"Use: list utilizadores {pagina+1} para próxima página")
        if pagina > 1:
            print(f"Use: list utilizadores {pagina-1} para página anterior")
        print("="*70)

