from dados import Utilizador, Segmento, RedeUrbana
import json

def main():
    rede = RedeUrbana()
    utilizadores = {}

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
                
            else:
                print("Erro: Comando não reconhecido.")
            
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()