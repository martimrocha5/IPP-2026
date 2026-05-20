"""
Módulo controlador: ponto de entrada da aplicação e interpretador de comandos.
Orquestra a interação entre os módulos de dados, modelo e vista.
"""

from dados import Utilizador, Segmento, RedeUrbana
import json
import random
import sys
from model import MotorAnalise, MotorRecomendacao
from arvores import ArvoreUtilizadores
from view import View
from graficos import VisualizacaoDados
from mapa_braga import carregar_mapa_expandido

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# Perfis aceites pelo sistema
PERFIS_VALIDOS = ["idoso", "adulto saudável", "pessoa com mobilidade reduzida"]
MODOS_VALIDOS  = ["padrao", "relaxar", "exercicio", "ar_puro", "trabalho"]


def inicializar_rede(rede):
    """
    Define a malha urbana de Braga com os segmentos pré-configurados.

    Args:
        rede: Objeto RedeUrbana a popular.
    """
    segmentos = [
        Segmento("UMinho_Gualtar",  "Braga_Parque",       1200, 19, 85, 45, 60,  1, "regular",   "sim", "boa"),
        Segmento("UMinho_Gualtar",  "Bom_Jesus",          3500, 17, 95, 20, 90, 18, "regular",   "sim", "media"),
        Segmento("Braga_Parque",    "Praca_Republica",    1500, 22, 50, 75, 20,  2, "irregular", "sim", "excelente"),
        Segmento("Praca_Republica", "Estacao_Comboios",    800, 21, 40, 85, 10,  1, "regular",   "sim", "excelente"),
        Segmento("Braga_Parque",    "Estacao_Comboios",   2500, 20, 45, 70, 15,  2, "regular",   "sim", "boa"),
        Segmento("Praca_Republica", "Bom_Jesus",          4000, 18, 80, 30, 70, 15, "irregular", "sim", "media"),
    ]
    for s in segmentos:
        rede.adicionar_segmento(s)
    print(f"✅ Malha urbana de 'Braga Saudável' inicializada com {len(segmentos)} segmentos.")


def carregar_utilizadores(utilizadores, ficheiro):
    """
    Carrega utilizadores de um ficheiro JSON para a árvore BSP.

    Args:
        utilizadores: Objeto ArvoreUtilizadores onde inserir os dados.
        ficheiro: Caminho para o ficheiro JSON.
    """
    try:
        with open(ficheiro, 'r', encoding='utf-8') as f:
            dados_users = json.load(f)

        count_antes = len(utilizadores)
        ignorados = 0

        for user in dados_users:
            try:
                novo_user = Utilizador(
                    id_utilizador=user["id"],
                    nome=user["nome"],
                    idade=user["idade"],
                    sexo=user["sexo"],
                    perfil=user["perfil"]
                )
                utilizadores.inserir(novo_user)
            except (KeyError, ValueError):
                ignorados += 1

        count_novos = len(utilizadores) - count_antes
        print(f"✅ {count_novos} utilizadores carregados de '{ficheiro}'.", end="")
        if ignorados:
            print(f" ({ignorados} ignorados por dados inválidos)")
        else:
            print()

    except FileNotFoundError:
        print(f" Ficheiro '{ficheiro}' não encontrado.")
    except json.JSONDecodeError:
        print(f" O ficheiro '{ficheiro}' não é um JSON válido.")
    except Exception as e:
        print(f" Erro inesperado ao ler ficheiro: {e}")


def gravar_utilizadores(utilizadores, ficheiro):
    """
    Grava todos os utilizadores da árvore num ficheiro JSON.

    Args:
        utilizadores: Objeto ArvoreUtilizadores com os dados.
        ficheiro: Caminho para o ficheiro JSON de destino.
    """
    todos = utilizadores.listar_todos()
    dados = [
        {
            "id":     u.get_id(),
            "nome":   u.get_nome(),
            "idade":  u.get_idade(),
            "sexo":   u.get_sexo(),
            "perfil": u.get_perfil()
        }
        for u in todos
    ]
    try:
        with open(ficheiro, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f" {len(dados)} utilizadores gravados em '{ficheiro}'.")
    except Exception as e:
        print(f" Erro ao gravar ficheiro: {e}")


def gerar_id_unico(utilizadores):
    """
    Gera um ID único para um novo utilizador, garantindo que não existe duplicado.

    Args:
        utilizadores: Objeto ArvoreUtilizadores para verificar duplicados.

    Returns:
        String com ID único no formato 'UXXXXX'.
    """
    novo_id = f"U{random.randint(10000, 99999)}"
    while utilizadores.procurar(novo_id) is not None:
        novo_id = f"U{random.randint(10000, 99999)}"
    return novo_id


# ──────────────────────────────────────────────────────────────────────────────
# AUDITORIA DO SISTEMA
# ──────────────────────────────────────────────────────────────────────────────

class Auditoria:
    """Sistema simples de auditoria para registar ações no sistema."""
    
    def __init__(self):
        self._registos = []
    
    def registar(self, acao, detalhes="", sucesso=True):
        """Registar uma ação no sistema.
        
        Args:
            acao: Tipo de ação (ex: 'ins_utilizador', 'remover_utilizador')
            detalhes: Informações adicionais
            sucesso: Se a ação foi bem-sucedida
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅" if sucesso else "❌"
        self._registos.append(f"[{timestamp}] {status} {acao}: {detalhes}")
    
    def exportar_registos(self, ficheiro="auditoria.log"):
        """Exporta os registos para um ficheiro."""
        try:
            with open(ficheiro, 'w', encoding='utf-8') as f:
                for registo in self._registos:
                    f.write(registo + "\n")
            print(f" Auditoria exportada para '{ficheiro}' ({len(self._registos)} registos).")
        except Exception as e:
            print(f" Erro ao exportar auditoria: {e}")
    
    def listar_ultimos(self, n=10):
        """Lista os últimos N registos de auditoria."""
        print(f"\n{'─'*70}")
        print(f"ÚLTIMOS {n} REGISTOS DE AUDITORIA")
        print(f"{'─'*70}")
        for registo in self._registos[-n:]:
            print(registo)
        print(f"{'─'*70}\n")


# ──────────────────────────────────────────────────────────────────────────────
# PROCESSADORES DE COMANDOS ADICIONAIS
# ──────────────────────────────────────────────────────────────────────────────

def processar_remover_utilizador(partes, utilizadores, auditoria):
    """Remove um utilizador do sistema."""
    if len(partes) != 2:
        print(" Formato inválido. Utiliza: remover_utilizador <id>")
        return
    
    id_utilizador = partes[1]
    user = utilizadores.procurar(id_utilizador)
    
    if user is None:
        print(f" Utilizador '{id_utilizador}' não encontrado.")
        auditoria.registar("remover_utilizador", f"ID '{id_utilizador}'", sucesso=False)
        return
    
    if utilizadores.remover(id_utilizador):
        print(f" Utilizador '{user.get_nome()}' ({id_utilizador}) removido com sucesso.")
        auditoria.registar("remover_utilizador", f"{id_utilizador} - {user.get_nome()}", sucesso=True)
    else:
        print(f" Não foi possível remover o utilizador '{id_utilizador}'.")
        auditoria.registar("remover_utilizador", f"ID '{id_utilizador}'", sucesso=False)


def processar_remover_percurso(partes, rede, auditoria):
    """Remove um percurso da rede."""
    if len(partes) != 3:
        print(" Formato inválido. Utiliza: remover_percurso <origem> <destino>")
        return
    
    origem, destino = partes[1], partes[2]
    
    if not rede.contem_ponto(origem):
        print(f" Ponto '{origem}' não existe na rede.")
        auditoria.registar("remover_percurso", f"{origem} → {destino}", sucesso=False)
        return
    
    if not rede.contem_ponto(destino):
        print(f" Ponto '{destino}' não existe na rede.")
        auditoria.registar("remover_percurso", f"{origem} → {destino}", sucesso=False)
        return
    
    if rede.remover_segmento(origem, destino):
        print(f" Percurso '{origem}' → '{destino}' removido com sucesso (ambas as direções).")
        auditoria.registar("remover_percurso", f"{origem} ↔ {destino}", sucesso=True)
    else:
        print(f" Percurso '{origem}' → '{destino}' não encontrado.")
        auditoria.registar("remover_percurso", f"{origem} → {destino}", sucesso=False)


def processar_editar_utilizador(partes, utilizadores, auditoria):
    """Edita dados de um utilizador."""
    if len(partes) < 4:
        print("  Formato inválido.")
        print("   Utiliza: editar_utilizador <id> <campo> <novo_valor>")
        print("   Campos: nome | idade | sexo | perfil")
        return
    
    id_utilizador = partes[1]
    campo = partes[2].lower()
    novo_valor = " ".join(partes[3:])
    
    user = utilizadores.procurar(id_utilizador)
    if user is None:
        print(f" Utilizador '{id_utilizador}' não encontrado.")
        auditoria.registar("editar_utilizador", f"ID '{id_utilizador}' - não encontrado", sucesso=False)
        return
    
    try:
        if campo == "nome":
            user._nome = novo_valor
        elif campo == "idade":
            idade = int(novo_valor)
            if not (0 <= idade <= 120):
                raise ValueError("Idade deve estar entre 0 e 120.")
            user._idade = idade
        elif campo == "sexo":
            if novo_valor.upper() not in ["M", "F", "OUTRO"]:
                raise ValueError("Sexo deve ser M, F ou OUTRO.")
            user._sexo = novo_valor.upper()
        elif campo == "perfil":
            if novo_valor.lower() not in PERFIS_VALIDOS:
                raise ValueError(f"Perfil deve ser um de: {', '.join(PERFIS_VALIDOS)}")
            user._perfil = novo_valor.lower()
        else:
            print(f" Campo '{campo}' desconhecido.")
            return
        
        print(f" Utilizador '{id_utilizador}' atualizado: {campo} = '{novo_valor}'")
        auditoria.registar("editar_utilizador", f"{id_utilizador} - {campo}='{novo_valor}'", sucesso=True)
    except Exception as e:
        print(f" Erro ao editar: {e}")
        auditoria.registar("editar_utilizador", f"{id_utilizador} - erro: {e}", sucesso=False)


def main():
    """Função principal que inicializa o sistema e arranca o interpretador de comandos."""
    rede = RedeUrbana()
    utilizadores = ArvoreUtilizadores()
    motor_analise = MotorAnalise()
    motor_recomendacao = MotorRecomendacao(motor_analise)
    clima_atual = "Sol"

    inicializar_rede(rede)
    carregar_mapa_expandido(rede)
    carregar_utilizadores(utilizadores, "dataset_utilizadores.json")
    View.mostrar_boas_vindas(len(utilizadores))

    while True:
        try:
            entrada = input("> ").strip()
            if not entrada:
                continue

            partes = entrada.split()
            comando = partes[0].lower()

            # ── RECOMENDAR ───────────────────────────────────────────────────
            if comando == "recomendar":
                if len(partes) >= 4:
                    origem          = partes[1]
                    destino         = partes[2]
                    id_utilizador   = partes[3]
                    modo_escolhido  = partes[4] if len(partes) > 4 else "padrao"
                    acompanhante    = " ".join(partes[5:]) if len(partes) > 5 else "Nenhum"

                    if modo_escolhido not in MODOS_VALIDOS:
                        print(f"❌ Modo '{modo_escolhido}' inválido. Modos disponíveis: {' | '.join(MODOS_VALIDOS)}")
                        continue

                    if origem == destino:
                        print("⚠️  A origem e o destino são o mesmo ponto. Já estás no destino!")
                        continue

                    if not rede.obter_conexoes(origem):
                        print(f"❌ O ponto '{origem}' não existe na rede. Usa 'mapa' para ver os pontos disponíveis.")
                        continue

                    if not rede.obter_conexoes(destino):
                        print(f"❌ O ponto '{destino}' não existe na rede. Usa 'mapa' para ver os pontos disponíveis.")
                        continue

                    user_atual = utilizadores.procurar(id_utilizador)
                    
                    # Se não encontrado por ID, verificar se foi passado um perfil ou palavra-chave de perfil
                    if user_atual is None:
                        perfil_normalizado = id_utilizador.lower().strip()
                        perfil_detectado = None
                        
                        if perfil_normalizado in ["idoso", "idosa"]:
                            perfil_detectado = "idoso"
                        elif perfil_normalizado in ["adulto", "saudável", "saudavel", "adulto saudável", "adulto saudavel"]:
                            perfil_detectado = "adulto saudável"
                        elif perfil_normalizado in ["mobilidade", "reduzida", "pessoa com mobilidade reduzida", "pcd"]:
                            perfil_detectado = "pessoa com mobilidade reduzida"
                            
                        if perfil_detectado:
                            # Tentar encontrar qualquer utilizador real na árvore com esse perfil
                            todos_users = utilizadores.listar_todos()
                            for u in todos_users:
                                if u.get_perfil() == perfil_detectado:
                                    user_atual = u
                                    print(f"ℹ️ A usar o perfil '{perfil_detectado}' (associado ao utilizador '{u.get_nome()}' - {u.get_id()})")
                                    break
                            # Se não houver nenhum, criar um utilizador temporário genérico
                            if user_atual is None:
                                idade_default = 75 if perfil_detectado == "idoso" else (35 if perfil_detectado == "adulto saudável" else 50)
                                user_atual = Utilizador("UTEMP", f"Utilizador Genérico ({perfil_detectado})", idade_default, "OUTRO", perfil_detectado)
                                print(f"ℹ️ Criado utilizador temporário para o perfil '{perfil_detectado}'.")
                                
                    if user_atual is not None:
                        caminho, custo = motor_recomendacao.encontrar_melhor_caminho(
                            rede, origem, destino, user_atual, modo_escolhido, acompanhante, clima_atual
                        )
                        if caminho:
                            distancia_total = sum(seg.get_distancia() for seg in caminho)
                            inclinacao_abs = sum(abs(seg.get_inclinacao()) for seg in caminho)
                            velocidade_kmh = 4.0
                            if "trabalho" in modo_escolhido:
                                velocidade_kmh = 5.5  # Passo apressado para ir para o trabalho
                            if user_atual.get_perfil() in ["idoso", "pessoa com mobilidade reduzida"]:
                                if "trabalho" in modo_escolhido:
                                    velocidade_kmh = 3.5  # Mesmo idosos apressam o passo para o trabalho
                                else:
                                    velocidade_kmh -= 1.5
                            if acompanhante in ["Cadeira de Rodas", "Andarilho"]:
                                if "trabalho" in modo_escolhido:
                                    velocidade_kmh = max(1.5, velocidade_kmh - 0.5)
                                else:
                                    velocidade_kmh -= 1.0
                            velocidade_kmh = max(1.0, velocidade_kmh)
                            tempo_minutos = int(((distancia_total / 1000.0) / velocidade_kmh) * 60)
                            calorias_base = (distancia_total / 1000.0) * 50
                            if modo_escolhido == "exercicio": calorias_base *= 1.5
                            calorias = int(calorias_base + inclinacao_abs * 2)

                            print(f"\n[CLIMA: {clima_atual}] ⏱️ Tempo: ~{tempo_minutos} min | 🔥 Calorias: ~{calorias} kcal")
                            
                        View.mostrar_resultado_rota(
                            origem, destino, user_atual, modo_escolhido, caminho, custo, motor_analise, acompanhante, clima_atual
                        )
                        if caminho:
                            user_atual.adicionar_historico(origem, destino, modo_escolhido, custo)
                            gravar_utilizadores(utilizadores, "dataset_utilizadores.json") # Auto-save
                            todas_rotas = motor_recomendacao.encontrar_todos_caminhos(
                                rede, origem, destino, user_atual, modo_escolhido, 10, acompanhante, clima_atual
                            )
                            if len(todas_rotas) > 1:
                                VisualizacaoDados.comparar_rotas(todas_rotas, origem, destino)
                    else:
                        print(f"❌ Utilizador com ID '{id_utilizador}' não encontrado.")
                else:
                    print("❌ Formato inválido.")
                    print("   Utiliza: recomendar <origem> <destino> <id_utilizador> [modo] [acompanhante]")
                    print(f"   Modos: {' | '.join(MODOS_VALIDOS)}")

            # ── LIST ─────────────────────────────────────────────────────────
            elif comando == "list":
                if len(partes) >= 2:
                    sub    = partes[1].lower()
                    pagina = 1
                    if len(partes) >= 3:
                        try:
                            pagina = int(partes[2])
                        except ValueError:
                            print("❌ O número de página deve ser um inteiro positivo.")
                            continue

                    if sub == "percursos":
                        View.listar_percursos_paginado(rede, pagina)
                    elif sub == "utilizadores":
                        View.listar_utilizadores_paginado(utilizadores, pagina)
                    else:
                        print("❌ Opção inválida. Utiliza: list percursos | list utilizadores")
                else:
                    print("❌ Formato inválido. Utiliza: list percursos [pagina] | list utilizadores [pagina]")

            # ── HISTORICO ────────────────────────────────────────────────────
            elif comando == "historico":
                if len(partes) == 2:
                    user_atual = utilizadores.procurar(partes[1])
                    if user_atual:
                        View.mostrar_historico(user_atual)
                    else:
                        print(f"❌ Utilizador '{partes[1]}' não encontrado.")
                else:
                    print("❌ Formato inválido. Utiliza: historico <id_utilizador>")

            # ── PROCURAR ─────────────────────────────────────────────────────
            elif comando == "procurar":
                if len(partes) == 2:
                    user_atual = utilizadores.procurar(partes[1])
                    if user_atual:
                        View.mostrar_perfil(user_atual)
                    else:
                        print(f"❌ Utilizador '{partes[1]}' não encontrado na base de dados.")
                else:
                    print("❌ Formato inválido. Utiliza: procurar <id_utilizador>")

            # ── INS_UTILIZADOR ───────────────────────────────────────────────
            elif comando == "ins_utilizador":
                # Aceita nome com espaços e distingue assinaturas:
                # 1. Simplificada: ins_utilizador <nome_com_espacos> <perfil>
                # 2. Completa:     ins_utilizador <nome_com_espacos> <idade> <sexo> <perfil>
                
                args_str = " ".join(partes[1:])
                perfil_encontrado = None
                
                # Procurar qual o perfil no final dos argumentos
                for perf in PERFIS_VALIDOS:
                    if args_str.lower().endswith(perf):
                        perfil_encontrado = perf
                        break
                        
                # Também suportar "adulto saudavel" sem acento
                if not perfil_encontrado and args_str.lower().endswith("adulto saudavel"):
                    perfil_encontrado = "adulto saudável"
                    
                if perfil_encontrado and len(args_str) > len(perfil_encontrado):
                    tamanho_a_remover = len(perfil_encontrado)
                    if not args_str.lower().endswith(perfil_encontrado) and args_str.lower().endswith("adulto saudavel"):
                        tamanho_a_remover = len("adulto saudavel")
                    
                    remaining = args_str[:-tamanho_a_remover].strip()
                    rem_partes = remaining.split()
                    
                    # Verificar se é o formato completo (termina com idade e sexo)
                    is_completo = False
                    if len(rem_partes) >= 2:
                        idade_cand = rem_partes[-2]
                        sexo_cand = rem_partes[-1].upper()
                        if idade_cand.isdigit() and sexo_cand in ["M", "F", "OUTRO"]:
                            is_completo = True
                            
                    if is_completo:
                        idade = int(rem_partes[-2])
                        sexo = rem_partes[-1].upper()
                        nome = " ".join(rem_partes[:-2]).strip()
                    else:
                        if perfil_encontrado == "idoso":
                            idade = 70
                        elif perfil_encontrado == "adulto saudável":
                            idade = 30
                        else: # pessoa com mobilidade reduzida
                            idade = 50
                        sexo = "OUTRO"
                        nome = remaining
                        
                    try:
                        novo_id = gerar_id_unico(utilizadores)
                        novo_user = Utilizador(novo_id, nome, idade, sexo, perfil_encontrado)
                        utilizadores.inserir(novo_user)
                        if is_completo:
                            print(f"✅ Utilizador '{nome}' inserido com ID: {novo_id} (Formato Completo)")
                        else:
                            print(f"✅ Utilizador '{nome}' inserido com ID: {novo_id} (Perfil: {perfil_encontrado}, Idade default: {idade})")
                        gravar_utilizadores(utilizadores, "dataset_utilizadores.json") # Auto-save
                    except ValueError as e:
                        print(f"❌ Erro de validação: {e}")
                else:
                    print("❌ Formato inválido.")
                    print("   Utiliza (simplificado): ins_utilizador <nome> <perfil>")
                    print("   Utiliza (completo):     ins_utilizador <nome> <idade> <sexo> <perfil>")
                    print(f"   Perfis válidos: {' | '.join(PERFIS_VALIDOS)}")

            # ── INS_PERCURSO ─────────────────────────────────────────────────
            elif comando == "ins_percurso":
                # Aceita o formato simplificado: ins_percurso <origem>-<destino> ou ins_percurso <origem> <destino>
                # E também o formato completo: ins_percurso <origem> <destino> <dist> <temp> <ar> <ruido> <verdes> <inclinacao> <pav> <passadeiras> <ilum>
                
                origem, destino = None, None
                usou_simplificado = False
                
                if len(partes) == 2:
                    # Formato ins_percurso <origem>-<destino>
                    percurso = partes[1]
                    for delim in ["->", "-", "↔", "to"]:
                        if delim in percurso:
                            sub_p = percurso.split(delim)
                            if len(sub_p) == 2:
                                origem = sub_p[0].strip()
                                destino = sub_p[1].strip()
                                usou_simplificado = True
                                break
                elif len(partes) == 3:
                    # Formato ins_percurso <origem> <destino>
                    origem = partes[1]
                    destino = partes[2]
                    usou_simplificado = True
                    
                if usou_simplificado and origem and destino:
                    distancia   = 1000.0
                    temp        = 20.0
                    ar          = 80.0
                    ruido       = 30.0
                    verdes      = 50.0
                    inclinacao  = 0.0
                    pavimento   = "regular"
                    passadeiras = "sim"
                    iluminacao  = "boa"
                    
                    try:
                        novo_seg = Segmento(
                            origem, destino, distancia, temp, ar,
                            ruido, verdes, inclinacao, pavimento, passadeiras, iluminacao
                        )
                        rede.adicionar_segmento(novo_seg)
                        print(f"✅ Percurso '{origem} -> {destino}' ({distancia}m) inserido com sucesso (Valores por omissão).")
                    except ValueError as e:
                        print(f"❌ Erro de validação: {e}")
                        
                elif len(partes) == 12:
                    origem    = partes[1]
                    destino   = partes[2]
                    pavimento = partes[9].lower()

                    if pavimento not in ["regular", "irregular"]:
                        print("❌ Pavimento deve ser 'regular' ou 'irregular'.")
                        continue

                    try:
                        distancia   = float(partes[3])
                        temp        = float(partes[4])
                        ar          = float(partes[5])
                        ruido       = float(partes[6])
                        verdes      = float(partes[7])
                        inclinacao  = float(partes[8])
                        passadeiras = partes[10]
                        iluminacao  = partes[11]

                        # Validações de negócio antes de criar o objeto
                        if inclinacao < 0:
                            print("❌ Inclinação deve ser um valor positivo ou zero.")
                            continue

                        novo_seg = Segmento(
                            origem, destino, distancia, temp, ar,
                            ruido, verdes, inclinacao, pavimento, passadeiras, iluminacao
                        )
                        rede.adicionar_segmento(novo_seg)
                        print(f"✅ Percurso '{origem} -> {destino}' ({distancia}m) inserido com sucesso.")

                    except ValueError as e:
                        print(f"❌ Erro de validação: {e}")
                else:
                    print("❌ Formato inválido.")
                    print("   Utiliza (simplificado): ins_percurso <origem>-<destino> ou <origem> <destino>")
                    print("   Utiliza (completo):     ins_percurso <origem> <destino> <dist> <temp> <ar> <ruido>")
                    print("                                <verdes> <inclinacao> <pav> <passadeiras> <ilum>")

            # ── VER ──────────────────────────────────────────────────────────
            elif comando == "ver":
                if len(partes) == 1:
                    # Sem argumentos: mostra mapa na consola e abre a janela gráfica (GUI)
                    print("\n🌐 A desenhar mapa na consola...")
                    View.mostrar_mapa()
                    print("🌐 A iniciar a interface gráfica 'Braga Saudável'...")
                    try:
                        from gui import AppGui
                        app = AppGui()
                        app.mainloop()
                        print("✅ Interface gráfica fechada.")
                    except Exception as ex:
                        print(f"❌ Erro ao iniciar a interface gráfica: {ex}")
                elif len(partes) == 2:
                    # 1 argumento: ver <percurso> (ex: ver Hospital_Braga-Bom_Jesus)
                    percurso = partes[1]
                    origem, destino = None, None
                    for delim in ["->", "-", "↔", "to"]:
                        if delim in percurso:
                            sub_partes = percurso.split(delim)
                            if len(sub_partes) == 2:
                                origem = sub_partes[0].strip()
                                destino = sub_partes[1].strip()
                                break
                    if origem and destino:
                        segmento_encontrado = None
                        for seg in rede.obter_conexoes(origem):
                            if seg.get_destino() == destino:
                                segmento_encontrado = seg
                                break
                        View.mostrar_detalhes_segmento(origem, destino, segmento_encontrado)
                    else:
                        print(f"❌ Formato inválido. Não foi possível identificar a origem e destino em '{percurso}'.")
                        print("   Use um delimitador como '-' ou '->' (ex: ver Hospital_Braga-Bom_Jesus)")
                elif len(partes) == 3:
                    # 2 argumentos: ver <origem> <destino> (ex: ver Hospital_Braga Bom_Jesus)
                    origem, destino = partes[1], partes[2]
                    segmento_encontrado = None
                    for seg in rede.obter_conexoes(origem):
                        if seg.get_destino() == destino:
                            segmento_encontrado = seg
                            break
                    View.mostrar_detalhes_segmento(origem, destino, segmento_encontrado)
                else:
                    print("❌ Formato inválido. Utiliza:")
                    print("   - ver (sem argumentos para abrir janela gráfica)")
                    print("   - ver <origem>-<destino> (formato percurso)")
                    print("   - ver <origem> <destino> (dois argumentos separados por espaço)")

            # ── MAPA ─────────────────────────────────────────────────────────
            elif comando == "mapa":
                View.mostrar_mapa()

            # ── ESTATISTICAS ─────────────────────────────────────────────────
            elif comando == "estatisticas":
                sub = partes[1].lower() if len(partes) > 1 else "cidade"
                if sub == "cidade":
                    VisualizacaoDados.raio_x_cidade(rede)
                elif sub == "utilizadores":
                    VisualizacaoDados.analise_utilizadores(utilizadores)
                elif sub == "percursos":
                    VisualizacaoDados.estatisticas_percursos(utilizadores, rede)
                else:
                    print("❌ Opção inválida. Utiliza: estatisticas [cidade | utilizadores | percursos]")

            # ── ANALISE_UTILIZADORES (atalho) ─────────────────────────────────
            elif comando == "analise_utilizadores":
                VisualizacaoDados.analise_utilizadores(utilizadores)

            # ── GRAVAR ───────────────────────────────────────────────────────
            elif comando == "gravar":
                if len(partes) == 2:
                    gravar_utilizadores(utilizadores, partes[1])
                else:
                    print("❌ Formato inválido. Utiliza: gravar <ficheiro>")

            # ── LER ──────────────────────────────────────────────────────────
            elif comando == "ler":
                if len(partes) == 2:
                    carregar_utilizadores(utilizadores, partes[1])
                else:
                    print("❌ Formato inválido. Utiliza: ler <ficheiro>")

            # ── CLIMA ────────────────────────────────────────────────────────
            elif comando == "clima":
                if clima_atual == "Sol":
                    clima_atual = "Noite"
                    print("🌙 Período alterado para: Noite. A iluminação pública das ruas é agora crítica!")
                elif clima_atual == "Noite":
                    clima_atual = "Chuva"
                    print("🌧️ O tempo mudou! Está a chover em Braga. Ruas com piso irregular estão perigosas.")
                elif clima_atual == "Chuva":
                    clima_atual = "Noite_Chuva"
                    print("🌧️🌙 O tempo mudou! Está a chover E é de noite em Braga. Visibilidade reduzida e pisos muito escorregadios!")
                else:
                    clima_atual = "Sol"
                    print("☀️ O tempo mudou! O sol brilha em Braga. Piso irregular mais seguro.")

            # ── ACIDENTES ────────────────────────────────────────────────────
            elif comando == "acidentes":
                # Limpar antigos
                for conexoes in rede._grafo.values():
                    for seg in conexoes:
                        seg.set_acidente(False)
                todas_ruas = []
                ruas_vistas = set()
                for o, conexoes in rede._grafo.items():
                    for seg in conexoes:
                        d = seg.get_destino()
                        id_rua = tuple(sorted([o, d]))
                        if id_rua not in ruas_vistas:
                            ruas_vistas.add(id_rua)
                            todas_ruas.append((o, d))
                if todas_ruas:
                    # Embaralhar para obter aleatoriedade
                    random.shuffle(todas_ruas)
                    num_acidentes_desejados = random.randint(1, 3)
                    acidentes_gerados = 0
                    
                    print("\n⚠️ GERAR ACIDENTES ALEATÓRIOS...")
                    for o, d in todas_ruas:
                        if acidentes_gerados >= num_acidentes_desejados:
                            break
                        
                        # Tentar bloquear temporariamente
                        rede.reportar_acidente(o, d, True)
                        if rede.verificar_conectividade_sem_acidentes():
                            # Mantém bloqueado
                            print(f" ⛔ Acidente bloqueou: {o} <-> {d}!")
                            acidentes_gerados += 1
                        else:
                            # Reverter
                            rede.reportar_acidente(o, d, False)
                            
                    if acidentes_gerados == 0:
                        print("💡 Não foi possível gerar acidentes sem isolar partes da cidade.")
                    else:
                        print(f"✅ Simulação atualizada com {acidentes_gerados} acidentes.\n")

            # ── EXPORTAR ─────────────────────────────────────────────────────
            elif comando == "exportar":
                if len(partes) == 2:
                    id_user = partes[1]
                    u = utilizadores.procurar(id_user)
                    if u:
                        import csv
                        filename = f"relatorio_{u.get_nome().replace(' ', '_')}.csv"
                        try:
                            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                                writer = csv.writer(f, delimiter=';')
                                writer.writerow(["ID", u.get_id()])
                                writer.writerow(["Nome", u.get_nome()])
                                writer.writerow(["Histórico de Viagens"])
                                for h in u.get_historico():
                                    if len(h) == 4: writer.writerow([h[0], h[1], h[2], h[3]])
                            print(f"✅ CSV exportado para '{filename}'")
                        except Exception as e:
                            print(f"❌ Erro ao exportar CSV: {e}")
                    else:
                        print(f"❌ Utilizador '{id_user}' não encontrado.")
                else:
                    print("❌ Utiliza: exportar <id_utilizador>")

            # ── AJUDA ────────────────────────────────────────────────────────
            elif comando == "ajuda":
                View.mostrar_ajuda()

            # ── SAIR ─────────────────────────────────────────────────────────
            elif comando == "sair":
                print("✅ A encerrar o sistema 'Braga Saudável'. Boas viagens!")
                break

            else:
                print(f"❌ Comando '{comando}' não reconhecido.")
                print("   Escreve 'ajuda' para ver a lista de comandos disponíveis.")

        except KeyboardInterrupt:
            print("\n\n✅ Interrompido. A encerrar o sistema.")
            break
        except Exception as e:
            print(f"❌ Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
