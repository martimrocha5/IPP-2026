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

        barras1 = ax.bar(x - largura / 2, poluicao, largura, label='Qualidade do Ar', color='#3498db')
        barras2 = ax.bar(x + largura / 2, verdes,   largura, label='Zonas Verdes',    color='#2ecc71')

        ax.set_ylabel('Índice de Qualidade (0-100)', fontweight='bold')
        ax.set_title('Raio-X Ambiental: Rede Braga Saudável', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(nomes_ruas, rotation=0, fontsize=9)
        ax.set_ylim(0, 110)
        ax.legend()
        ax.bar_label(barras1, padding=3)
        ax.bar_label(barras2, padding=3)

        fig.tight_layout()
        print("\n A abrir o gráfico ambiental da cidade... (fecha a janela para continuares)")
        plt.show()

    @staticmethod
    def analise_utilizadores(arvore):
        todos = arvore.listar_todos()

        if not todos:
            print(" Erro: Não há utilizadores registados para gerar estatísticas.")
            return

        # --- Contagem por perfil ---
        contagem_perfis = {}
        idades_por_perfil = {}

        for u in todos:
            perfil = u.get_perfil()
            contagem_perfis[perfil] = contagem_perfis.get(perfil, 0) + 1

            if perfil not in idades_por_perfil:
                idades_por_perfil[perfil] = []
            idades_por_perfil[perfil].append(u.get_idade())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Análise de Utilizadores — Total: {len(todos)}',
                     fontsize=15, fontweight='bold')

        # --- Gráfico 1: Pizza de perfis ---
        cores = ['#e74c3c', '#3498db', '#2ecc71']
        labels = list(contagem_perfis.keys())
        valores = list(contagem_perfis.values())

        ax1.pie(
            valores,
            labels=labels,
            autopct='%1.1f%%',
            colors=cores[:len(labels)],
            startangle=140,
            textprops={'fontsize': 11}
        )
        ax1.set_title('Distribuição por Perfil', fontweight='bold')

        # --- Gráfico 2: Histograma de idades por perfil ---
        cores_hist = ['#e74c3c', '#3498db', '#2ecc71']
        for i, (perfil, idades) in enumerate(idades_por_perfil.items()):
            ax2.hist(
                idades,
                bins=10,
                alpha=0.7,
                label=perfil,
                color=cores_hist[i % len(cores_hist)],
                edgecolor='white'
            )

        ax2.set_xlabel('Idade', fontweight='bold')
        ax2.set_ylabel('Número de Utilizadores', fontweight='bold')
        ax2.set_title('Distribuição de Idades por Perfil', fontweight='bold')
        ax2.legend()

        # Imprimir resumo na consola
        print("\n--- Resumo Estatístico dos Utilizadores ---")
        for perfil, idades in idades_por_perfil.items():
            media = sum(idades) / len(idades)
            print(f" {perfil:35s} | {len(idades):4d} utilizadores | Idade média: {media:.1f} anos")
        print("-" * 60)

        fig.tight_layout()
        print("\n A abrir o painel de análise de utilizadores... (fecha a janela para continuares)")
        plt.show()

    @staticmethod
    def comparar_rotas(caminhos_com_custo, origem, destino):
        if not caminhos_com_custo or len(caminhos_com_custo) < 2:
            return

        rotulos = []
        custos = []

        for i, (caminho, custo) in enumerate(caminhos_com_custo):
            distancia = sum(seg.get_distancia() for seg in caminho)
            rotulos.append(f"Rota {i+1}\n({distancia}m)")
            custos.append(custo)

        fig, ax = plt.subplots(figsize=(10, 6))
        barras = ax.bar(rotulos, custos, color='#3498db')
        
        indice_melhor = custos.index(min(custos))
        barras[indice_melhor].set_color('#2ecc71')

        ax.set_ylabel('Custo Total (Penalizações)')
        ax.set_title(f'Comparação de Alternativas: {origem} -> {destino}', fontweight='bold')
        ax.bar_label(barras, padding=3)
        
        plt.tight_layout()
        plt.show()
