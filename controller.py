from dados import Utilizador, Segmento, RedeUrbana
import json
from model import MotorAnalise, MotorRecomendacao

def inicializar_braga(rede, utilizadores, ficheiro_dataset="dataset_utilizadores.json"):
    try:
        with open(ficheiro_dataset, 'r', encoding='utf-8') as f:
            dados_users = json.load(f)
  
            for user in dados_users:
                uid = user["id"]
                novo_user = Utilizador(
                    id_utilizador=uid,
                    nome=user["nome"],
                    idade=user["idade"],
                    sexo=user["sexo"],
                    perfil=user["perfil"]
                )
                utilizadores[uid] = novo_user
                
        print(f" Sucesso: {len(utilizadores)} utilizadores carregados do dataset!")
        
    except FileNotFoundError:
        print(f" Aviso: O ficheiro '{ficheiro_dataset}' não foi encontrado. A arrancar a rede sem utilizadores iniciais.")
    except Exception as e:
        print(f" Erro ao ler o dataset de utilizadores: {e}")

    s1 = Segmento("UMinho_Gualtar", "Braga_Parque", 1200, 19, 85, 45, 60, 1, "regular", "sim", "boa")
    s2 = Segmento("UMinho_Gualtar", "Bom_Jesus", 3500, 17, 95, 20, 90, 18, "regular", "sim", "media")
    s3 = Segmento("Braga_Parque", "Praca_Republica", 1500, 22, 50, 75, 20, 2, "irregular", "sim", "excelente")
    s4 = Segmento("Praca_Republica", "Estacao_Comboios", 800, 21, 40, 85, 10, 1, "regular", "sim", "excelente")
    s5 = Segmento("Braga_Parque", "Estacao_Comboios", 2500, 20, 45, 70, 15, 2, "regular", "sim", "boa")
    s6 = Segmento("Praca_Republica", "Bom_Jesus", 4000, 18, 80, 30, 70, 15, "irregular", "sim", "media")

    for s in [s1, s2, s3, s4, s5, s6]:
        rede.adicionar_segmento(s)

    print(" Sistema inicializado com a malha urbana 'Braga Saudável'.")

def main():
    rede = RedeUrbana()
    utilizadores = {}
    
    motor_analise = MotorAnalise()
    motor_recomendacao = MotorRecomendacao(motor_analise)

    inicializar_braga(rede, utilizadores)

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
                
            elif comando == "ins_utilizador":
                if len(partes) >= 3:
                    perfil = partes[-1]
                    nome = " ".join(partes[1:-1])
                    
                    novo_id = f"U{len(utilizadores) + 1:05d}"
                    
                    novo_utilizador = Utilizador(novo_id, nome, 0, "N/A", perfil)
                    
                    utilizadores[novo_id] = novo_utilizador
                    
                    print(f"Sucesso: Utilizador '{nome}' ({perfil}) registado com o ID {novo_id}.")
                else:
                    print("Erro: Formato inválido. Utiliza: ins_utilizador <nome> <perfil>")
            
            elif comando == "ler":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    try:
                        with open(ficheiro, 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                        
                        for d in dados:
                            novo_user = Utilizador(d["id"], d["nome"], d["idade"], d["sexo"], d["perfil"])
                            utilizadores[d["id"]] = novo_user
                            
                        print(f"Sucesso: {len(dados)} utilizadores carregados do ficheiro '{ficheiro}'.")
                        
                    except FileNotFoundError:
                        print(f"Erro: O ficheiro '{ficheiro}' não foi encontrado no sistema.")
                    except json.JSONDecodeError:
                        print(f"Erro: O ficheiro '{ficheiro}' não possui uma formatação JSON válida.")
                    except KeyError as e:
                        print(f"Erro: Estrutura de dados inválida. Chave em falta: {e}")
                    except Exception as e:
                        print(f"Erro crítico e inesperado: {e}")
                else:
                    print("Erro: Formato inválido. Utiliza: ler <ficheiro>")

            elif comando == "ins_percurso":
                if len(partes) == 12:
                    try:
                        origem = partes[1]
                        destino = partes[2]
                        distancia = float(partes[3])
                        temp = float(partes[4])
                        ar = float(partes[5])
                        ruido = float(partes[6])
                        zonas_verdes = float(partes[7])
                        inclinacao = float(partes[8])
                        pavimento = partes[9]
                        passadeiras = partes[10]
                        iluminacao = partes[11]

                        novo_segmento = Segmento(
                            origem, destino, distancia, temp, ar, ruido,
                            zonas_verdes, inclinacao, pavimento, passadeiras, iluminacao
                        )
                        
                        rede.adicionar_segmento(novo_segmento)
                        
                        print(f"Sucesso: Segmento de '{origem}' para '{destino}' adicionado com sucesso.")

                    except ValueError:
                        print("Erro: A distância e os indicadores numéricos (temp, ar, ruido, verdes, inclinacao) devem ser valores numéricos.")
                else:
                    print("Erro: Formato inválido. Utiliza: ins_percurso <origem> <destino> <distancia> <temp> <ar> <ruido> <verdes> <inclinacao> <pavimento> <passadeiras> <iluminacao>")
            
            elif comando == "list" and len(partes) == 2 and partes[1] == "percursos":
                print(rede)
                
            elif comando == "ver":
                if len(partes) == 3:
                    origem = partes[1]
                    destino = partes[2]
                    conexoes = rede.obter_conexoes(origem)
                    encontrado = False
                    
                    for seg in conexoes:
                        if seg.get_destino() == destino:
                            print(f"\n--- Detalhes do Percurso: {origem} -> {destino} ---")
                            print(f"Distância: {seg.get_distancia()}m")
                            print(f"Ambiente -> Temp: {seg.get_temperatura()} | Ar: {seg.get_qualidade_ar()} | Ruído: {seg.get_ruido()} | Verdes: {seg.get_zonas_verdes()}")
                            print(f"Acessibilidade -> Inclinação: {seg.get_inclinacao()} | Pavimento: {seg.get_pavimento()} | Passadeiras: {seg.get_passadeiras()} | Iluminação: {seg.get_iluminacao()}\n")
                            encontrado = True
                            break
                            
                    if not encontrado:
                        print(f"Aviso: Não existe um segmento direto registado entre '{origem}' e '{destino}'.")
                else:
                    print("Erro: Formato inválido. Utiliza: ver <origem> <destino>")
            
            elif comando == "recomendar":
                if len(partes) >= 4:
                    origem = partes[1]
                    destino = partes[2]
                    id_utilizador = partes[3]
                    modo_escolhido = partes[4] if len(partes) > 4 else "padrao"

                    if id_utilizador in utilizadores:
                        user_atual = utilizadores[id_utilizador]
                        print(f"\n A calcular rota de '{origem}' para '{destino}' para {user_atual.get_nome()} (Modo: {modo_escolhido})...")

                        caminho, custo = motor_recomendacao.encontrar_melhor_caminho(rede, origem, destino, user_atual, modo_escolhido)

                        if caminho:
                            print("\n Percurso Encontrado!")
                            print(f"Custo total (Índice de Conforto): {custo}")
                            distancia_total = sum(seg.get_distancia() for seg in caminho)
                            print(f"Distância total: {distancia_total}m")

                            print("\n Itinerário:")
                            for i, seg in enumerate(caminho, 1):
                                print(f"  {i}. {seg.get_origem()} -> {seg.get_destino()} ({seg.get_distancia()}m)")
                            print("\n Destino atingido com sucesso! ")
                        else:
                            print(f"\n Aviso: Não foi possível encontrar um caminho seguro entre '{origem}' e '{destino}'.")

                    else:
                        print(f"Erro: Utilizador com ID '{id_utilizador}' não encontrado.")
                else:
                    print("Erro: Formato inválido. Utiliza: recomendar <origem> <destino> <id_utilizador> [modo_opcional]")
            
            elif comando == "gravar":
                if len(partes) == 2:
                    ficheiro = partes[1]
                    try:
                        dados_exportar = []
                        
                        for uid, user in utilizadores.items():
                            dados_exportar.append({
                                "id": uid,
                                "nome": user.get_nome(),
                                "idade": user.get_idade(),
                                "sexo": user.get_sexo(),
                                "perfil": user.get_perfil()
                            })
                        
                        with open(ficheiro, 'w', encoding='utf-8') as f:
                            json.dump(dados_exportar, f, ensure_ascii=False, indent=4)
                            
                        print(f"Sucesso: Dados de {len(utilizadores)} utilizadores guardados de forma segura em '{ficheiro}'.")
                        
                    except Exception as e:
                        print(f"Erro crítico ao tentar gravar o ficheiro: {e}")
                else:
                    print("Erro: Formato inválido. Utiliza: gravar <ficheiro>")
                
            else:
                print("Erro: Comando não reconhecido.")
            
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()