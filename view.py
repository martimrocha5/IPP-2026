# Vai mostrar ao utlizador o que está a acontecer

# Rubis aka Botija aka Bestie aka Apaz aka EstouFartaDeAAturar aka QueroFazerXixi aka TenhoFome aka TenhoSono

class View:
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
        - Gualtar <-> Bom Jesus | Gualtar <-> Braga Parque
        - Braga Parque <-> Arcada (Praça) | Braga Parque <-> Estação
        - Praça República <-> Estação | Praça República <-> Bom Jesus
        ============================================================
        """
        print(mapa)

    @staticmethod
    def mostrar_resultado_rota(origem, destino, nome_utilizador, modo, caminho, custo):
        print(f"\n============================================================")
        print(f" ROTA CALCULADA: {origem} -> {destino}")
        print(f" Utilizador: {nome_utilizador} |  Modo: {modo.upper()}")
        print(f"============================================================")
        
        if caminho:
            print(f" Percurso Otimizado Encontrado!")
            print(f" Índice de Custo (Penalizações): {custo}")
            
            distancia_total = sum(seg.get_distancia() for seg in caminho)
            print(f" Distância total: {distancia_total}m")

            print("\n Itinerário Passo-a-Passo:")
            for i, seg in enumerate(caminho, 1):
                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m)")
            
            print("\n Destino atingido com sucesso!")
        else:
            print(f"\n Aviso Crítico: Não foi possível encontrar um caminho seguro.")
        print(f"============================================================")

    @staticmethod
    def mostrar_detalhes_segmento(origem, destino, seg):
        if seg is not None:
            print(f"\n--- 🔍 Detalhes do Percurso: {origem} -> {destino} ---")
            print(f" Distância: {seg.get_distancia()}m")
            print(f" Ambiente -> Temp: {seg.get_temperatura()}ºC | Ar: {seg.get_qualidade_ar()} | Ruído: {seg.get_ruido()} | Verdes: {seg.get_zonas_verdes()}")
            print(f" Acessibilidade -> Inclinação: {seg.get_inclinacao()} | Pavimento: {seg.get_pavimento()} | Passadeiras: {seg.get_passadeiras()}")
            print("--------------------------------------------------")
        else:
            print(f"\n Aviso: Não existe um segmento direto registado entre '{origem}' e '{destino}'.")