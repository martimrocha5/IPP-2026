from dados import Utilizador, Segmento, RedeUrbana
import json
from model import MotorAnalise, MotorRecomendacao
from arvores import ArvoreUtilizadores
from view import View
from graficos import VisualizacaoDados

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
    print("\nDigita 'ajuda' para veres todos os comandos disponíveis.\n")

    while True:
        try:
            entrada = input("> ").strip()
            if not entrada:
                continue

            partes = entrada.split()
            comando = partes[0].lower()

            if comando == "sair":
                print("Sistema encerrado com sucesso.")
                break

            elif comando == "ajuda":
                View.mostrar_ajuda()

            elif comando == "ins_utilizador":
                if len(partes) >= 3:
                    perfil = partes[-1]
                    nome = " ".join(partes[1:-1])

                    novo_id = f"U{len(utilizadores) + 1:05d}"

                    while utilizadores.procurar(novo_id) is not None:
                        novo_id = f"U{int(novo_id[1:]) + 1:05d}"

                    novo_utilizador = Utilizador(novo_id, nome, 0, "N/A", perfil)
                    utilizadores.inserir(novo_utilizador)

                    print(f" Sucesso: Utilizador '{nome}' ({perfil}) registado com o ID {novo_id}.")
                else:
                    print("Erro: Formato inválido. Utiliza: ins_utilizador <nome> <perfil>")

            elif comando == "ler":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    try:
                        with open(ficheiro, 'r', encoding='utf-8') as f:
                            dados = json.load(f)

                        count = 0
                        for d in dados:
                            novo_user = Utilizador(
                                d["id"], d["nome"], d["idade"], d["sexo"], d["perfil"]
                            )
                            utilizadores.inserir(novo_user)
                            count += 1

                        print(f" Sucesso: {count} utilizadores carregados do ficheiro '{ficheiro}'.")

                    except FileNotFoundError:
                        print(f" Erro: O ficheiro '{ficheiro}' não foi encontrado no sistema.")
                    except json.JSONDecodeError:
                        print(f" Erro: O ficheiro '{ficheiro}' não possui uma formatação JSON válida.")
                    except KeyError as e:
                        print(f" Erro: Estrutura de dados inválida. Chave em falta: {e}")
                    except Exception as e:
                        print(f" Erro crítico e inesperado: {e}")
                else:
                    print("Erro: Formato inválido. Utiliza: ler <ficheiro>")

            elif comando == "ins_percurso":
                if len(partes) == 12:
                    try:
                        origem       = partes[1]
                        destino      = partes[2]
                        distancia    = float(partes[3])
                        temp         = float(partes[4])
                        ar           = float(partes[5])
                        ruido        = float(partes[6])
                        zonas_verdes = float(partes[7])
                        inclinacao   = float(partes[8])
                        pavimento    = partes[9]
                        passadeiras  = partes[10]
                        iluminacao   = partes[11]

                        novo_segmento = Segmento(
                            origem, destino, distancia, temp, ar, ruido,
                            zonas_verdes, inclinacao, pavimento, passadeiras, iluminacao
                        )
                        rede.adicionar_segmento(novo_segmento)
                        print(f" Sucesso: Segmento '{origem}' -> '{destino}' adicionado com sucesso.")

                    except ValueError:
                        print(" Erro: Os valores numéricos (distancia, temp, ar, ruido, verdes, inclinacao) devem ser números.")
                else:
                    print(" Erro: Formato inválido.")
                    print(" Uso: ins_percurso <origem> <destino> <distancia> <temp> <ar> <ruido> <verdes> <inclinacao> <pavimento> <passadeiras> <iluminacao>")

            elif comando == "list":
                if len(partes) == 2 and partes[1] == "percursos":
                    print(rede)

                elif len(partes) == 2 and partes[1] == "utilizadores":
                    todos = utilizadores.listar_todos()
                    if todos:
                        print(f"\n Total de utilizadores registados: {len(todos)}")
                        print("-" * 60)
                        for u in todos:
                            print(u)
                        print("-" * 60)
                    else:
                        print(" Aviso: Não há utilizadores registados no sistema.")
                else:
                    print(" Erro: Comando inválido. Usa: list percursos  |  list utilizadores")

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
                    print(" Erro: Formato inválido. Utiliza: ver <origem> <destino>")

            elif comando == "recomendar":
                if len(partes) >= 4:
                    origem        = partes[1]
                    destino       = partes[2]
                    id_utilizador = partes[3]
                    modo_escolhido = partes[4] if len(partes) > 4 else "padrao"

                    user_atual = utilizadores.procurar(id_utilizador)

                    if user_atual is not None:
                        print(f"\n A calcular rota de '{origem}' para '{destino}' "
                              f"para {user_atual.get_nome()} (Modo: {modo_escolhido})...")

                        caminho, custo = motor_recomendacao.encontrar_melhor_caminho(
                            rede, origem, destino, user_atual, modo_escolhido
                        )

                        View.mostrar_resultado_rota(
                            origem, destino, user_atual.get_nome(), modo_escolhido, caminho, custo
                        )
                    else:
                        print(f" Erro: Utilizador com ID '{id_utilizador}' não encontrado na Árvore.")
                else:
                    print(" Erro: Formato inválido.")
                    print(" Uso: recomendar <origem> <destino> <id_utilizador> [modo_opcional]")
                    print(" Modos disponíveis: padrao | relaxar | exercicio | ar_puro")

            elif comando == "gravar":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    try:
                        todos_users = utilizadores.listar_todos()
                        dados_exportar = []

                        for user in todos_users:
                            dados_exportar.append({
                                "id":     user.get_id(),
                                "nome":   user.get_nome(),
                                "idade":  user.get_idade(),
                                "sexo":   user.get_sexo(),
                                "perfil": user.get_perfil()
                            })

                        with open(ficheiro, 'w', encoding='utf-8') as f:
                            json.dump(dados_exportar, f, ensure_ascii=False, indent=4)

                        print(f" Sucesso: {len(dados_exportar)} utilizadores guardados em '{ficheiro}'.")

                    except Exception as e:
                        print(f" Erro crítico ao tentar gravar o ficheiro: {e}")
                else:
                    print(" Erro: Formato inválido. Utiliza: gravar <ficheiro>")

            elif comando == "mapa":
                View.mostrar_mapa()

            elif comando == "estatisticas":
                if len(partes) == 1 or (len(partes) == 2 and partes[1] == "cidade"):
                    VisualizacaoDados.raio_x_cidade(rede)
                elif len(partes) == 2 and partes[1] == "utilizadores":
                    VisualizacaoDados.analise_utilizadores(utilizadores)
                else:
                    print(" Uso: estatisticas [cidade | utilizadores]")

            else:
                print(f" Erro: Comando '{comando}' não reconhecido. Digita 'ajuda' para ver os comandos disponíveis.")

        except Exception as e:
            print(f" Erro inesperado: {e}")


if __name__ == "__main__":
    main()
