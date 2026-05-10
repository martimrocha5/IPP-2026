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
    def mostrar_resultado_rota(origem, destino, nome_utilizador, modo, caminho, custo):
        print(f"\n{'='*60}")
        print(f" ROTA CALCULADA: {origem} -> {destino}")
        print(f" Utilizador: {nome_utilizador} |  Modo: {modo.upper()}")
        print(f"{'='*60}")

        if caminho:
            print(f" Percurso Otimizado Encontrado!")
            print(f" Índice de Custo (com penalizações): {custo:.1f}")

            distancia_total = sum(seg.get_distancia() for seg in caminho)
            print(f" Distância total: {distancia_total}m")

            print("\n Itinerário Passo-a-Passo:")
            for i, seg in enumerate(caminho, 1):
                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m)")

            print("\n Destino atingido com sucesso! 🏁")
        else:
            print(f"\n Aviso Crítico: Não foi possível encontrar um caminho seguro entre '{origem}' e '{destino}'.")

        print(f"{'='*60}")

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
