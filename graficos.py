import matplotlib.pyplot as plt
import numpy as np

# Configuração de Estilo Global Matplotlib para Visual Premium Minimalista
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['text.color'] = '#0f172a'        # Slate 900
plt.rcParams['axes.labelcolor'] = '#0f172a'
plt.rcParams['xtick.color'] = '#475569'       # Slate 600
plt.rcParams['ytick.color'] = '#475569'

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
                    nomes_ruas.append(f"{origem} ➔ {destino}")
                    poluicao.append(seg.get_qualidade_ar())
                    verdes.append(seg.get_zonas_verdes())

        if not nomes_ruas:
            print(" Erro: Não há malha urbana registada para gerar estatísticas.")
            return

        # Para legibilidade absoluta e evitar sobreposição, usamos barras horizontais (barh)
        # com dimensionamento dinâmico da altura baseado no número de ruas.
        y = np.arange(len(nomes_ruas))
        largura = 0.35
        
        # Ajustar dinamicamente o tamanho da figura para evitar sobreposição de texto
        altura_figura = max(6, len(nomes_ruas) * 0.4)
        fig, ax = plt.subplots(figsize=(12, altura_figura))

        barras1 = ax.barh(y - largura / 2, poluicao, largura, label='Qualidade do Ar', color='#0284c7') # Sky 600
        barras2 = ax.barh(y + largura / 2, verdes,   largura, label='Zonas Verdes',    color='#10b981') # Emerald 500

        ax.set_xlabel('Índice de Qualidade (0-100)', fontweight='bold', labelpad=10)
        ax.set_title('Raio-X Ambiental: Rede Braga Saudável', fontsize=15, fontweight='bold', pad=20)
        ax.set_yticks(y)
        
        # Limpar underscores das ruas para apresentação fluida
        nomes_limpos = [n.replace("_", " ") for n in nomes_ruas]
        ax.set_yticklabels(nomes_limpos, fontsize=9, color='#1e293b')
        ax.set_xlim(0, 115)
        ax.invert_yaxis() # Primeira rua no topo

        # Gridlines horizontais e remoção de spines desnecessárias
        ax.grid(axis='x', linestyle='--', alpha=0.4, color='#cbd5e1')
        ax.set_axisbelow(True)
        for spine in ['top', 'right', 'left']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#cbd5e1')

        ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', shadow=False)
        
        ax.bar_label(barras1, padding=4, fmt='%d', fontsize=8, color='#0f172a')
        ax.bar_label(barras2, padding=4, fmt='%d', fontsize=8, color='#0f172a')

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

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
        fig.suptitle(f'Painel de Análise de Utilizadores (Total: {len(todos)})',
                     fontsize=15, fontweight='bold', color='#0f172a', y=0.98)

        # --- Gráfico 1: Donut Moderno de Perfis ---
        cores = ['#ef4444', '#0284c7', '#10b981'] # Red 500, Sky 600, Emerald 500
        labels = list(contagem_perfis.keys())
        valores = list(contagem_perfis.values())

        # Ocultamos os nomes das fatias no donut e mostramos apenas a percentagem interna
        # para garantir sobreposição zero. Os nomes e totais vão para a legenda.
        wedges, texts, autotexts = ax1.pie(
            valores,
            autopct='%1.1f%%',
            colors=cores[:len(labels)],
            startangle=140,
            pctdistance=0.75,
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
            textprops=dict(color='#0f172a', weight='bold', fontsize=10)
        )
        
        # Ocultar percentagens de fatias insignificantes (< 4%) para evitar overlapping
        for autotext, val in zip(autotexts, valores):
            if val / sum(valores) < 0.04:
                autotext.set_text('')

        ax1.set_title('Distribuição por Perfil Clínico', fontweight='bold', fontsize=12, pad=15)
        
        # Legenda premium com badges fora da área do gráfico
        labels_legend = [f"{l.replace('_', ' ').title()} ({v})" for l, v in zip(labels, valores)]
        ax1.legend(
            wedges, labels_legend,
            title="Perfis",
            loc="center left",
            bbox_to_anchor=(0.9, 0.5),
            frameon=True,
            facecolor='#ffffff',
            edgecolor='#cbd5e1'
        )

        # --- Gráfico 2: Histograma Empilhado (Stacked) de Idades ---
        # Ao empilhar (stacked=True), as idades não se sobrepõem transparentemente
        idades_list = []
        labels_list = []
        cores_list = []
        
        for i, perfil in enumerate(labels):
            idades_list.append(idades_por_perfil[perfil])
            labels_list.append(perfil.replace('_', ' ').title())
            cores_list.append(cores[i % len(cores)])

        ax2.hist(
            idades_list,
            bins=10,
            stacked=True,
            label=labels_list,
            color=cores_list,
            edgecolor='white',
            linewidth=1,
            alpha=0.9
        )

        ax2.set_xlabel('Idade (anos)', fontweight='bold', labelpad=8)
        ax2.set_ylabel('Número de Utilizadores', fontweight='bold', labelpad=8)
        ax2.set_title('Distribuição de Idades por Perfil', fontweight='bold', fontsize=12, pad=15)
        
        # Gridlines suaves e remoção de spines para ax2
        ax2.grid(axis='y', linestyle='--', alpha=0.4, color='#cbd5e1')
        ax2.set_axisbelow(True)
        for spine in ['top', 'right']:
            ax2.spines[spine].set_visible(False)
        ax2.spines['left'].set_color('#cbd5e1')
        ax2.spines['bottom'].set_color('#cbd5e1')
        
        ax2.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1')

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
            rotulos.append(f"Rota {i+1} ({distancia}m)")
            custos.append(custo)

        fig, ax = plt.subplots(figsize=(10, 5.5))
        
        # Destacar a rota de menor custo em Verde Esmeralda e as outras em Azul
        custo_min = min(custos)
        cores_barras = ['#10b981' if c == custo_min else '#0284c7' for c in custos]
        
        barras = ax.bar(rotulos, custos, color=cores_barras, width=0.45, edgecolor='#cbd5e1', linewidth=1)
        
        ax.set_ylabel('Custo Total (Penalizações)', fontweight='bold', labelpad=10)
        ax.set_title(f'Comparação de Alternativas: {origem.replace("_", " ")} ➔ {destino.replace("_", " ")}', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticklabels(rotulos, rotation=15, ha='right', fontsize=9)
        
        ax.grid(axis='y', linestyle='--', alpha=0.4, color='#cbd5e1')
        ax.set_axisbelow(True)
        
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['bottom'].set_color('#cbd5e1')
        
        ax.bar_label(barras, padding=4, fmt='%.1f', fontweight='bold', color='#0f172a')
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def estatisticas_percursos(arvore, rede):
        todos = arvore.listar_todos()
        contagem_rotas = {}

        for u in todos:
            historico = u.get_historico()
            for h in historico:
                if len(h) == 4:
                    origem, destino = h[0], h[1]
                    rota = f"{origem} ➔ {destino}"
                    contagem_rotas[rota] = contagem_rotas.get(rota, 0) + 1

        if not contagem_rotas:
            print(" Não há histórico de percursos suficiente para gerar estatísticas.")
            return

        rotas_ordenadas = sorted(contagem_rotas.items(), key=lambda x: x[1], reverse=True)[:10] # Top 10
        rotulos = [r[0].replace("_", " ") for r in rotas_ordenadas]
        valores = [r[1] for r in rotas_ordenadas]

        # Gráfico horizontal para visualização limpa de textos longos
        fig, ax = plt.subplots(figsize=(12, 6))
        
        y = np.arange(len(rotulos))
        barras = ax.barh(y, valores, color='#8b5cf6', height=0.55, edgecolor='#cbd5e1', linewidth=1) # Violet 500

        ax.set_xlabel('Número de Viagens Realizadas', fontweight='bold', labelpad=10)
        ax.set_title('Top 10 Percursos Mais Populares', fontweight='bold', fontsize=14, pad=20)
        ax.set_yticks(y)
        ax.set_yticklabels(rotulos, fontsize=9.5, color='#1e293b')
        ax.invert_yaxis() # Primeiro lugar no topo

        # Gridlines verticais e spines minimalistas
        ax.grid(axis='x', linestyle='--', alpha=0.4, color='#cbd5e1')
        ax.set_axisbelow(True)
        
        for spine in ['top', 'right', 'left']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#cbd5e1')

        ax.bar_label(barras, padding=5, fmt='%d', fontweight='bold', color='#475569')

        plt.tight_layout()
        plt.show()
