from dados import Utilizador, Segmento, RedeUrbana
import json
import numpy as np
import sys
sys.setrecursionlimit(5000)  # Aumentar limite de recursão
from model import MotorAnalise, MotorRecomendacao
from arvores import ArvoreUtilizadores
from view import View
from graficos import VisualizacaoDados
import random

def gravar_dados(rede, utilizadores, ficheiro):
    """Gravar utilizadores e segmentos em ficheiro JSON"""
    try:
        dados = {
            "utilizadores": [],
            "segmentos": []
        }
        
        # Gravar utilizadores
        for user in utilizadores.listar_todos():
            dados["utilizadores"].append({
                "id": user.get_id(),
                "nome": user.get_nome(),
                "idade": user.get_idade(),
                "sexo": user.get_sexo(),
                "perfil": user.get_perfil(),
                "historico": user.get_historico()
            })
        
        # Gravar segmentos (evitar duplicatas bidireccionais)
        ruas_vistas = set()
        for origem, conexoes in rede._grafo.items():
            for seg in conexoes:
                destino = seg.get_destino()
                id_rua = tuple(sorted([origem, destino]))
                
                if id_rua not in ruas_vistas:
                    ruas_vistas.add(id_rua)
                    dados["segmentos"].append({
                        "origem": seg.get_origem(),
                        "destino": seg.get_destino(),
                        "distancia": seg.get_distancia(),
                        "temperatura": seg.get_temperatura(),
                        "qualidade_ar": seg.get_qualidade_ar(),
                        "ruido": seg.get_ruido(),
                        "zonas_verdes": seg.get_zonas_verdes(),
                        "inclinacao": seg.get_inclinacao(),
                        "pavimento": seg.get_pavimento(),
                        "passadeiras": seg.get_passadeiras(),
                        "iluminacao": seg.get_iluminacao()
                    })
        
        with open(ficheiro, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        
        print(f" Sucesso: Sistema gravado em '{ficheiro}'")
        print(f"   - {len(dados['utilizadores'])} utilizadores")
        print(f"   - {len(dados['segmentos'])} segmentos")
    except Exception as e:
        print(f" Erro ao gravar dados: {e}")

def carregar_dados(rede, utilizadores, ficheiro):
    """Carregar utilizadores e segmentos de um ficheiro JSON"""
    try:
        with open(ficheiro, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Carregar utilizadores
        for user_data in dados.get("utilizadores", []):
            novo_user = Utilizador(
                id_utilizador=user_data["id"],
                nome=user_data["nome"],
                idade=user_data["idade"],
                sexo=user_data["sexo"],
                perfil=user_data["perfil"]
            )
            # Restaurar histórico
            for hist in user_data.get("historico", []):
                novo_user.adicionar_historico(hist[0], hist[1], hist[2], hist[3])
            utilizadores.inserir(novo_user)
        
        # Carregar segmentos
        for seg_data in dados.get("segmentos", []):
            novo_seg = Segmento(
                origem=seg_data["origem"],
                destino=seg_data["destino"],
                distancia=seg_data["distancia"],
                temp=seg_data["temperatura"],
                ar=seg_data["qualidade_ar"],
                ruido=seg_data["ruido"],
                zonas_verdes=seg_data["zonas_verdes"],
                inclinacao=seg_data["inclinacao"],
                pavimento=seg_data["pavimento"],
                passadeiras=seg_data["passadeiras"],
                iluminacao=seg_data["iluminacao"]
            )
            rede.adicionar_segmento(novo_seg)
        
        print(f" Sucesso: Sistema carregado de '{ficheiro}'")
        print(f"   - {len(dados['utilizadores'])} utilizadores")
        print(f"   - {len(dados['segmentos'])} segmentos")
    except FileNotFoundError:
        print(f" Erro: Ficheiro '{ficheiro}' não encontrado.")
    except Exception as e:
        print(f" Erro ao carregar dados: {e}")

def inicializar_braga(rede, utilizadores, ficheiro_dataset="dataset_utilizadores.json"):
    try:
        with open(ficheiro_dataset, 'r', encoding='utf-8') as f:
            dados_users = json.load(f)

            for user in dados_users:
                novo_user = Utilizador(
                    id_utilizador=user["id"],
                    nome=user["nome"],
                    idade=user["idade"],
                    sexo=user["sexo"],
                    perfil=user["perfil"]
                )
                utilizadores.inserir(novo_user)

        print(f" Sucesso: {len(utilizadores)} utilizadores carregados para a Árvore Binária de Procura!")

    except FileNotFoundError:
        print(f" Aviso: O ficheiro '{ficheiro_dataset}' não foi encontrado.")
    except Exception as e:
        print(f" Erro ao ler o dataset: {e}")

    # Definir a malha urbana de Braga
    s1 = Segmento("UMinho_Gualtar", "Braga_Parque",       1200, 19, 85, 45, 60,  1, "regular",   "sim", "boa")
    s2 = Segmento("UMinho_Gualtar", "Bom_Jesus",          3500, 17, 95, 20, 90, 18, "regular",   "sim", "media")
    s3 = Segmento("Braga_Parque",   "Praca_Republica",    1500, 22, 50, 75, 20,  2, "irregular", "sim", "excelente")
    s4 = Segmento("Praca_Republica","Estacao_Comboios",    800, 21, 40, 85, 10,  1, "regular",   "sim", "excelente")
    s5 = Segmento("Braga_Parque",   "Estacao_Comboios",   2500, 20, 45, 70, 15,  2, "regular",   "sim", "boa")
    s6 = Segmento("Praca_Republica","Bom_Jesus",          4000, 18, 80, 30, 70, 15, "irregular", "sim", "media")

    for s in [s1, s2, s3, s4, s5, s6]:
        rede.adicionar_segmento(s)

    print("Sistema inicializado com a malha urbana completa de 'Braga Saudável'.")


def main():
    rede = RedeUrbana()
    utilizadores = ArvoreUtilizadores() 
    motor_analise = MotorAnalise()
    motor_recomendacao = MotorRecomendacao(motor_analise)

    inicializar_braga(rede, utilizadores)
    
    total_users = 0
    if utilizadores._raiz is not None:
        total_users = 1000 
        
    View.mostrar_boas_vindas(total_users)

    while True:
        try:
            entrada = input("> ").strip()
            if not entrada:
                continue

            partes = entrada.split()
            comando = partes[0].lower()

            if comando == "recomendar":
                if len(partes) >= 4:
                    origem = partes[1]
                    destino = partes[2]
                    id_utilizador = partes[3]
                    modo_escolhido = partes[4] if len(partes) > 4 else "padrao"

                    if origem == destino:
                        print("⚠️ Aviso: A origem e o destino são o mesmo local. Já te encontras no destino!")
                        continue

                    user_atual = utilizadores.procurar(id_utilizador)

                    if user_atual is not None:
                        caminho, custo = motor_recomendacao.encontrar_melhor_caminho(rede, origem, destino, user_atual, modo_escolhido)
                        
                        View.mostrar_resultado_rota(origem, destino, user_atual, modo_escolhido, caminho, custo, motor_analise)
                        
                        if caminho:
                            user_atual.adicionar_historico(origem, destino, modo_escolhido, custo)
                            
                            todas_rotas = motor_recomendacao.encontrar_todos_caminhos(rede, origem, destino, user_atual, modo_escolhido)
                            if len(todas_rotas) > 1:
                                VisualizacaoDados.comparar_rotas(todas_rotas, origem, destino)
                    else:
                        print(f"Erro: Utilizador com ID '{id_utilizador}' não encontrado.")
                else:
                    print("Erro: Formato inválido. Utiliza: recomendar <origem> <destino> <id_utilizador> [modo]")

            elif comando == "historico":
                if len(partes) == 2:
                    id_utilizador = partes[1]
                    user_atual = utilizadores.procurar(id_utilizador)
                    if user_atual:
                        View.mostrar_historico(user_atual)
                    else:
                        print("Erro: Utilizador não encontrado.")
                else:
                    print("Erro: Formato inválido. Utiliza: historico <id_utilizador>")

            elif comando == "procurar":
                if len(partes) == 2:
                    id_utilizador = partes[1]
                    user_atual = utilizadores.procurar(id_utilizador)
                    if user_atual:
                        View.mostrar_perfil(user_atual)
                    else:
                        print("Erro: Utilizador não encontrado na base de dados.")
                else:
                    print("Erro: Formato inválido. Utiliza: procurar <id_utilizador>")

            elif comando == "ins_utilizador":
                if len(partes) >= 5:
                    novo_id = f"U{random.randint(2000, 9999)}"
                    nome = partes[1]
                    try:
                        idade = int(partes[2])
                    except ValueError:
                        print("Erro: Idade deve ser um número inteiro.")
                        continue
                        
                    sexo = partes[3].upper()
                    if sexo not in ["M", "F", "OUTRO"]:
                        print("Erro: Sexo deve ser M, F ou OUTRO.")
                        continue
                        
                    perfil = " ".join(partes[4:])
                    novo_user = Utilizador(novo_id, nome, idade, sexo, perfil)
                    utilizadores.inserir(novo_user)
                    print(f" Utilizador {nome} inserido com ID: {novo_id}")
                else:
                    print("Erro: Formato inválido. Utiliza: ins_utilizador <nome> <idade> <sexo> <perfil>")

            elif comando == "ins_percurso":
                if len(partes) == 12:
                    origem = partes[1]
                    destino = partes[2]
                    try:
                        distancia = float(partes[3])
                        temp = float(partes[4])
                        ar = float(partes[5])
                        ruido = float(partes[6])
                        verdes = float(partes[7])
                        inclinacao = float(partes[8])
                        passadeiras = partes[10]
                        
                        if not (0 <= ar <= 100):
                            print("Erro: Qualidade do ar deve estar entre 0 e 100.")
                            continue
                            
                        if inclinacao < 0:
                            print("Erro: Inclinação deve ser um valor positivo ou zero.")
                            continue
                            
                    except ValueError:
                        print("Erro: Os valores numéricos introduzidos são inválidos.")
                        continue

                    pavimento = partes[9].lower()
                    if pavimento not in ["regular", "irregular"]:
                        print("Erro: Pavimento deve ser 'regular' ou 'irregular'.")
                        continue
                        
                    iluminacao = partes[11]

                    novo_seg = Segmento(origem, destino, distancia, temp, ar, ruido, verdes, inclinacao, pavimento, passadeiras, iluminacao)
                    rede.adicionar_segmento(novo_seg)
                    print(f" Percurso {origem} -> {destino} inserido.")
                else:
                    print("Erro: Formato inválido para ins_percurso.")

            elif comando == "mapa":
                View.mostrar_mapa()
                
            elif comando == "estatisticas":
                VisualizacaoDados.raio_x_cidade(rede)
            
            elif comando == "analise_utilizadores":
                VisualizacaoDados.analise_utilizadores(utilizadores)
                
            elif comando == "list":
                if len(partes) >= 2:
                    subcomando = partes[1].lower()
                    if subcomando == "percursos":
                        # Listar todos os percursos
                        print("\n" + "="*60)
                        print("LISTA DE PERCURSOS DA REDE")
                        print("="*60)
                        ruas_vistas = set()
                        contador = 0
                        
                        for origem, conexoes in rede._grafo.items():
                            for seg in conexoes:
                                destino = seg.get_destino()
                                id_rua = tuple(sorted([origem, destino]))
                                
                                if id_rua not in ruas_vistas:
                                    ruas_vistas.add(id_rua)
                                    contador += 1
                                    print(f"\n{contador}. {seg.get_origem()} → {seg.get_destino()}")
                                    print(f"   Distância: {seg.get_distancia()}m")
                                    print(f"   Qualidade Ar: {seg.get_qualidade_ar()} | Ruído: {seg.get_ruido()} | Verdes: {seg.get_zonas_verdes()}")
                                    print(f"   Inclinação: {seg.get_inclinacao()}° | Pavimento: {seg.get_pavimento()} | Iluminação: {seg.get_iluminacao()}")
                        
                        if contador == 0:
                            print("Nenhum percurso registado.")
                        print("="*60)
                    
                    elif subcomando == "utilizadores":
                        # Listar todos os utilizadores
                        print("\n" + "="*60)
                        print("LISTA DE UTILIZADORES")
                        print("="*60)
                        todos = utilizadores.listar_todos()
                        if not todos:
                            print("Nenhum utilizador registado.")
                        else:
                            for i, user in enumerate(todos, 1):
                                print(f"{i}. {user}")
                        print("="*60)
                    else:
                        print("Erro: Subcomando inválido. Utiliza: list percursos ou list utilizadores")
                else:
                    print("Erro: Formato inválido. Utiliza: list <percursos|utilizadores>")
            
            elif comando == "gravar":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    gravar_dados(rede, utilizadores, ficheiro)
                else:
                    print("Erro: Formato inválido. Utiliza: gravar <ficheiro>")
            
            elif comando == "ler":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    carregar_dados(rede, utilizadores, ficheiro)
                else:
                    print("Erro: Formato inválido. Utiliza: ler <ficheiro>")
            
            elif comando == "ajuda":
                View.mostrar_ajuda()
                
            elif comando == "ver":
                if len(partes) == 3:
                    origem = partes[1]
                    destino = partes[2]
                    conexoes = rede.obter_conexoes(origem)
                    segmento_encontrado = None
                    
                    for seg in conexoes:
                        if seg.get_destino() == destino:
                            segmento_encontrado = seg
                            break
                    
                    View.mostrar_detalhes_segmento(origem, destino, segmento_encontrado)
                else:
                    print("Erro: Formato inválido. Utiliza: ver <origem> <destino>")

            elif comando == "sair":
                print("A encerrar o sistema. Boas viagens!")
                break
            else:
                print("Comando não reconhecido.")
                print("Comandos: ajuda, recomendar, mapa, estatisticas, analise_utilizadores, ver,")
                print("          procurar, historico, ins_utilizador, ins_percurso, list, gravar, ler, sair")

        except Exception as e:
            print(f" Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
