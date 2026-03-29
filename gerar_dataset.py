import json
import random

def gerar_dataset_utilizadores(quantidade, nome_ficheiro="dataset_utilizadores.json"):
    # Listas separadas para garantir coerência com o sexo
    primeiros_nomes_m = ["João", "Pedro", "Tiago", "Rui", "Miguel", "Hugo", "Diogo", "Bruno", "Gonçalo", "Tomás"]
    primeiros_nomes_f = ["Ana", "Maria", "Catarina", "Beatriz", "Sofia", "Inês", "Marta", "Joana", "Leonor", "Carolina"]
    apelidos = ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues", "Martins", "Gomes", "Lopes"]
    
    # Perfis definidos no enunciado do projeto
    perfis_possiveis = ["idoso", "pessoa com mobilidade reduzida", "adulto saudável"]
    
    utilizadores = []
    
    for i in range(1, quantidade + 1):
        # 1. Gerar ID único (ex: U00001, U00002, etc.)
        id_utilizador = f"U{i:05d}"
        
        # 2. Definir o sexo e escolher o nome correspondente
        sexo = random.choice(["M", "F"])
        if sexo == "M":
            nome_completo = f"{random.choice(primeiros_nomes_m)} {random.choice(apelidos)}"
        else:
            nome_completo = f"{random.choice(primeiros_nomes_f)} {random.choice(apelidos)}"
        
        # 3. Escolher o perfil
        perfil = random.choice(perfis_possiveis)
        
        # 4. Ajustar a idade de forma lógica consoante o perfil
        if perfil == "idoso":
            idade = random.randint(65, 95)
        elif perfil == "adulto saudável":
            idade = random.randint(18, 64)
        else: # pessoa com mobilidade reduzida (pode ser qualquer idade)
            idade = random.randint(18, 95)
            
        # Construir o dicionário do utilizador
        utilizador = {
            "id": id_utilizador,
            "nome": nome_completo,
            "idade": idade,
            "sexo": sexo,
            "perfil": perfil
        }
        utilizadores.append(utilizador)
        
    # Gravar o ficheiro JSON
    with open(nome_ficheiro, 'w', encoding='utf-8') as f:
        json.dump(utilizadores, f, ensure_ascii=False, indent=4)
        
    print(f"Update concluído! Ficheiro '{nome_ficheiro}' gerado com {quantidade} utilizadores super detalhados.")

gerar_dataset_utilizadores(1000)