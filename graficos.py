import matplotlib.pyplot as plt
import numpy as np

class VisualizacaoDados:
    @staticmethod
    def raio_x_cidade(rede):
        ruas_vistas = set()
        nomes_ruas = []
        poluicao = []
        verdes = []

        for origem, conexoes in rede._grafo.items():
            for seg in conexoes:
                destino = seg.get_destino()

                id_rua = tuple(sorted([origem, destino]))
                
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    nomes_ruas.append(f"{origem}\n↓\n{destino}")
                    poluicao.append(seg.get_qualidade_ar())
                    verdes.append(seg.get_zonas_verdes())

        if not nomes_ruas:
            print(" Erro: Não há malha urbana registada para gerar estatísticas.")
            return

        x = np.arange(len(nomes_ruas))
        largura = 0.35  

        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Barras vermelhas para o perigo (poluição) e verdes para saúde (natureza)
        barras1 = ax.bar(x - largura/2, poluicao, largura, label='Poluição', color='#e74c3c')
        barras2 = ax.bar(x + largura/2, verdes, largura, label='Zonas Verdes', color='#2ecc71')

        # 3. Formatação Profissional
        ax.set_ylabel('Índice de Qualidade (0-100)', fontweight='bold')
        ax.set_title('Raio-X Ambiental: Rede Braga Saudável', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(nomes_ruas, rotation=0, fontsize=9)
        ax.legend()

        # Adicionar os valores numéricos por cima de cada barra
        ax.bar_label(barras1, padding=3)
        ax.bar_label(barras2, padding=3)

        # Ajustar as margens para nada ficar cortado
        fig.tight_layout()
        
        print("\n A abrir o painel de controlo visual... (Fecha a janela do gráfico para continuares a usar a consola)")
        plt.show()