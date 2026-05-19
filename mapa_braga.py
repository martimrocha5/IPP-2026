from dados import Segmento

def carregar_mapa_expandido(rede):
    """
    Adiciona novos segmentos da cidade de Braga à rede urbana existente.
    Estes pontos representam locais reais e conhecidos, com indicadores 
    ambientais e de acessibilidade aproximados.
    """
    segmentos_novos = [
        # Praca_Republica <-> Jardim_Santa_Barbara
        Segmento("Praca_Republica", "Jardim_Santa_Barbara", 400, 22, 60, 50, 85, 0, "regular", "sim", "boa"),
        
        # Jardim_Santa_Barbara <-> Se_Braga
        Segmento("Jardim_Santa_Barbara", "Se_Braga", 300, 21, 55, 45, 10, 0, "irregular", "não", "boa"),
        
        # Praca_Republica <-> Avenida_Liberdade
        Segmento("Praca_Republica", "Avenida_Liberdade", 600, 22, 40, 80, 30, 1, "regular", "sim", "excelente"),
        
        # Avenida_Liberdade <-> Se_Braga
        Segmento("Avenida_Liberdade", "Se_Braga", 700, 21, 45, 70, 5, 2, "irregular", "sim", "boa"),

        # UMinho_Gualtar <-> Hospital_Braga
        Segmento("UMinho_Gualtar", "Hospital_Braga", 1500, 19, 80, 40, 50, 5, "regular", "sim", "boa"),
        
        # Braga_Parque <-> Hospital_Braga
        Segmento("Braga_Parque", "Hospital_Braga", 2000, 19, 70, 55, 30, 6, "regular", "sim", "media"),

        # Bom_Jesus <-> Santuario_Sameiro
        Segmento("Bom_Jesus", "Santuario_Sameiro", 2500, 16, 98, 15, 95, 12, "regular", "não", "media"),

        # Hospital_Braga <-> Bom_Jesus (Ligação de Reforço via Tenões)
        Segmento("Hospital_Braga", "Bom_Jesus", 3000, 18, 75, 45, 40, 4, "regular", "sim", "boa"),

        # Hospital_Braga <-> Praca_Republica (Ligação Direta via Av. João Paulo II)
        Segmento("Hospital_Braga", "Praca_Republica", 2500, 20, 60, 60, 30, 2, "regular", "sim", "media"),

        # Santuario_Sameiro <-> Avenida_Liberdade (Ligação Alternativa via Falperra)
        Segmento("Santuario_Sameiro", "Avenida_Liberdade", 4000, 15, 95, 20, 90, 8, "regular", "não", "media"),

        # Estacao_Comboios <-> Se_Braga (Eixo Pedonal do Centro Histórico)
        Segmento("Estacao_Comboios", "Se_Braga", 800, 21, 50, 80, 15, 0, "irregular", "sim", "excelente"),
        
        # Estacao_Comboios <-> Estadio_Municipal
        Segmento("Estacao_Comboios", "Estadio_Municipal", 3000, 20, 65, 50, 40, -2, "regular", "sim", "boa"),
        
        # Praca_Republica <-> Estadio_Municipal
        Segmento("Praca_Republica", "Estadio_Municipal", 2200, 21, 50, 60, 20, -1, "regular", "sim", "boa"),
    ]
    
    for s in segmentos_novos:
        rede.adicionar_segmento(s)
        
    print(f"🗺️ Mais {len(segmentos_novos)} segmentos de Braga adicionados à rede urbana.")
