import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import sys
import math
import json
import random
import csv

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Importar lógica de negócio
from dados import Utilizador, RedeUrbana, Segmento
from arvores import ArvoreUtilizadores
from model import MotorAnalise, MotorRecomendacao
from controller import inicializar_rede, gerar_id_unico, MODOS_VALIDOS, PERFIS_VALIDOS
from mapa_braga import carregar_mapa_expandido
from graficos import VisualizacaoDados
from view import View

class RedirectText:
    """Classe para redirecionar o stdout para um widget Text do Tkinter com colorização inteligente."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        # Configurar tags de cor para logs modernos em fundo claro
        self.text_widget.tag_configure("success", foreground="#16a34a", font=("Consolas", 10, "bold")) # Green (Darker)
        self.text_widget.tag_configure("warning", foreground="#d97706", font=("Consolas", 10, "bold")) # Amber (Darker)
        self.text_widget.tag_configure("error", foreground="#dc2626", font=("Consolas", 10, "bold")) # Red (Darker)
        self.text_widget.tag_configure("info", foreground="#0284c7", font=("Consolas", 10)) # Deep Sky Blue
        self.text_widget.tag_configure("normal", foreground="#1e293b", font=("Consolas", 10)) # Preto Velho / Charcoal Slate

    def write(self, string):
        try:
            self.text_widget.config(state=tk.NORMAL)
            lines = string.split("\n")
            for i, line in enumerate(lines):
                is_last = (i == len(lines) - 1)
                
                tag = "normal"
                line_lower = line.lower()
                if "✅" in line or "sucesso" in line_lower or "otimizada encontrada" in line_lower or "guardado" in line_lower or "carregados" in line_lower:
                    tag = "success"
                elif "⚠️" in line or "aviso" in line_lower or "atenção" in line_lower:
                    tag = "warning"
                elif "❌" in line or "erro" in line_lower or "não encontrado" in line_lower or "sem rota viável" in line_lower:
                    tag = "error"
                elif "🌿" in line or "🚀" in line or "---" in line or "🔍" in line or "⏱️" in line or "🔥" in line or "📏" in line:
                    tag = "info"
                    
                self.text_widget.insert(tk.END, line, tag)
                if not is_last:
                    self.text_widget.insert(tk.END, "\n", "normal")
                    
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
        except Exception:
            pass
        
    def flush(self):
        pass

class AppGui(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Braga Saudável - Gestão Global")
        self.geometry("1200x850") 
        self.minsize(1050, 750)
        
        # Iniciar em Fullscreen (Maximizado)
        try:
            self.state('zoomed')
        except Exception:
            pass
        
        # Configuração do Grid para 2 colunas: sidebar (0) e content (1)
        self.columnconfigure(0, weight=0, minsize=260)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Paleta de Cores e Estética Geral (Clean Light Theme with Violet Neon Accents)
        self.cor_bg = "#f8fafc"        # Slate 50 (Fundo Branco Limpo)
        self.cor_card = "#ffffff"      # Branco Puro para os Cards
        self.cor_sidebar = "#0f172a"   # Slate 900 (Contraste Premium)
        self.cor_sidebar_btn = "#1e293b" # Slate 800
        self.cor_primary = "#8b5cf6"   # Neon Violet
        self.cor_primary_hover = "#7c3aed" # Neon Violet Hover
        self.cor_secondary = "#0ea5e9" # Neon Blue
        self.cor_secondary_hover = "#0284c7" # Neon Blue Hover
        self.cor_danger = "#ef4444"    # Red 500
        self.cor_danger_hover = "#dc2626" # Red 600
        self.cor_text = "#0f172a"      # Dark Slate 900 para Texto
        self.cor_muted = "#64748b"     # Slate 500 para Texto Mudo
        self.fonte_normal = ("Segoe UI", 10)
        self.fonte_bold = ("Segoe UI", 10, "bold")
        self.fonte_titulo = ("Segoe UI", 13, "bold")
        
        self.configure(bg=self.cor_bg)
        self._configurar_estilos()
        
        # Inicialização do Sistema de Braga Saudável
        self.rede = RedeUrbana()
        self.utilizadores = ArvoreUtilizadores()
        self.motor_analise = MotorAnalise()
        self.motor_recomendacao = MotorRecomendacao(self.motor_analise)
        
        # Clima Composto (Suporta Dia/Noite e Chuva simultâneos)
        self.periodo_sel = "Sol"
        self.chuva_sel = "Seco"
        self.clima = "Sol"
        self.ultima_rota_calculada = None
        
        inicializar_rede(self.rede)
        carregar_mapa_expandido(self.rede)
        self._carregar_utilizadores_com_historico("dataset_utilizadores.json")
        
        self._criar_interface()
        self.selecionar_pagina(0)
        
    def _carregar_utilizadores_com_historico(self, ficheiro):
        try:
            with open(ficheiro, 'r', encoding='utf-8') as f:
                dados_users = json.load(f)
            for user in dados_users:
                try:
                    novo_user = Utilizador(
                        id_utilizador=user["id"], nome=user["nome"],
                        idade=user["idade"], sexo=user["sexo"], perfil=user["perfil"]
                    )
                    # Restaurar histórico se existir
                    if "historico" in user:
                        for h in user["historico"]:
                            if len(h) == 4:
                                novo_user.adicionar_historico(h[0], h[1], h[2], h[3])
                    self.utilizadores.inserir(novo_user)
                except (KeyError, ValueError):
                    pass
            print(f"✅ Utilizadores carregados com histórico do ficheiro '{ficheiro}'.")
        except Exception as e:
            print(f"⚠️ Erro ao carregar utilizadores base: {e}")

    def _configurar_estilos(self):
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        style.configure("TFrame", background=self.cor_bg)
        
        # Estilo para as LabelFrames modernas (estilo cards transparentes)
        style.configure("TLabelFrame", background=self.cor_card, foreground=self.cor_text, font=("Segoe UI", 10, "bold"), borderwidth=1, relief="solid")
        style.configure("TLabelFrame.Label", background=self.cor_card, font=("Segoe UI", 10, "bold"), foreground=self.cor_primary)
        
        # Estilo para as Labels
        style.configure("TLabel", background=self.cor_card, font=self.fonte_normal, foreground=self.cor_text)
        
        # Comboboxes e Entries
        style.configure("TCombobox", padding=5, font=self.fonte_normal, background=self.cor_bg, fieldbackground=self.cor_card)
        style.configure("TEntry", padding=5, font=self.fonte_normal, background=self.cor_bg, fieldbackground=self.cor_card)
        
        # Treeview Styling
        style.configure("Treeview", 
                        background=self.cor_card, 
                        foreground=self.cor_text, 
                        rowheight=26, 
                        fieldbackground=self.cor_card,
                        font=self.fonte_normal)
        style.configure("Treeview.Heading", 
                        background="#f1f5f9", 
                        foreground=self.cor_primary, 
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview", 
                  background=[("selected", self.cor_primary)], 
                  foreground=[("selected", "white")])

    def criar_botao_moderno(self, parent, text, command, bg=None, fg="white", hover_bg=None, font=None, padx=12, pady=6):
        if bg is None: bg = self.cor_primary
        if hover_bg is None: hover_bg = self.cor_primary_hover
        if font is None: font = self.fonte_bold
        
        btn = tk.Button(
            parent, text=text, command=command, font=font,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
            bd=0, relief="flat", padx=padx, pady=pady, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def criar_card_frame(self, parent, padding=20):
        # Um frame branco com contorno fino de Slate 200 para parecer um card moderno
        card = tk.Frame(parent, bg=self.cor_card, highlightbackground="#e2e8f0", highlightthickness=1, bd=0, relief="flat")
        card.config(padx=padding, pady=padding)
        return card

    def _criar_interface(self):
        # 1. SIDEBAR FRAME (Esquerda)
        self.sidebar_frame = tk.Frame(self, bg=self.cor_sidebar, width=260)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # Logo no Topo da Sidebar
        logo_container = tk.Frame(self.sidebar_frame, bg=self.cor_sidebar, pady=25)
        logo_container.pack(fill=tk.X)
        
        lbl_logo_icon = tk.Label(logo_container, text="🏃", font=("Segoe UI", 28), bg=self.cor_sidebar, fg=self.cor_primary)
        lbl_logo_icon.pack()
        lbl_logo = tk.Label(logo_container, text="Braga Saudável", font=("Segoe UI", 15, "bold"), bg=self.cor_sidebar, fg="white")
        lbl_logo.pack()
        lbl_sub = tk.Label(logo_container, text="Painel de Gestão Urbana", font=("Segoe UI", 9), bg=self.cor_sidebar, fg="#94a3b8")
        lbl_sub.pack(pady=(2, 0))
        
        # Linha Divisória
        div = tk.Frame(self.sidebar_frame, bg="#334155", height=1)
        div.pack(fill=tk.X, padx=20, pady=10)
        
        # Botões de Navegação da Sidebar
        self.btn_nav_rec = self._criar_btn_sidebar("📍  Recomendação", lambda: self.selecionar_pagina(0))
        self.btn_nav_user = self._criar_btn_sidebar("👥  Utilizadores", lambda: self.selecionar_pagina(1))
        self.btn_nav_mapa = self._criar_btn_sidebar("🗺️  Mapa & Rede", lambda: self.selecionar_pagina(2))
        self.btn_nav_fich = self._criar_btn_sidebar("💾  Dados & Estatísticas", lambda: self.selecionar_pagina(3))
        
        self.sidebar_btns = [self.btn_nav_rec, self.btn_nav_user, self.btn_nav_mapa, self.btn_nav_fich]
        
        # Box de Status do Clima / Sistema na Sidebar (no rodapé)
        status_box = tk.Frame(self.sidebar_frame, bg="#1e293b", padx=15, pady=15, bd=0)
        status_box.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=20)
        
        self.lbl_clima_sidebar = tk.Label(status_box, text="🌤️ Clima: Sol", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#e2e8f0")
        self.lbl_clima_sidebar.pack(anchor=tk.W)
        
        self.lbl_users_count = tk.Label(status_box, text=f"👥 Utilizadores: {len(self.utilizadores.listar_todos())}", font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8")
        self.lbl_users_count.pack(anchor=tk.W, pady=(5, 0))
        
        # 2. CONTENT FRAME (Direita) - Usando PanedWindow ajustável!
        self.content_frame = tk.Frame(self, bg=self.cor_bg)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # PanedWindow vertical para separar a área de páginas do terminal de logs
        self.paned_window = tk.PanedWindow(self.content_frame, orient=tk.VERTICAL, bg=self.cor_bg, bd=0, sashwidth=6, sashrelief="flat")
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        
        # Content Container para as páginas (Top pane)
        self.page_container = tk.Frame(self.paned_window, bg=self.cor_bg)
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)
        
        # Inicializar os frames das páginas
        self.tab_recomendacao = tk.Frame(self.page_container, bg=self.cor_bg)
        self.tab_utilizadores = tk.Frame(self.page_container, bg=self.cor_bg)
        self.tab_mapa = tk.Frame(self.page_container, bg=self.cor_bg)
        self.tab_ficheiros = tk.Frame(self.page_container, bg=self.cor_bg)
        
        self._setup_tab_recomendacao()
        self._setup_tab_utilizadores()
        self._setup_tab_mapa()
        self._setup_tab_ficheiros()
        
        # Adicionar o page_container ao PanedWindow
        self.paned_window.add(self.page_container, minsize=380, stretch="always")
        
        # Console de Atividades (Bottom pane)
        console_wrapper = tk.Frame(self.paned_window, bg=self.cor_bg)
        console_wrapper.columnconfigure(0, weight=1)
        console_wrapper.rowconfigure(0, weight=1)
        
        frame_console = tk.LabelFrame(console_wrapper, text=" Terminal de Atividades (Logs) ", bg=self.cor_card, font=("Segoe UI", 10, "bold"), fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_console.grid(row=0, column=0, sticky="nsew", padx=25, pady=(0, 25))
        frame_console.columnconfigure(0, weight=1)
        frame_console.rowconfigure(0, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(
            frame_console, font=("Consolas", 10), 
            bg="#ffffff", fg="#0f172a", insertbackground="#0f172a", 
            bd=0, highlightthickness=0
        )
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Adicionar o console ao PanedWindow
        self.paned_window.add(console_wrapper, minsize=150, stretch="always")
        
        sys.stdout = RedirectText(self.console_text)
        print("✅ Sistema Iniciado com Sucesso. Todas as funcionalidades disponíveis.")

    def _criar_btn_sidebar(self, text, command):
        btn = tk.Button(
            self.sidebar_frame, text=text, command=command, font=("Segoe UI", 11, "bold"),
            bg=self.cor_sidebar, fg="#94a3b8", activebackground=self.cor_sidebar_btn, activeforeground="white",
            bd=0, relief="flat", padx=25, pady=12, anchor="w", cursor="hand2"
        )
        btn.pack(fill=tk.X, padx=15, pady=4)
        btn.bind("<Enter>", lambda e: self._hover_btn_sidebar(btn, True))
        btn.bind("<Leave>", lambda e: self._hover_btn_sidebar(btn, False))
        return btn

    def _hover_btn_sidebar(self, btn, is_enter):
        # Apenas aplica hover se o botão não for o ativo (azul)
        if btn["bg"] != self.cor_primary:
            if is_enter:
                btn.config(bg=self.cor_sidebar_btn, fg="white")
            else:
                btn.config(bg=self.cor_sidebar, fg="#94a3b8")

    def selecionar_pagina(self, idx):
        paginas = [self.tab_recomendacao, self.tab_utilizadores, self.tab_mapa, self.tab_ficheiros]
        
        # Esconder todas as páginas
        for pag in paginas:
            pag.grid_forget()
            
        # Exibir a página selecionada com margens limpas
        paginas[idx].grid(row=0, column=0, sticky="nsew", padx=25, pady=(25, 15))
        
        # Atualizar estilos dos botões da sidebar
        for i, btn in enumerate(self.sidebar_btns):
            if i == idx:
                btn.config(bg=self.cor_primary, fg="white")
            else:
                btn.config(bg=self.cor_sidebar, fg="#94a3b8")
                
        # Atualizar contagem rápida
        try:
            self.lbl_users_count.config(text=f"👥 Utilizadores: {len(self.utilizadores.listar_todos())}")
        except Exception:
            pass

    # =========================================================================
    # TAB: RECOMENDAÇÃO
    # =========================================================================
    def _setup_tab_recomendacao(self):
        self.modo_principal_sel = "padrao"
        self.modo_secundario_sel = "Nenhum"
        
        self.tab_recomendacao.columnconfigure(0, weight=1)
        self.tab_recomendacao.columnconfigure(1, weight=1)
        self.tab_recomendacao.rowconfigure(0, weight=1)
        
        # Card Esquerda (Inputs)
        card_esq = self.criar_card_frame(self.tab_recomendacao, padding=12)
        card_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        card_esq.columnconfigure(1, weight=1)
        
        # Título
        lbl_titulo = tk.Label(card_esq, text="📍 Calcular Rota Otimizada", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_titulo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))
        
        pontos = sorted(self.rede.listar_pontos())
        
        # Origem
        tk.Label(card_esq, text="Ponto de Origem:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.cb_origem = ttk.Combobox(card_esq, values=pontos, state="readonly", font=self.fonte_normal)
        self.cb_origem.grid(row=1, column=1, sticky="ew", pady=3, padx=(15, 0))
        if pontos: self.cb_origem.current(0)
        
        # Destino
        tk.Label(card_esq, text="Ponto de Destino:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.cb_destino = ttk.Combobox(card_esq, values=pontos, state="readonly", font=self.fonte_normal)
        self.cb_destino.grid(row=2, column=1, sticky="ew", pady=3, padx=(15, 0))
        if len(pontos) > 1: self.cb_destino.current(1)
            
        # ID do Utilizador
        tk.Label(card_esq, text="ID do Utilizador:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=3, column=0, sticky=tk.W, pady=3)
        frame_user = tk.Frame(card_esq, bg=self.cor_card)
        frame_user.grid(row=3, column=1, sticky="ew", pady=3, padx=(15, 0))
        frame_user.columnconfigure(0, weight=1)
        
        self.entry_user_id_rec = ttk.Entry(frame_user, font=self.fonte_normal)
        self.entry_user_id_rec.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        btn_novo_rapido = self.criar_botao_moderno(frame_user, "✨ Novo Rápido", self.janela_novo_utilizador_rapido, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover, pady=3, padx=8)
        btn_novo_rapido.grid(row=0, column=1, sticky="e")
        
        # Modo Principal (Chips / Seletor Segmentado)
        tk.Label(card_esq, text="Modo Principal:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=4, column=0, sticky=tk.W, pady=3)
        frame_modo_prio = tk.Frame(card_esq, bg=self.cor_card)
        frame_modo_prio.grid(row=4, column=1, sticky="w", pady=3, padx=(15, 0))
        
        self.botoes_modo_prio = {}
        
        modo_labels = {
            "padrao": "Padrão",
            "relaxar": "Relaxar",
            "exercicio": "Exercício",
            "ar_puro": "Ar Puro",
            "trabalho": "Ir p/ Trabalho"
        }
        
        for col_idx, m in enumerate(MODOS_VALIDOS):
            btn = tk.Button(
                frame_modo_prio, text=modo_labels.get(m, m.replace("_", " ").title()),
                font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=12, pady=4, cursor="hand2"
            )
            btn.config(command=lambda modo=m: self._selecionar_modo_principal(modo))
            btn.grid(row=0, column=col_idx, padx=(0, 6))
            self.botoes_modo_prio[m] = btn
            
        self._atualizar_botoes_modo_principal()
        
        # Modo Secundário (Chips / Seletor Segmentado)
        tk.Label(card_esq, text="Modo Secundário:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=5, column=0, sticky=tk.W, pady=3)
        frame_modo_sec = tk.Frame(card_esq, bg=self.cor_card)
        frame_modo_sec.grid(row=5, column=1, sticky="w", pady=3, padx=(15, 0))
        
        self.botoes_modo_sec = {}
        
        for col_idx, m in enumerate(["Nenhum"] + MODOS_VALIDOS):
            btn = tk.Button(
                frame_modo_sec, text="Nenhum" if m == "Nenhum" else modo_labels.get(m, m.replace("_", " ").title()),
                font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=12, pady=4, cursor="hand2"
            )
            btn.config(command=lambda modo=m: self._selecionar_modo_secundario(modo))
            btn.grid(row=0, column=col_idx, padx=(0, 6))
            self.botoes_modo_sec[m] = btn
            
        self._atualizar_botoes_modo_secundario()
        
        # Acompanhante
        tk.Label(card_esq, text="Acompanhante:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=6, column=0, sticky=tk.W, pady=3)
        self.cb_acompanhante = ttk.Combobox(card_esq, values=["Nenhum", "Carrinho de Mão", "Carrinho de Compras", "Cadeira de Rodas", "Carrinho de Bebé", "Mala com Rodas", "Andarilho"], state="readonly", font=self.fonte_normal)
        self.cb_acompanhante.grid(row=6, column=1, sticky="ew", pady=3, padx=(15, 0))
        self.cb_acompanhante.current(0)
        
        # Período do Dia (Chips / Seletor Segmentado)
        tk.Label(card_esq, text="Período do Dia:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=7, column=0, sticky=tk.W, pady=3)
        frame_periodo = tk.Frame(card_esq, bg=self.cor_card)
        frame_periodo.grid(row=7, column=1, sticky="w", pady=3, padx=(15, 0))
        
        self.botoes_periodo = {}
        for col_idx, p in enumerate(["Sol", "Noite"]):
            lbl = "☀️ Dia / Sol" if p == "Sol" else "🌙 Noite"
            btn = tk.Button(
                frame_periodo, text=lbl,
                font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=12, pady=4, cursor="hand2"
            )
            btn.config(command=lambda per=p: self._definir_periodo(per))
            btn.grid(row=0, column=col_idx, padx=(0, 6))
            self.botoes_periodo[p] = btn
            
        # Precipitação (Chips / Seletor Segmentado)
        tk.Label(card_esq, text="Precipitação:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).grid(row=8, column=0, sticky=tk.W, pady=3)
        frame_chuva = tk.Frame(card_esq, bg=self.cor_card)
        frame_chuva.grid(row=8, column=1, sticky="w", pady=3, padx=(15, 0))
        
        self.botoes_chuva = {}
        for col_idx, c in enumerate(["Seco", "Chuva"]):
            lbl = "☁️ Seco" if c == "Seco" else "🌧️ Chuva"
            btn = tk.Button(
                frame_chuva, text=lbl,
                font=("Segoe UI", 9, "bold"), bd=0, relief="flat", padx=12, pady=4, cursor="hand2"
            )
            btn.config(command=lambda chv=c: self._definir_chuva(chv))
            btn.grid(row=0, column=col_idx, padx=(0, 6))
            self.botoes_chuva[c] = btn
            
        self._atualizar_botoes_periodo()
        self._atualizar_botoes_chuva()
        
        # Botões de Ação
        btn_frame = tk.Frame(card_esq, bg=self.cor_card)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(8, 0))
        
        self.criar_botao_moderno(btn_frame, "🚀 Calcular Rota", self.acao_recomendar, bg=self.cor_primary, hover_bg=self.cor_primary_hover, pady=4, padx=8).pack(side=tk.LEFT, padx=6)
        self.criar_botao_moderno(btn_frame, "👁️ Detalhes Segmento", self.acao_ver_segmento, bg="#475569", hover_bg="#334155", pady=4, padx=8).pack(side=tk.LEFT, padx=6)
        self.criar_botao_moderno(btn_frame, "🗺️ Ver Rota no Mapa", self.acao_ver_rota_mapa, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover, pady=4, padx=8).pack(side=tk.LEFT, padx=6)

        # Card Direita (Resultados)
        card_dir = self.criar_card_frame(self.tab_recomendacao)
        card_dir.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        card_dir.columnconfigure(0, weight=1)
        
        self.card_resultados = card_dir
        self._mostrar_placeholder_resultados()

    def _selecionar_modo_principal(self, modo):
        self.modo_principal_sel = modo
        if modo == "trabalho":
            self.modo_secundario_sel = "Nenhum"
        # Se selecionou exercicio, desativar relaxar no secundario
        elif modo == "exercicio" and self.modo_secundario_sel == "relaxar":
            self.modo_secundario_sel = "Nenhum"
        # Se selecionou relaxar, desativar exercicio no secundario
        elif modo == "relaxar" and self.modo_secundario_sel == "exercicio":
            self.modo_secundario_sel = "Nenhum"
            
        self._atualizar_botoes_modo_principal()
        self._atualizar_botoes_modo_secundario()

    def _atualizar_botoes_modo_principal(self):
        modo_labels = {
            "padrao": "Padrão",
            "relaxar": "Relaxar",
            "exercicio": "Exercício",
            "ar_puro": "Ar Puro",
            "trabalho": "Ir p/ Trabalho"
        }
        for m, btn in self.botoes_modo_prio.items():
            # Esconder "relaxar" se o secundario for "exercicio", ou esconder "exercicio" se o secundario for "relaxar"
            deve_esconder = (m == "relaxar" and self.modo_secundario_sel == "exercicio") or \
                             (m == "exercicio" and self.modo_secundario_sel == "relaxar")
                             
            if deve_esconder:
                btn.config(
                    text="", state=tk.DISABLED,
                    bg=self.cor_card, activebackground=self.cor_card,
                    bd=0, relief="flat", cursor=""
                )
                btn.bind("<Enter>", lambda e: None)
                btn.bind("<Leave>", lambda e: None)
            else:
                if m == self.modo_principal_sel:
                    bg_cor = self.cor_primary
                    hover_cor = self.cor_primary_hover
                    fg_cor = "white"
                else:
                    bg_cor = "#e2e8f0"
                    hover_cor = "#cbd5e1"
                    fg_cor = self.cor_text
                
                btn.config(
                    text=modo_labels.get(m, m.replace("_", " ").title()),
                    state=tk.NORMAL,
                    bg=bg_cor, fg=fg_cor,
                    activebackground=hover_cor, activeforeground=fg_cor,
                    cursor="hand2"
                )
                # Bind hover effect dynamically
                btn.bind("<Enter>", lambda e, b=btn, hc=hover_cor: b.config(bg=hc))
                btn.bind("<Leave>", lambda e, b=btn, bc=bg_cor: b.config(bg=bc))

    def _selecionar_modo_secundario(self, modo):
        if modo == "trabalho":
            self.modo_principal_sel = "trabalho"
            self.modo_secundario_sel = "Nenhum"
        else:
            self.modo_secundario_sel = modo
            # Se selecionou exercicio, desativar relaxar no principal
            if modo == "exercicio" and self.modo_principal_sel == "relaxar":
                self.modo_principal_sel = "padrao"
            # Se selecionou relaxar, desativar exercicio no principal
            elif modo == "relaxar" and self.modo_principal_sel == "exercicio":
                self.modo_principal_sel = "padrao"
            
        self._atualizar_botoes_modo_principal()
        self._atualizar_botoes_modo_secundario()

    def _atualizar_botoes_modo_secundario(self):
        modo_labels = {
            "padrao": "Padrão",
            "relaxar": "Relaxar",
            "exercicio": "Exercício",
            "ar_puro": "Ar Puro",
            "trabalho": "Ir p/ Trabalho"
        }
        for m, btn in self.botoes_modo_sec.items():
            # Esconder "relaxar" se o principal for "exercicio", ou esconder "exercicio" se o principal for "relaxar"
            # Esconder "trabalho" da lista secundária pois não faz sentido combinado, e esconder todos exceto "Nenhum" se principal for "trabalho"
            deve_esconder = (m == "relaxar" and self.modo_principal_sel == "exercicio") or \
                             (m == "exercicio" and self.modo_principal_sel == "relaxar") or \
                             (m == "trabalho") or \
                             (self.modo_principal_sel == "trabalho" and m != "Nenhum")
                             
            if deve_esconder:
                btn.config(
                    text="", state=tk.DISABLED,
                    bg=self.cor_card, activebackground=self.cor_card,
                    bd=0, relief="flat", cursor=""
                )
                btn.bind("<Enter>", lambda e: None)
                btn.bind("<Leave>", lambda e: None)
            else:
                if m == self.modo_secundario_sel:
                    bg_cor = self.cor_secondary
                    hover_cor = self.cor_secondary_hover
                    fg_cor = "white"
                else:
                    bg_cor = "#e2e8f0"
                    hover_cor = "#cbd5e1"
                    fg_cor = self.cor_text
                    
                btn.config(
                    text="Nenhum" if m == "Nenhum" else modo_labels.get(m, m.replace("_", " ").title()),
                    state=tk.NORMAL,
                    bg=bg_cor, fg=fg_cor,
                    activebackground=hover_cor, activeforeground=fg_cor,
                    cursor="hand2"
                )
                # Bind hover effect dynamically
                btn.bind("<Enter>", lambda e, b=btn, hc=hover_cor: b.config(bg=hc))
                btn.bind("<Leave>", lambda e, b=btn, bc=bg_cor: b.config(bg=bc))

    def _mostrar_placeholder_resultados(self):
        for widget in self.card_resultados.winfo_children():
            widget.destroy()
            
        lbl_titulo = tk.Label(self.card_resultados, text="✨ Resultados da Rota", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_titulo.pack(anchor=tk.W, pady=(0, 20))
        
        frame_placeholder = tk.Frame(self.card_resultados, bg=self.cor_card)
        frame_placeholder.pack(fill=tk.BOTH, expand=True)
        
        lbl_icon = tk.Label(frame_placeholder, text="🔍", font=("Segoe UI", 48), bg=self.card_resultados["bg"], fg="#94a3b8")
        lbl_icon.pack(pady=(50, 10))
        
        lbl_texto = tk.Label(frame_placeholder, 
                             text="Aguardando cálculo da rota otimizada...\nInsira os dados à esquerda e clique em 'Calcular Rota'.", 
                             font=self.fonte_normal, bg=self.cor_card, fg="#64748b", justify="center")
        lbl_texto.pack(pady=10)

    def _mostrar_erro_resultados(self, origem, destino):
        for widget in self.card_resultados.winfo_children():
            widget.destroy()
            
        lbl_titulo = tk.Label(self.card_resultados, text="❌ Sem Rota Viável", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_danger)
        lbl_titulo.pack(anchor=tk.W, pady=(0, 20))
        
        lbl_erro = tk.Label(self.card_resultados, 
                             text=f"Não foi possível encontrar uma rota viável de\n'{origem.replace('_', ' ')}' para '{destino.replace('_', ' ')}'\ncom os parâmetros selecionados.",
                             font=self.fonte_normal, bg=self.cor_card, fg=self.cor_text, justify="center")
        lbl_erro.pack(pady=40)

    def _atualizar_resultados_rota(self, distancia, tempo, calorias, caminho):
        for widget in self.card_resultados.winfo_children():
            widget.destroy()
            
        lbl_titulo = tk.Label(self.card_resultados, text="✨ Rota Otimizada Recomendada", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_titulo.pack(anchor=tk.W, pady=(0, 20))
        
        frame_badges = tk.Frame(self.card_resultados, bg=self.cor_card)
        frame_badges.pack(fill=tk.X, pady=(0, 20))
        
        # Badge Distância
        badge_dist = tk.Frame(frame_badges, bg="#ecfdf5", bd=0, highlightbackground="#10b981", highlightthickness=1, padx=10, pady=8)
        badge_dist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(badge_dist, text="📏 Distância", font=self.fonte_normal, bg="#ecfdf5", fg="#10b981").pack()
        tk.Label(badge_dist, text=f"{distancia}m", font=("Segoe UI", 12, "bold"), bg="#ecfdf5", fg="#10b981").pack()
        
        # Badge Tempo
        badge_tempo = tk.Frame(frame_badges, bg="#f0f9ff", bd=0, highlightbackground="#0284c7", highlightthickness=1, padx=10, pady=8)
        badge_tempo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(badge_tempo, text="⏱️ Tempo", font=self.fonte_normal, bg="#f0f9ff", fg="#0284c7").pack()
        tk.Label(badge_tempo, text=f"{tempo} min", font=("Segoe UI", 12, "bold"), bg="#f0f9ff", fg="#0284c7").pack()
        
        # Badge Calorias
        badge_cal = tk.Frame(frame_badges, bg="#fef2f2", bd=0, highlightbackground="#ef4444", highlightthickness=1, padx=10, pady=8)
        badge_cal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(badge_cal, text="🔥 Calorias", font=self.fonte_normal, bg="#fef2f2", fg="#ef4444").pack()
        tk.Label(badge_cal, text=f"{calorias} kcal", font=("Segoe UI", 12, "bold"), bg="#fef2f2", fg="#ef4444").pack()
        
        lbl_passos_titulo = tk.Label(self.card_resultados, text="👣 Sequência de Percurso:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text)
        lbl_passos_titulo.pack(anchor=tk.W, pady=(10, 5))
        
        frame_passos_container = tk.Frame(self.card_resultados, bg=self.cor_card)
        frame_passos_container.pack(fill=tk.BOTH, expand=True)
        
        canvas_passos = tk.Canvas(frame_passos_container, bg=self.cor_card, highlightthickness=0)
        scroll_passos = ttk.Scrollbar(frame_passos_container, orient="vertical", command=canvas_passos.yview)
        frame_passos = tk.Frame(canvas_passos, bg=self.cor_card)
        
        frame_passos.bind("<Configure>", lambda e: canvas_passos.configure(scrollregion=canvas_passos.bbox("all")))
        canvas_passos.create_window((0, 0), window=frame_passos, anchor="nw")
        canvas_passos.configure(yscrollcommand=scroll_passos.set)
        
        canvas_passos.pack(side="left", fill="both", expand=True)
        scroll_passos.pack(side="right", fill="y")
        
        for i, seg in enumerate(caminho, 1):
            lbl_passo = tk.Label(frame_passos, text=f"{i}. {seg.get_origem().replace('_', ' ')} ➡️ {seg.get_destino().replace('_', ' ')} ({seg.get_distancia()}m)", 
                                 font=self.fonte_normal, bg=self.cor_card, fg=self.cor_text, anchor="w", justify="left")
            lbl_passo.pack(anchor=tk.W, pady=3)

    # =========================================================================
    # TAB: UTILIZADORES
    # =========================================================================
    def _setup_tab_utilizadores(self):
        # Canvas de scroll para acomodar os cards de forma limpa
        canvas = tk.Canvas(self.tab_utilizadores, bg=self.cor_bg, highlightthickness=0)
        scroll = ttk.Scrollbar(self.tab_utilizadores, orient="vertical", command=canvas.yview)
        
        content = tk.Frame(canvas, bg=self.cor_bg)
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=content, anchor="nw", width=900) 
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        content.columnconfigure(0, weight=1)
        
        # CARD 1: Adicionar Utilizador
        card_add = self.criar_card_frame(content, padding=20)
        card_add.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        card_add.columnconfigure(1, weight=1)
        
        lbl_add_title = tk.Label(card_add, text="➕ Registar Novo Utilizador", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_add_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        tk.Label(card_add, text="Nome Completo:", font=self.fonte_bold, bg=self.cor_card).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.entry_nome = ttk.Entry(card_add, font=self.fonte_normal)
        self.entry_nome.grid(row=1, column=1, sticky="ew", pady=8, padx=(15, 0))
        
        tk.Label(card_add, text="Idade:", font=self.fonte_bold, bg=self.cor_card).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.entry_idade = ttk.Entry(card_add, font=self.fonte_normal, width=12)
        self.entry_idade.grid(row=2, column=1, sticky="w", pady=8, padx=(15, 0))
        
        tk.Label(card_add, text="Género / Sexo:", font=self.fonte_bold, bg=self.cor_card).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.cb_sexo = ttk.Combobox(card_add, values=["M", "F", "OUTRO"], state="readonly", font=self.fonte_normal, width=12)
        self.cb_sexo.grid(row=3, column=1, sticky="w", pady=8, padx=(15, 0))
        self.cb_sexo.current(0)
        
        tk.Label(card_add, text="Perfil Clínico:", font=self.fonte_bold, bg=self.cor_card).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.cb_perfil = ttk.Combobox(card_add, values=PERFIS_VALIDOS, state="readonly", font=self.fonte_normal)
        self.cb_perfil.grid(row=4, column=1, sticky="ew", pady=8, padx=(15, 0))
        self.cb_perfil.current(1)
        
        btn_reg = self.criar_botao_moderno(card_add, "Registar Utilizador", self.acao_adicionar_utilizador, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover)
        btn_reg.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        
        # CARD 2: Pesquisa, Edição e Remoção
        card_pesquisa = self.criar_card_frame(content, padding=20)
        card_pesquisa.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        card_pesquisa.columnconfigure(1, weight=1)
        
        lbl_pesquisa_title = tk.Label(card_pesquisa, text="🔍 Gestão & Consulta de Perfil", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_pesquisa_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        tk.Label(card_pesquisa, text="ID do Utilizador:", font=self.fonte_bold, bg=self.cor_card).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.entry_pesquisa_id = ttk.Entry(card_pesquisa, font=self.fonte_normal, width=20)
        self.entry_pesquisa_id.grid(row=1, column=1, sticky="w", pady=8, padx=(15, 0))
        
        btn_frame = tk.Frame(card_pesquisa, bg=self.cor_card)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0), sticky="ew")
        
        self.criar_botao_moderno(btn_frame, "👤 Ver Perfil", self.acao_procurar_user, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame, "📜 Ver Histórico", self.acao_historico_user, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame, "✏️ Editar Perfil", self.acao_editar_user, bg=self.cor_primary, hover_bg=self.cor_primary_hover).pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame, "📄 Exportar CSV", self.acao_exportar_csv_user, bg="#8b5cf6", hover_bg="#7c3aed").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame, "❌ Remover", self.acao_remover_user, bg=self.cor_danger, hover_bg=self.cor_danger_hover).pack(side=tk.LEFT, padx=5)
        
        # CARD 3: Consulta Geral
        card_geral = self.criar_card_frame(content, padding=20)
        card_geral.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        lbl_geral_title = tk.Label(card_geral, text="📋 Análise e Consulta Geral", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_geral_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        btn_frame3 = tk.Frame(card_geral, bg=self.cor_card)
        btn_frame3.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.criar_botao_moderno(btn_frame3, "Listar Todos Utilizadores", self.acao_listar_utilizadores, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame3, "📊 Gráfico: Perfis Clínicos", self.acao_mostrar_grafico_utilizadores, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover).pack(side=tk.LEFT, padx=5)

    # =========================================================================
    # TAB: MAPA & REDE
    # =========================================================================
    def _setup_tab_mapa(self):
        card = self.criar_card_frame(self.tab_mapa)
        card.pack(fill=tk.BOTH, expand=True)
        
        lbl_title = tk.Label(card, text="🗺️ Exploração e Configuração da Rede Urbana", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Grupo 1: Visualizações
        frame_vis = tk.LabelFrame(card, text=" Visualização da Cidade ", bg=self.cor_card, font=self.fonte_bold, fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_vis.pack(fill=tk.X, pady=10, ipady=10, ipadx=10)
        
        btn_frame_vis = tk.Frame(frame_vis, bg=self.cor_card)
        btn_frame_vis.pack(padx=15, pady=10, fill=tk.X)
        
        self.criar_botao_moderno(btn_frame_vis, "🗺️ Abrir Mapa Gráfico Interativo", self.acao_mostrar_mapa_grafico, bg=self.cor_primary, hover_bg=self.cor_primary_hover).pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_vis, "📍 Listar Pontos Existentes", self.acao_listar_pontos, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_vis, "🛣️ Listar Percursos Base", self.acao_listar_percursos, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        
        # Grupo 2: Gestão da Rede
        frame_gestao = tk.LabelFrame(card, text=" Modificar a Rede e Condições Urbanas ", bg=self.cor_card, font=self.fonte_bold, fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_gestao.pack(fill=tk.X, pady=15, ipady=10, ipadx=10)
        
        btn_frame_gestao = tk.Frame(frame_gestao, bg=self.cor_card)
        btn_frame_gestao.pack(padx=15, pady=10, fill=tk.X)
        
        self.criar_botao_moderno(btn_frame_gestao, "➕ Adicionar Percurso", self.janela_adicionar_percurso, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover).pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_gestao, "❌ Remover Percurso", self.janela_remover_percurso, bg=self.cor_danger, hover_bg=self.cor_danger_hover).pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_gestao, "🎲 Simular Acidentes", self.acao_gerar_acidentes_aleatorios, bg="#f59e0b", hover_bg="#d97706").pack(side=tk.LEFT, padx=5)
        
        self.btn_clima = self.criar_botao_moderno(btn_frame_gestao, "🌤️ Mudar Clima (Atual: Sol)", self.acao_mudar_clima, bg="#0ea5e9", hover_bg="#0284c7")
        self.btn_clima.pack(side=tk.LEFT, padx=5)

    # =========================================================================
    # TAB: FICHEIROS & ESTATÍSTICAS
    # =========================================================================
    def _setup_tab_ficheiros(self):
        card = self.criar_card_frame(self.tab_ficheiros)
        card.pack(fill=tk.BOTH, expand=True)
        
        lbl_title = tk.Label(card, text="💾 Gestão de Ficheiros & Auditoria de Viagens", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary)
        lbl_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Top frame for side-by-side Persistência & Estatísticas
        frame_topo = tk.Frame(card, bg=self.cor_card)
        frame_topo.pack(fill=tk.X, pady=(0, 10))
        frame_topo.columnconfigure(0, weight=1)
        frame_topo.columnconfigure(1, weight=1)
        
        # Grupo 1: Ficheiros
        frame_fich = tk.LabelFrame(frame_topo, text=" Persistência de Dados (JSON) ", bg=self.cor_card, font=self.fonte_bold, fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_fich.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        
        lbl_info = tk.Label(frame_fich, text="Suporta importação e exportação completa dos perfis e históricos.", font=self.fonte_normal, bg=self.cor_card, fg=self.cor_muted)
        lbl_info.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        btn_frame_fich = tk.Frame(frame_fich, bg=self.cor_card)
        btn_frame_fich.pack(padx=15, fill=tk.X, pady=(0, 5))
        
        self.criar_botao_moderno(btn_frame_fich, "⬇️ Importar JSON", self.acao_ler_json, bg=self.cor_primary, hover_bg=self.cor_primary_hover).pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_fich, "⬆️ Exportar JSON", self.acao_gravar_json, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover).pack(side=tk.LEFT, padx=5)
        
        # Grupo 2: Estatísticas
        frame_est = tk.LabelFrame(frame_topo, text=" Auditorias e Estatísticas ", bg=self.cor_card, font=self.fonte_bold, fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_est.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        
        lbl_info_est = tk.Label(frame_est, text="Consulte logs detalhados e tendências de percursos.", font=self.fonte_normal, bg=self.cor_card, fg=self.cor_muted)
        lbl_info_est.pack(anchor=tk.W, padx=15, pady=(5, 10))
        
        btn_frame_est = tk.Frame(frame_est, bg=self.cor_card)
        btn_frame_est.pack(padx=15, fill=tk.X, pady=(0, 5))
        
        self.criar_botao_moderno(btn_frame_est, "🔍 Raio-X da Cidade", self.acao_raio_x_cidade, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        self.criar_botao_moderno(btn_frame_est, "📈 Populares", self.acao_estatisticas_percursos, bg="#475569", hover_bg="#334155").pack(side=tk.LEFT, padx=5)
        
        # Grupo 3: Histórico de Viagens Global (Auditoria)
        frame_auditoria = tk.LabelFrame(card, text=" Tabela de Histórico Global & Auditoria em Tempo Real ", bg=self.cor_card, font=self.fonte_bold, fg=self.cor_primary, bd=0, relief="flat", highlightbackground="#e2e8f0", highlightthickness=1)
        frame_auditoria.pack(fill=tk.BOTH, expand=True, pady=10, ipady=5, ipadx=10)
        
        frame_busca = tk.Frame(frame_auditoria, bg=self.cor_card)
        frame_busca.pack(fill=tk.X, padx=15, pady=(5, 5))
        
        tk.Label(frame_busca, text="🔍 Filtrar Viagens:", font=self.fonte_bold, bg=self.cor_card, fg=self.cor_text).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busca_historico = ttk.Entry(frame_busca, font=self.fonte_normal, width=40)
        self.entry_busca_historico.pack(side=tk.LEFT)
        self.entry_busca_historico.bind("<KeyRelease>", self._filtrar_historico)
        
        frame_tabela = tk.Frame(frame_auditoria, bg=self.cor_card)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        colunas = ("id_nome", "origem", "destino", "modo", "custo")
        self.tree_historico = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=8)
        
        self.tree_historico.heading("id_nome", text="Utilizador ID / Nome", command=lambda: self._ordenar_coluna("id_nome", False))
        self.tree_historico.heading("origem", text="Origem", command=lambda: self._ordenar_coluna("origem", False))
        self.tree_historico.heading("destino", text="Destino", command=lambda: self._ordenar_coluna("destino", False))
        self.tree_historico.heading("modo", text="Modo", command=lambda: self._ordenar_coluna("modo", False))
        self.tree_historico.heading("custo", text="Custo", command=lambda: self._ordenar_coluna("custo", False))
        
        self.tree_historico.column("id_nome", width=250, anchor="w")
        self.tree_historico.column("origem", width=150, anchor="center")
        self.tree_historico.column("destino", width=150, anchor="center")
        self.tree_historico.column("modo", width=120, anchor="center")
        self.tree_historico.column("custo", width=100, anchor="e")
        
        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scroll_y.set)
        
        self.tree_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carregar inicialmente
        self._carregar_historico_global()

    def _carregar_historico_global(self, filtro=""):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
            
        filtro = filtro.lower()
        users = self.utilizadores.listar_todos()
        
        for u in users:
            id_nome = f"[{u.get_id()}] {u.get_nome()}"
            for origem, destino, modo, custo in u.get_historico():
                match = (not filtro) or (
                    filtro in id_nome.lower() or
                    filtro in origem.lower() or
                    filtro in destino.lower() or
                    filtro in modo.lower() or
                    filtro in str(custo)
                )
                if match:
                    custo_str = f"{custo:.2f}" if isinstance(custo, (int, float)) else str(custo)
                    self.tree_historico.insert("", "end", values=(
                        id_nome,
                        origem.replace("_", " "),
                        destino.replace("_", " "),
                        modo.replace("_", " "),
                        custo_str
                    ))

    def _filtrar_historico(self, event=None):
        filtro = self.entry_busca_historico.get()
        self._carregar_historico_global(filtro)

    def _ordenar_coluna(self, col, reverse):
        dados = [(self.tree_historico.set(k, col), k) for k in self.tree_historico.get_children("")]
        
        if col == "custo":
            try:
                dados.sort(key=lambda t: float(t[0]), reverse=reverse)
            except ValueError:
                dados.sort(reverse=reverse)
        else:
            dados.sort(reverse=reverse)
            
        for index, (val, k) in enumerate(dados):
            self.tree_historico.move(k, "", index)
            
        self.tree_historico.heading(col, command=lambda: self._ordenar_coluna(col, not reverse))

    # =========================================================================
    # AÇÕES: RECOMENDAÇÃO
    # =========================================================================
    def acao_recomendar(self):
        origem = self.cb_origem.get()
        destino = self.cb_destino.get()
        id_user = self.entry_user_id_rec.get().strip()
        modo1 = self.modo_principal_sel
        modo2_val = self.modo_secundario_sel
        modo = modo1 if modo2_val in ["Nenhum", modo1] else f"{modo1}+{modo2_val}"
        acompanhante = self.cb_acompanhante.get()
        
        if not id_user:
            messagebox.showwarning("Aviso", "Por favor, introduz o ID do utilizador.")
            return
        user = self.utilizadores.procurar(id_user)
        if not user:
            messagebox.showerror("Erro", f"Utilizador '{id_user}' não encontrado.")
            return
        if origem == destino:
            print("⚠️ Origem e destino são idênticos.")
            return
            
        print(f"\n🔍 A procurar rota de {origem} para {destino} ({modo}) [Clima: {self.clima}]...")
        caminho, custo = self.motor_recomendacao.encontrar_melhor_caminho(self.rede, origem, destino, user, modo, acompanhante, self.clima)
        
        if caminho:
            self.ultima_rota_calculada = caminho
            print(f"✅ Rota Otimizada Encontrada! Custo final: {custo}")
            distancia_total = sum(seg.get_distancia() for seg in caminho)
            inclinacao_abs = sum(abs(seg.get_inclinacao()) for seg in caminho)
            
            # Cálculo de Tempo
            velocidade_kmh = 4.0
            if "trabalho" in modo:
                velocidade_kmh = 5.5  # Passo apressado para ir para o trabalho
            if user.get_perfil() in ["idoso", "pessoa com mobilidade reduzida"]:
                if "trabalho" in modo:
                    velocidade_kmh = 3.5  # Mesmo idosos apressam o passo para o trabalho
                else:
                    velocidade_kmh -= 1.5
            if acompanhante in ["Cadeira de Rodas", "Andarilho"]:
                if "trabalho" in modo:
                    velocidade_kmh = max(1.5, velocidade_kmh - 0.5)
                else:
                    velocidade_kmh -= 1.0
            velocidade_kmh = max(1.0, velocidade_kmh)
            
            tempo_horas = (distancia_total / 1000.0) / velocidade_kmh
            tempo_minutos = int(tempo_horas * 60)
            
            # Cálculo de Calorias
            calorias_base = (distancia_total / 1000.0) * 50
            if modo == "exercicio": calorias_base *= 1.5
            calorias_base += inclinacao_abs * 2 
            calorias = int(calorias_base)
            
            print(f"⏱️ Tempo Estimado: ~{tempo_minutos} min | 🔥 Calorias: ~{calorias} kcal | 📏 Distância: {distancia_total}m")
            for i, seg in enumerate(caminho, 1):
                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m)")
            user.adicionar_historico(origem, destino, modo, custo)
            self.acao_gravar_json_silencioso() 
            
            # Atualizar os cards de resultados na tela
            try:
                self._atualizar_resultados_rota(distancia_total, tempo_minutos, calorias, caminho)
                self._carregar_historico_global()
            except Exception as e:
                print(f"⚠️ Erro ao atualizar painel visual: {e}")
        else:
            print(f"❌ Sem rota viável de {origem} para {destino}.")
            try:
                self._mostrar_erro_resultados(origem, destino)
            except Exception as e:
                print(f"⚠️ Erro ao mostrar erro visual: {e}")

    def acao_ver_segmento(self):
        origem = self.cb_origem.get()
        destino = self.cb_destino.get()
        segmento_encontrado = None
        for seg in self.rede.obter_conexoes(origem):
            if seg.get_destino() == destino:
                segmento_encontrado = seg
                break
        View.mostrar_detalhes_segmento(origem, destino, segmento_encontrado)

    def _desenhar_mapa_no_canvas(self, canvas, rota=None):
        canvas.delete("all")
        
        coords = {
            "Praca_Republica": (450, 400), "Avenida_Liberdade": (450, 500), "Se_Braga": (350, 420),
            "Jardim_Santa_Barbara": (400, 320), "Estacao_Comboios": (200, 400), "Estadio_Municipal": (200, 150),
            "Braga_Parque": (600, 250), "UMinho_Gualtar": (750, 200), "Hospital_Braga": (700, 100),
            "Bom_Jesus": (800, 400), "Santuario_Sameiro": (800, 550)
        }
        
        pontos = self.rede.listar_pontos()
        raio = 250
        centro = (450, 350)
        angle_step = 2 * math.pi / max(1, len(pontos))
        
        for i, ponto in enumerate(pontos):
            if ponto not in coords:
                angle = i * angle_step
                x = centro[0] + raio * math.cos(angle)
                y = centro[1] + raio * math.sin(angle)
                coords[ponto] = (x, y)
                
        # 1. Desenhar a rede base de ruas (GPS style double-line)
        ruas_vistas = set()
        for origem, conexoes in self.rede._grafo.items():
            for seg in conexoes:
                destino = seg.get_destino()
                id_rua = tuple(sorted([origem, destino]))
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    x1, y1 = coords[origem]
                    x2, y2 = coords[destino]
                    
                    street_tag = f"street_{origem}_{destino}"
                    
                    if seg.get_acidente():
                        # Click target invisible thicker line
                        target_id = canvas.create_line(x1, y1, x2, y2, fill="", width=12, tags=(street_tag, "street_target"))
                        canvas.tag_bind(target_id, "<Button-1>", lambda event, o=origem, d=destino, c=canvas, r=rota: self._on_street_click(o, d, c, r))
                        
                        canvas.create_line(x1, y1, x2, y2, fill="#ef4444", width=4, dash=(6, 4), tags=(street_tag, "street"))
                        mx, my = (x1+x2)/2, (y1+y2)/2
                        canvas.create_text(mx, my, text="⛔", font=("Segoe UI", 16), tags=(street_tag, "street"))
                    else:
                        target_id = canvas.create_line(x1, y1, x2, y2, fill="", width=12, tags=(street_tag, "street_target"))
                        canvas.tag_bind(target_id, "<Button-1>", lambda event, o=origem, d=destino, c=canvas, r=rota: self._on_street_click(o, d, c, r))
                        
                        canvas.create_line(x1, y1, x2, y2, fill="#1e293b", width=5, tags=(street_tag, "street"))
                        canvas.create_line(x1, y1, x2, y2, fill="#334155", width=2, tags=(street_tag, "street"))
                        
        # 2. Desenhar a rota otimizada se fornecida (Glow neon)
        if rota:
            for seg in rota:
                if seg.get_origem() in coords and seg.get_destino() in coords:
                    x1, y1 = coords[seg.get_origem()]
                    x2, y2 = coords[seg.get_destino()]
                    canvas.create_line(x1, y1, x2, y2, fill="#0ea5e9", width=9)
                    canvas.create_line(x1, y1, x2, y2, fill="#22c55e", width=5, arrow=tk.LAST, arrowshape=(16, 20, 6))
                    
        # 3. Desenhar nós com efeito de anel concêntrico e badges escuros
        for ponto, (x, y) in coords.items():
            cor_no = "#3b82f6" 
            if rota:
                if ponto == rota[0].get_origem():
                    cor_no = "#10b981" 
                elif ponto == rota[-1].get_destino():
                    cor_no = "#0ea5e9" 
            
            node_tag = f"node_{ponto}"
            # Anéis
            outer_id = canvas.create_oval(x - 13, y - 13, x + 13, y + 13, fill="#1e293b", outline="#334155", width=1, tags=(node_tag, "node"))
            canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill=cor_no, outline="#ffffff", width=2, tags=(node_tag, "node"))
            
            # Badge de Texto
            nome_limpo = ponto.replace("_", " ")
            text_id = canvas.create_text(x, y - 24, text=nome_limpo, font=("Segoe UI", 9, "bold"), fill="#0f172a", tags=(node_tag, "node"))
            bbox = canvas.bbox(text_id)
            if bbox:
                bg_id = canvas.create_rectangle(bbox[0]-6, bbox[1]-2, bbox[2]+6, bbox[3]+2, fill="#ffffff", outline="#cbd5e1", width=1, tags=(node_tag, "node"))
                canvas.tag_lower(bg_id, text_id)
                
            # Bindings para os nós (Left Click -> Origem, Right Click -> Destino, Hover -> Tooltip)
            canvas.tag_bind(node_tag, "<Button-1>", lambda event, p=ponto, c=canvas: self._on_node_left_click(p, c))
            canvas.tag_bind(node_tag, "<Button-3>", lambda event, p=ponto, c=canvas: self._on_node_right_click(p, c))
            canvas.tag_bind(node_tag, "<Button-2>", lambda event, p=ponto, c=canvas: self._on_node_right_click(p, c))
            
            # Tooltip trigger apenas no anel externo para evitar piscadas
            canvas.tag_bind(outer_id, "<Enter>", lambda event, p=ponto, c=canvas: self._on_node_enter(event, p, c))
            canvas.tag_bind(outer_id, "<Leave>", lambda event, c=canvas: self._on_node_leave(event, c))
                
        # 4. Legenda flutuante no mapa (Mais pequena e elegante)
        canvas.create_rectangle(15, 15, 155, 96, fill="#ffffff", outline="#cbd5e1", width=1)
        canvas.create_text(22, 26, text="Legenda", font=("Segoe UI", 8, "bold"), fill="#0f172a", anchor="w")
        
        # Partida (Origem)
        canvas.create_oval(22-3, 43-3, 22+3, 43+3, fill="#10b981", outline="white", width=1)
        canvas.create_text(32, 43, text="Partida (Origem)", font=("Segoe UI", 7), fill="#475569", anchor="w")
        
        # Chegada (Destino)
        canvas.create_oval(22-3, 57-3, 22+3, 57+3, fill="#0ea5e9", outline="white", width=1)
        canvas.create_text(32, 57, text="Chegada (Destino)", font=("Segoe UI", 7), fill="#475569", anchor="w")
        
        # Nós de Passagem
        canvas.create_oval(22-3, 71-3, 22+3, 71+3, fill="#3b82f6", outline="white", width=1)
        canvas.create_text(32, 71, text="Nós de Passagem", font=("Segoe UI", 7), fill="#475569", anchor="w")
        
        # Rua Bloqueada
        canvas.create_line(16, 85, 28, 85, fill="#ef4444", width=2, dash=(3,1))
        canvas.create_text(32, 85, text="⛔ Rua Bloqueada", font=("Segoe UI", 7), fill="#475569", anchor="w")

    def _on_node_left_click(self, ponto, canvas):
        try:
            self.cb_origem.set(ponto)
            print(f"📍 Origem definida no mapa para: {ponto.replace('_', ' ')}")
        except Exception as e:
            print(f"❌ Erro ao definir origem: {e}")

    def _on_node_right_click(self, ponto, canvas):
        try:
            self.cb_destino.set(ponto)
            print(f"🏁 Destino definido no mapa para: {ponto.replace('_', ' ')}")
        except Exception as e:
            print(f"❌ Erro ao definir destino: {e}")

    def _on_street_click(self, origem, destino, canvas, rota):
        current_state = False
        for seg in self.rede.obter_conexoes(origem):
            if seg.get_destino() == destino:
                current_state = seg.get_acidente()
                break
                
        acao = "desbloquear" if current_state else "bloquear por acidente"
        msg = f"Deseja {acao} a rua entre '{origem.replace('_', ' ')}' e '{destino.replace('_', ' ')}'?"
        if messagebox.askyesno("Confirmar Bloqueio/Desbloqueio", msg):
            if not current_state:
                # Testar se bloquear causa desconectividade na rede
                self.rede.reportar_acidente(origem, destino, True)
                if not self.rede.verificar_conectividade_sem_acidentes():
                    # Reverter imediatamente
                    self.rede.reportar_acidente(origem, destino, False)
                    messagebox.showwarning(
                        "⚠️ Acesso Bloqueado", 
                        f"Não é possível bloquear esta rua! Ela é a única ligação viável restante para ligar Braga e manter todos os pontos acessíveis."
                    )
                    return
            else:
                self.rede.reportar_acidente(origem, destino, False)
                
            self._desenhar_mapa_no_canvas(canvas, rota)
            status_txt = "BLOQUEADA" if not current_state else "DESBLOQUEADA"
            print(f"⛔ Rua {origem.replace('_', ' ')} <-> {destino.replace('_', ' ')} está agora {status_txt}!")

    def _on_node_enter(self, event, ponto, canvas):
        if canvas.find_withtag("tooltip"):
            canvas.delete("tooltip")
            
        conexoes = self.rede.obter_conexoes(ponto)
        links = []
        for seg in conexoes:
            status = "⛔" if seg.get_acidente() else "🟢"
            links.append(f"{status} {seg.get_destino().replace('_', ' ')} ({seg.get_distancia()}m)")
            
        texto_tooltip = f"📍 {ponto.replace('_', ' ')}\n" + ("Conexões de saída:\n" + "\n".join(links) if links else "Sem conexões de saída.")
        
        cx = event.x
        cy = event.y
        tx = cx + 15
        ty = cy + 15
        
        t_id = canvas.create_text(tx, ty, text=texto_tooltip, font=("Segoe UI", 9), fill="#0f172a", justify="left", anchor="nw", tags="tooltip")
        bbox = canvas.bbox(t_id)
        if bbox:
            bg_id = canvas.create_rectangle(bbox[0]-8, bbox[1]-6, bbox[2]+8, bbox[3]+6, fill="#ffffff", outline="#8b5cf6", width=1, tags="tooltip")
            canvas.tag_lower(bg_id, t_id)

    def _on_node_leave(self, event, canvas):
        canvas.delete("tooltip")

    def acao_ver_rota_mapa(self):
        if not hasattr(self, 'ultima_rota_calculada') or not self.ultima_rota_calculada:
            messagebox.showwarning("Aviso", "Por favor, calcula uma rota primeiro.")
            return
            
        if hasattr(self, 'mapa_janela') and self.mapa_janela.winfo_exists():
            self.mapa_janela.lift()
            self.mapa_janela.title("🗺️ Visualização da Rota Calculada")
            self._desenhar_mapa_no_canvas(self.mapa_canvas, self.ultima_rota_calculada)
            return
            
        self.mapa_janela = tk.Toplevel(self)
        self.mapa_janela.title("🗺️ Visualização da Rota Calculada")
        self.mapa_janela.geometry("950x720")
        self.mapa_janela.configure(bg=self.cor_bg)
        self.mapa_janela.columnconfigure(0, weight=1)
        self.mapa_janela.rowconfigure(0, weight=1)
        
        self.mapa_canvas = tk.Canvas(self.mapa_janela, bg=self.cor_bg, highlightthickness=0)
        self.mapa_canvas.grid(row=0, column=0, sticky="nsew")
        
        self._desenhar_mapa_no_canvas(self.mapa_canvas, self.ultima_rota_calculada)

    # =========================================================================
    # AÇÕES: UTILIZADORES
    # =========================================================================
    def janela_novo_utilizador_rapido(self):
        w = tk.Toplevel(self)
        w.title("Criar Novo Utilizador")
        w.geometry("420x350")
        w.configure(bg=self.cor_bg)
        
        frame = self.criar_card_frame(w, padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        frame.columnconfigure(1, weight=1)
        
        tk.Label(frame, text="Registo Rápido", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        tk.Label(frame, text="Nome Completo:", font=self.fonte_bold, bg=self.cor_card).grid(row=1, column=0, sticky=tk.W, pady=8)
        e_nome = ttk.Entry(frame, font=self.fonte_normal)
        e_nome.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))
        
        tk.Label(frame, text="Idade:", font=self.fonte_bold, bg=self.cor_card).grid(row=2, column=0, sticky=tk.W, pady=8)
        e_idade = ttk.Entry(frame, font=self.fonte_normal, width=12)
        e_idade.grid(row=2, column=1, sticky="w", pady=8, padx=(10, 0))
        
        tk.Label(frame, text="Sexo / Género:", font=self.fonte_bold, bg=self.cor_card).grid(row=3, column=0, sticky=tk.W, pady=8)
        cb_sexo = ttk.Combobox(frame, values=["M", "F", "OUTRO"], state="readonly", font=self.fonte_normal, width=12)
        cb_sexo.grid(row=3, column=1, sticky="w", pady=8, padx=(10, 0))
        cb_sexo.current(0)
        
        tk.Label(frame, text="Perfil Clínico:", font=self.fonte_bold, bg=self.cor_card).grid(row=4, column=0, sticky=tk.W, pady=8)
        cb_perfil = ttk.Combobox(frame, values=PERFIS_VALIDOS, state="readonly", font=self.fonte_normal)
        cb_perfil.grid(row=4, column=1, sticky="ew", pady=8, padx=(10, 0))
        cb_perfil.current(1)
        
        def gravar():
            nome = e_nome.get().strip()
            idade_str = e_idade.get().strip()
            if not nome or not idade_str:
                messagebox.showwarning("Aviso", "Preenche o nome e a idade.")
                return
            try:
                idade = int(idade_str)
                novo_id = gerar_id_unico(self.utilizadores)
                novo_user = Utilizador(novo_id, nome, idade, cb_sexo.get(), cb_perfil.get())
                self.utilizadores.inserir(novo_user)
                self.entry_user_id_rec.delete(0, tk.END)
                self.entry_user_id_rec.insert(0, novo_id)
                print(f"✅ Utilizador Rápido '{nome}' adicionado com ID: {novo_id}")
                w.destroy()
            except ValueError as e:
                messagebox.showerror("Erro", f"Erro nos dados: {e}")
                
        btn_gravar = self.criar_botao_moderno(frame, "Guardar & Usar", gravar, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover)
        btn_gravar.grid(row=5, column=0, columnspan=2, pady=(20, 0))

    def acao_adicionar_utilizador(self):
        nome = self.entry_nome.get().strip()
        idade_str = self.entry_idade.get().strip()
        sexo = self.cb_sexo.get()
        perfil = self.cb_perfil.get()
        if not nome or not idade_str:
            messagebox.showwarning("Aviso", "Preenche todos os campos.")
            return
        try:
            idade = int(idade_str)
            novo_id = gerar_id_unico(self.utilizadores)
            novo_user = Utilizador(novo_id, nome, idade, sexo, perfil)
            self.utilizadores.inserir(novo_user)
            print(f"✅ Utilizador '{nome}' adicionado com sucesso (ID: {novo_id}).")
            self.entry_nome.delete(0, tk.END)
            self.entry_idade.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {e}")
            
    def acao_procurar_user(self):
        id_user = self.entry_pesquisa_id.get().strip()
        u = self.utilizadores.procurar(id_user)
        if u: View.mostrar_perfil(u)
        else: print(f"❌ Utilizador {id_user} não encontrado.")

    def acao_historico_user(self):
        id_user = self.entry_pesquisa_id.get().strip()
        u = self.utilizadores.procurar(id_user)
        if u: View.mostrar_historico(u)
        else: print(f"❌ Utilizador {id_user} não encontrado.")

    def acao_editar_user(self):
        id_user = self.entry_pesquisa_id.get().strip()
        u = self.utilizadores.procurar(id_user)
        if not u:
            messagebox.showerror("Erro", "Utilizador não encontrado.")
            return
            
        w = tk.Toplevel(self)
        w.title(f"Editar Utilizador: {id_user}")
        w.geometry("420x350")
        w.configure(bg=self.cor_bg)
        
        frame = self.criar_card_frame(w, padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        frame.columnconfigure(1, weight=1)
        
        tk.Label(frame, text=f"Editar Perfil: {id_user}", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        tk.Label(frame, text="Nome Completo:", font=self.fonte_bold, bg=self.cor_card).grid(row=1, column=0, sticky=tk.W, pady=8)
        e_nome = ttk.Entry(frame, font=self.fonte_normal)
        e_nome.insert(0, u.get_nome())
        e_nome.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))
        
        tk.Label(frame, text="Idade:", font=self.fonte_bold, bg=self.cor_card).grid(row=2, column=0, sticky=tk.W, pady=8)
        e_idade = ttk.Entry(frame, font=self.fonte_normal, width=12)
        e_idade.insert(0, str(u.get_idade()))
        e_idade.grid(row=2, column=1, sticky="w", pady=8, padx=(10, 0))
        
        tk.Label(frame, text="Sexo / Género:", font=self.fonte_bold, bg=self.cor_card).grid(row=3, column=0, sticky=tk.W, pady=8)
        cb_sexo = ttk.Combobox(frame, values=["M", "F", "OUTRO"], state="readonly", font=self.fonte_normal, width=12)
        cb_sexo.set(u.get_sexo())
        cb_sexo.grid(row=3, column=1, sticky="w", pady=8, padx=(10, 0))
        
        tk.Label(frame, text="Perfil Clínico:", font=self.fonte_bold, bg=self.cor_card).grid(row=4, column=0, sticky=tk.W, pady=8)
        cb_perfil = ttk.Combobox(frame, values=PERFIS_VALIDOS, state="readonly", font=self.fonte_normal)
        cb_perfil.set(u.get_perfil())
        cb_perfil.grid(row=4, column=1, sticky="ew", pady=8, padx=(10, 0))
        
        def gravar():
            nome = e_nome.get().strip()
            idade_str = e_idade.get().strip()
            if not nome or not idade_str:
                messagebox.showwarning("Aviso", "Preenche o nome e a idade.")
                return
            try:
                idade = int(idade_str)
                u._nome = nome
                u._idade = idade
                u._sexo = cb_sexo.get()
                u._perfil = cb_perfil.get()
                self.acao_gravar_json_silencioso()
                print(f"✅ Utilizador '{nome}' editado com sucesso e guardado de forma permanente!")
                w.destroy()
            except ValueError as e:
                messagebox.showerror("Erro", f"Dados inválidos: {e}")
                
        btn_salvar = self.criar_botao_moderno(frame, "Guardar Alterações", gravar, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=(20, 0))

    def acao_exportar_csv_user(self):
        id_user = self.entry_pesquisa_id.get().strip()
        u = self.utilizadores.procurar(id_user)
        if not u:
            messagebox.showerror("Erro", "Utilizador não encontrado.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            initialfile=f"relatorio_{u.get_nome().replace(' ', '_')}.csv",
            filetypes=[("CSV", "*.csv")], 
            title="Exportar Relatório"
        )
        if not filename: return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["RELATÓRIO CLÍNICO/HISTÓRICO - BRAGA SAUDÁVEL"])
                writer.writerow(["ID", u.get_id()])
                writer.writerow(["Nome", u.get_nome()])
                writer.writerow(["Idade", u.get_idade()])
                writer.writerow(["Sexo", u.get_sexo()])
                writer.writerow(["Perfil", u.get_perfil().title()])
                writer.writerow([])
                writer.writerow(["Histórico de Viagens"])
                writer.writerow(["Origem", "Destino", "Modo", "Custo (Penalizações)"])
                
                for h in u.get_historico():
                    if len(h) == 4:
                        writer.writerow([h[0], h[1], h[2], h[3]])
                        
            print(f"✅ Relatório de {u.get_nome()} exportado com sucesso para '{filename}'.")
            messagebox.showinfo("Sucesso", f"Relatório CSV exportado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar CSV: {e}")

    def acao_remover_user(self):
        id_user = self.entry_pesquisa_id.get().strip()
        u = self.utilizadores.procurar(id_user)
        if not u:
            messagebox.showerror("Erro", "Utilizador não encontrado.")
            return
        if messagebox.askyesno("Confirmar Remoção", f"Remover o utilizador {u.get_nome()}?"):
            self.utilizadores.remover(id_user)
            print(f"✅ Utilizador {id_user} removido com sucesso.")

    def acao_listar_utilizadores(self):
        todos = self.utilizadores.listar_todos()
        print(f"\n--- Lista de Utilizadores ({len(todos)}) ---")
        for u in todos: print(u)

    def acao_mostrar_grafico_utilizadores(self):
        janela = tk.Toplevel(self)
        janela.title("Estatísticas: Perfis Clínicos")
        janela.geometry("620x450")
        janela.configure(bg="#ffffff")
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(janela, bg="#ffffff", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        todos = self.utilizadores.listar_todos()
        if not todos:
            canvas.create_text(310, 225, text="Sem dados de utilizadores para exibir.", font=("Segoe UI", 12, "bold"), fill=self.cor_muted)
            return
            
        contagem = {"idoso": 0, "adulto saudável": 0, "pessoa com mobilidade reduzida": 0}
        for u in todos:
            p = u.get_perfil()
            if p in contagem: contagem[p] += 1
            else: contagem[p] = 1
            
        total = sum(contagem.values())
        if total == 0: return
        
        cores = {
            "idoso": "#ef4444",                     # Vermelho coral
            "adulto saudável": "#10b981",            # Verde esmeralda
            "pessoa com mobilidade reduzida": "#f59e0b" # Laranja vibrante
        }
        
        # 1. Título do gráfico
        canvas.create_text(310, 35, text="Distribuição dos Perfis Clínicos", font=("Segoe UI", 14, "bold"), fill=self.cor_text)
        
        # 2. Desenhar as fatias do donut
        start_angle = 0
        bbox = (80, 95, 340, 355)  
        
        for perfil, valor in contagem.items():
            if valor > 0:
                extent = (valor / total) * 360
                cor = cores.get(perfil, "#3b82f6")
                canvas.create_arc(bbox, start=start_angle, extent=extent, fill=cor, outline="white", width=2)
                start_angle += extent
                
        # 3. Desenhar o círculo central (Donut)
        centro_x, centro_y = 210, 225
        hollow_r = 75
        canvas.create_oval(centro_x - hollow_r, centro_y - hollow_r, centro_x + hollow_r, centro_y + hollow_r, fill="#ffffff", outline="#f1f5f9", width=2)
        
        # Texto central do Donut
        canvas.create_text(centro_x, centro_y - 12, text="TOTAL", font=("Segoe UI", 8, "bold"), fill=self.cor_muted)
        canvas.create_text(centro_x, centro_y + 12, text=str(total), font=("Segoe UI", 20, "bold"), fill=self.cor_text)
        
        # 4. Legenda lateral formatada
        y_legenda = 120
        for perfil, valor in contagem.items():
            cor = cores.get(perfil, "#3b82f6")
            perc = (valor / total) * 100
            
            canvas.create_rectangle(380, y_legenda, 395, y_legenda+15, fill=cor, outline="")
            canvas.create_text(405, y_legenda + 7, text=perfil.title(), font=("Segoe UI", 10, "bold"), fill=self.cor_text, anchor="w")
            canvas.create_text(405, y_legenda + 25, text=f"{valor} utilizadores ({perc:.1f}%)", font=("Segoe UI", 9), fill=self.cor_muted, anchor="w")
            y_legenda += 50

    # =========================================================================
    # AÇÕES: MAPA E REDE
    # =========================================================================
    def acao_listar_pontos(self):
        pontos = sorted(self.rede.listar_pontos())
        print(f"\n--- Pontos na Rede ({len(pontos)}) ---")
        for p in pontos: print(f" - {p}")
            
    def acao_listar_percursos(self):
        ruas_vistas = set()
        print("\n--- Todos os Percursos ---")
        for origem, conexoes in self.rede._grafo.items():
            for seg in conexoes:
                id_rua = tuple(sorted([origem, seg.get_destino()]))
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    print(f"{seg.get_origem()} <-> {seg.get_destino()} ({seg.get_distancia()}m)")

    def janela_adicionar_percurso(self):
        w = tk.Toplevel(self)
        w.title("Adicionar Novo Percurso")
        w.geometry("480x640")
        w.configure(bg=self.cor_bg)
        
        canvas = tk.Canvas(w, bg=self.cor_bg, highlightthickness=0)
        scroll = ttk.Scrollbar(w, orient="vertical", command=canvas.yview)
        
        frame = self.criar_card_frame(canvas, padding=20)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        frame.columnconfigure(1, weight=1)
        
        tk.Label(frame, text="Inserir Novo Percurso", font=self.fonte_titulo, bg=self.cor_card, fg=self.cor_primary).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        campos = ["Origem", "Destino", "Distância (m)", "Temp (ºC)", "Qualidade Ar (0-100)", 
                  "Ruído (dB) (0-100)", "Zonas Verdes (0-100)", "Inclinação (°)", 
                  "Pavimento (regular/irregular)", "Passadeiras (sim/não)", "Iluminação (boa/media/excelente)"]
        
        entradas = []
        for i, campo in enumerate(campos, 1):
            tk.Label(frame, text=f"{campo}:", font=self.fonte_bold, bg=self.cor_card).grid(row=i, column=0, sticky=tk.W, pady=6)
            e = ttk.Entry(frame, font=self.fonte_normal)
            e.grid(row=i, column=1, sticky="ew", pady=6, padx=(10, 0))
            entradas.append(e)
            
        def gravar_percurso():
            try:
                origem = entradas[0].get().strip()
                destino = entradas[1].get().strip()
                dist = float(entradas[2].get())
                temp = float(entradas[3].get())
                ar = float(entradas[4].get())
                ruido = float(entradas[5].get())
                zv = float(entradas[6].get())
                inc = float(entradas[7].get())
                pav = entradas[8].get().strip()
                passa = entradas[9].get().strip()
                ilum = entradas[10].get().strip()
                
                if not origem or not destino:
                    messagebox.showwarning("Aviso", "Preenche a origem e o destino.")
                    return
                
                seg = Segmento(origem, destino, dist, temp, ar, ruido, zv, inc, pav, passa, ilum)
                self.rede.adicionar_segmento(seg)
                print(f"✅ Percurso {origem} <-> {destino} inserido com sucesso!")
                
                pontos_novos = sorted(self.rede.listar_pontos())
                self.cb_origem['values'] = pontos_novos
                self.cb_destino['values'] = pontos_novos
                w.destroy()
            except ValueError as ex:
                messagebox.showerror("Erro de Formato", f"Verifica as caixas numéricas: {ex}")
                
        btn_gravar = self.criar_botao_moderno(frame, "Guardar Percurso", gravar_percurso, bg=self.cor_secondary, hover_bg=self.cor_secondary_hover)
        btn_gravar.grid(row=len(campos)+1, column=0, columnspan=2, pady=(20, 10))

    def janela_remover_percurso(self):
        origem = simpledialog.askstring("Remover", "Origem do Percurso:")
        if not origem: return
        destino = simpledialog.askstring("Remover", "Destino do Percurso:")
        if not destino: return
        if self.rede.remover_segmento(origem, destino):
            print(f"✅ Percurso {origem} <-> {destino} removido.")
        else:
            print(f"❌ Não foi possível encontrar/remover o percurso.")

    def acao_gerar_acidentes_aleatorios(self):
        # Limpar acidentes existentes
        for conexoes in self.rede._grafo.values():
            for seg in conexoes:
                seg.set_acidente(False)
                
        todas_ruas = []
        ruas_vistas = set()
        for origem, conexoes in self.rede._grafo.items():
            for seg in conexoes:
                destino = seg.get_destino()
                id_rua = tuple(sorted([origem, destino]))
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    todas_ruas.append((origem, destino))
                    
        if not todas_ruas: return
        
        # Embaralhar para obter aleatoriedade
        random.shuffle(todas_ruas)
        
        num_acidentes_desejados = random.randint(1, 3)
        acidentes_gerados = 0
        
        print("\n⚠️ GERAR ACIDENTES ALEATÓRIOS...")
        for origem, destino in todas_ruas:
            if acidentes_gerados >= num_acidentes_desejados:
                break
                
            # Tenta bloquear temporariamente
            self.rede.reportar_acidente(origem, destino, True)
            if self.rede.verificar_conectividade_sem_acidentes():
                # Válido! Mantém bloqueado
                print(f" ⛔ Acidente bloqueou a rua: {origem.replace('_', ' ')} <-> {destino.replace('_', ' ')}!")
                acidentes_gerados += 1
            else:
                # Reverter
                self.rede.reportar_acidente(origem, destino, False)
                
        if acidentes_gerados == 0:
            print("💡 Não foi possível gerar acidentes sem isolar partes da cidade.")
        else:
            print(f"✅ Simulação de trânsito atualizada com {acidentes_gerados} novos bloqueios.\n")
            
        # Redesenhar mapa se estiver aberto
        if hasattr(self, 'mapa_canvas') and self.mapa_canvas.winfo_exists():
            self._desenhar_mapa_no_canvas(self.mapa_canvas, self.ultima_rota_calculada)

    def _definir_periodo(self, periodo):
        self.periodo_sel = periodo
        self._sincronizar_clima_composto()
        
    def _definir_chuva(self, chuva):
        self.chuva_sel = chuva
        self._sincronizar_clima_composto()
        
    def _sincronizar_clima_composto(self):
        # Combinar período e chuva
        if self.periodo_sel == "Sol" and self.chuva_sel == "Seco":
            self.clima = "Sol"
        elif self.periodo_sel == "Noite" and self.chuva_sel == "Seco":
            self.clima = "Noite"
        elif self.periodo_sel == "Sol" and self.chuva_sel == "Chuva":
            self.clima = "Chuva"
        else: # Noite e Chuva
            self.clima = "Noite_Chuva"
            
        self._atualizar_botoes_periodo()
        self._atualizar_botoes_chuva()
        
        # Atualizar a sidebar
        if hasattr(self, 'lbl_clima_sidebar') and self.lbl_clima_sidebar.winfo_exists():
            sidebar_lbl = "🌤️ Sol"
            if self.periodo_sel == "Noite" and self.chuva_sel == "Chuva":
                sidebar_lbl = "🌙🌧️ Noite & Chuva"
            elif self.periodo_sel == "Sol" and self.chuva_sel == "Chuva":
                sidebar_lbl = "🌤️🌧️ Sol & Chuva"
            elif self.periodo_sel == "Noite":
                sidebar_lbl = "🌙 Noite"
            self.lbl_clima_sidebar.config(text=f"Clima: {sidebar_lbl}")
            
        # Atualizar o botão de gestão se existir
        if hasattr(self, 'btn_clima') and self.btn_clima.winfo_exists():
            btn_lbl = "🌤️ Sol"
            if self.periodo_sel == "Noite" and self.chuva_sel == "Chuva":
                btn_lbl = "🌙🌧️ Noite & Chuva"
            elif self.periodo_sel == "Sol" and self.chuva_sel == "Chuva":
                btn_lbl = "🌤️🌧️ Sol & Chuva"
            elif self.periodo_sel == "Noite":
                btn_lbl = "🌙 Noite"
            self.btn_clima.config(text=f"🌤️ Mudar Clima (Atual: {btn_lbl})")
            
        # Imprimir logs informativos
        if self.periodo_sel == "Noite" and self.chuva_sel == "Chuva":
            print("🌙🌧️ Está de Noite e a Chuver em Braga! Condições extremas: iluminação noturna precária e pavimento muito escorregadio.")
        elif self.periodo_sel == "Sol" and self.chuva_sel == "Chuva":
            print("🌤️🌧️ Está Sol e a Chuver em Braga! O piso irregular está escorregadio, mas a visibilidade diurna ajuda.")
        elif self.periodo_sel == "Noite":
            print("🌙 Está de Noite em Braga! A iluminação pública das ruas é agora crítica para a segurança das deslocações.")
        else:
            print("☀️ O tempo está limpo e ensolarado em Braga! Piso seguro e visibilidade perfeita.")
            
        # Redesenhar mapa se estiver aberto
        if hasattr(self, 'mapa_canvas') and self.mapa_canvas.winfo_exists():
            self._desenhar_mapa_no_canvas(self.mapa_canvas, self.ultima_rota_calculada)

    def _atualizar_botoes_periodo(self):
        for p, btn in self.botoes_periodo.items():
            if p == self.periodo_sel:
                bg_cor = "#f59e0b" if p == "Sol" else "#6366f1"
                fg_cor = "white"
                hover_cor = "#d97706" if p == "Sol" else "#4f46e5"
            else:
                bg_cor = "#e2e8f0"
                hover_cor = "#cbd5e1"
                fg_cor = "#0f172a"
                
            btn.config(
                bg=bg_cor, fg=fg_cor,
                activebackground=hover_cor, activeforeground=fg_cor
            )
            # Bind hover effect dynamically
            btn.bind("<Enter>", lambda e, b=btn, hc=hover_cor: b.config(bg=hc))
            btn.bind("<Leave>", lambda e, b=btn, bc=bg_cor: b.config(bg=bc))
            
    def _atualizar_botoes_chuva(self):
        for c, btn in self.botoes_chuva.items():
            if c == self.chuva_sel:
                bg_cor = "#475569" if c == "Seco" else "#0ea5e9"
                fg_cor = "white"
                hover_cor = "#334155" if c == "Seco" else "#0284c7"
            else:
                bg_cor = "#e2e8f0"
                hover_cor = "#cbd5e1"
                fg_cor = "#0f172a"
                
            btn.config(
                bg=bg_cor, fg=fg_cor,
                activebackground=hover_cor, activeforeground=fg_cor
            )
            # Bind hover effect dynamically
            btn.bind("<Enter>", lambda e, b=btn, hc=hover_cor: b.config(bg=hc))
            btn.bind("<Leave>", lambda e, b=btn, bc=bg_cor: b.config(bg=bc))

    def acao_mudar_clima(self):
        if self.periodo_sel == "Sol" and self.chuva_sel == "Seco":
            self.periodo_sel = "Noite"
            self.chuva_sel = "Seco"
        elif self.periodo_sel == "Noite" and self.chuva_sel == "Seco":
            self.periodo_sel = "Sol"
            self.chuva_sel = "Chuva"
        elif self.periodo_sel == "Sol" and self.chuva_sel == "Chuva":
            self.periodo_sel = "Noite"
            self.chuva_sel = "Chuva"
        else:
            self.periodo_sel = "Sol"
            self.chuva_sel = "Seco"
        self._sincronizar_clima_composto()

    def acao_mostrar_mapa_grafico(self):
        if hasattr(self, 'mapa_janela') and self.mapa_janela.winfo_exists():
            self.mapa_janela.lift()
            self.mapa_janela.title("Mapa Gráfico da Rede Urbana - Braga")
            self._desenhar_mapa_no_canvas(self.mapa_canvas)
            return
            
        self.mapa_janela = tk.Toplevel(self)
        self.mapa_janela.title("Mapa Gráfico da Rede Urbana - Braga")
        self.mapa_janela.geometry("950x720")
        self.mapa_janela.configure(bg=self.cor_bg)
        self.mapa_janela.columnconfigure(0, weight=1)
        self.mapa_janela.rowconfigure(0, weight=1)
        
        self.mapa_canvas = tk.Canvas(self.mapa_janela, bg=self.cor_bg, highlightthickness=0)
        self.mapa_canvas.grid(row=0, column=0, sticky="nsew")
        
        self._desenhar_mapa_no_canvas(self.mapa_canvas)

    # =========================================================================
    # AÇÕES: FICHEIROS E ESTATÍSTICAS
    # =========================================================================
    def acao_raio_x_cidade(self):
        print("\n--- RAIO-X DA CIDADE ---")
        VisualizacaoDados.raio_x_cidade(self.rede)
        print("--- FIM DO RAIO-X ---")

    def acao_estatisticas_percursos(self):
        print("\n--- ESTATÍSTICAS DE PERCURSOS ---")
        VisualizacaoDados.estatisticas_percursos(self.utilizadores, self.rede)

    def acao_gravar_json_silencioso(self, filename="dataset_utilizadores.json"):
        try:
            todos = self.utilizadores.listar_todos()
            dados = []
            for u in todos:
                dados.append({
                    "id": u.get_id(),
                    "nome": u.get_nome(),
                    "idade": u.get_idade(),
                    "sexo": u.get_sexo(),
                    "perfil": u.get_perfil(),
                    "historico": u.get_historico()
                })
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Erro ao auto-gravar: {e}")

    def acao_gravar_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Guardar Sistema")
        if not filename: return
        try:
            todos = self.utilizadores.listar_todos()
            dados = []
            for u in todos:
                dados.append({
                    "id": u.get_id(),
                    "nome": u.get_nome(),
                    "idade": u.get_idade(),
                    "sexo": u.get_sexo(),
                    "perfil": u.get_perfil(),
                    "historico": u.get_historico()
                })
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            print(f"✅ Sucesso: O sistema foi guardado em '{filename}' com histórico.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gravar: {e}")

    def acao_ler_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Ler Sistema")
        if not filename: return
        self.utilizadores = ArvoreUtilizadores() 
        self._carregar_utilizadores_com_historico(filename)
        print("✅ Sistema carregado do ficheiro JSON com sucesso.")
        try:
            self._carregar_historico_global()
        except Exception:
            pass

if __name__ == "__main__":
    app = AppGui()
    app.mainloop()
