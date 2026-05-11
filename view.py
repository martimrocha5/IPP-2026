class View:
    @staticmethod
    def mostrar_ajuda():
        print("""
============================================================
                   COMANDOS DISPONÍVEIS
============================================================
  ins_utilizador <nome> <perfil>
      Regista um novo utilizador.
      Perfis: idoso | adulto saudável | pessoa com mobilidade reduzida

  ins_percurso <origem> <destino> <dist> <temp> <ar> <ruido>
               <verdes> <inclinacao> <pavimento> <passadeiras> <iluminacao>
      Regista um novo segmento de percurso na rede urbana.

  list percursos          Lista todos os segmentos da rede urbana.
  list utilizadores       Lista todos os utilizadores registados.

  ver <origem> <destino>  Mostra os detalhes de um segmento específico.

  recomendar <origem> <destino> <id_utilizador> [modo]
      Calcula a melhor rota para o utilizador.
      Modos: padrao | relaxar | exercicio | ar_puro

  mapa                    Mostra o mapa textual da rede urbana.

  estatisticas [cidade | utilizadores]
      Gera gráficos de análise ambiental ou dos utilizadores.

  ler <ficheiro>          Carrega utilizadores de um ficheiro JSON.
  gravar <ficheiro>       Guarda todos os utilizadores num ficheiro JSON.

  ajuda                   Mostra esta mensagem.
  sair                    Encerra o programa.
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
        ============================================================
                🗺️  REDE URBANA: BRAGA SAUDÁVEL 🗺️
        ============================================================

                             [Bom_Jesus]
                            /           \\
                           /             \\
                          /               \\
        [UMinho_Gualtar] ---- [Braga_Parque] ---- [Estacao_Comboios]
                                         \\           /
                                          \\         /
                                      [Praca_Republica]

        ============================================================
        Ligações ativas:
        - Gualtar <-> Bom Jesus        | Gualtar <-> Braga Parque
        - Braga Parque <-> Praça Rep.  | Braga Parque <-> Estação
        - Praça República <-> Estação  | Praça República <-> Bom Jesus
        ============================================================
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
    def mostrar_resultado_rota(origem, destino, utilizador, modo, caminho, custo, motor_analise):
        print(f"\n============================================================")
        print(f" ROTA RECOMENDADA: {origem} -> {destino}")
        print(f" Utilizador: {utilizador.get_nome()} |  Modo: {modo.upper()}")
        print(f"============================================================")
        
        if caminho:
            print(f" Percurso Otimizado Encontrado!")
            print(f" Custo Total (Dijkstra): {custo}")
            print("\n Itinerário Passo-a-Passo:")
            
            for i, seg in enumerate(caminho, 1):
                conforto = motor_analise.calcular_indice_conforto(seg, utilizador, modo)
                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m) [Conforto: {conforto}/100]")
            
            print("\n Destino atingido com sucesso!")
        else:
            print(f"\n Aviso: Não foi possível encontrar um caminho seguro.")
        print(f"============================================================")
