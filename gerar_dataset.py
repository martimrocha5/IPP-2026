"""
Script utilitário para geração do dataset de utilizadores fictícios.

Executa diretamente para (re)gerar o ficheiro dataset_utilizadores.json:
    python gerar_dataset.py
"""

import json
import random


def gerar_dataset_utilizadores(quantidade, nome_ficheiro="dataset_utilizadores.json"):
    """
    Gera um ficheiro JSON com utilizadores fictícios para testes do sistema.

    Os utilizadores são gerados com perfis e idades coerentes:
      - 'idoso'                          → 65–95 anos
      - 'adulto saudável'                → 18–64 anos
      - 'pessoa com mobilidade reduzida' → 18–95 anos

    Args:
        quantidade   : Número de utilizadores a gerar.
        nome_ficheiro: Nome do ficheiro JSON de destino.
    """
    primeiros_nomes_m = [
        "João", "Pedro", "Tiago", "Rui", "Miguel",
        "Hugo", "Diogo", "Bruno", "Gonçalo", "Tomás"
    ]
    primeiros_nomes_f = [
        "Ana", "Maria", "Catarina", "Beatriz", "Sofia",
        "Inês", "Marta", "Joana", "Leonor", "Carolina"
    ]
    apelidos = [
        "Silva", "Santos", "Ferreira", "Pereira", "Oliveira",
        "Costa", "Rodrigues", "Martins", "Gomes", "Lopes"
    ]
    perfis_possiveis = [
        "idoso",
        "pessoa com mobilidade reduzida",
        "adulto saudável"
    ]

    utilizadores = []

    for i in range(1, quantidade + 1):
        id_utilizador = f"U{i:05d}"

        # Sexo e nome
        sexo = random.choice(["M", "F"])
        primeiro = random.choice(primeiros_nomes_m if sexo == "M" else primeiros_nomes_f)
        nome_completo = f"{primeiro} {random.choice(apelidos)}"

        # Perfil e idade coerente
        perfil = random.choice(perfis_possiveis)
        if perfil == "idoso":
            idade = random.randint(65, 95)
        elif perfil == "adulto saudável":
            idade = random.randint(18, 64)
        else:   # pessoa com mobilidade reduzida — qualquer faixa etária adulta
            idade = random.randint(18, 95)

        utilizadores.append({
            "id":     id_utilizador,
            "nome":   nome_completo,
            "idade":  idade,
            "sexo":   sexo,
            "perfil": perfil
        })

    with open(nome_ficheiro, 'w', encoding='utf-8') as f:
        json.dump(utilizadores, f, ensure_ascii=False, indent=4)

    print(f"✅ Ficheiro '{nome_ficheiro}' gerado com {quantidade} utilizadores.")


# Protege a execução automática quando o módulo é importado por outros ficheiros
if __name__ == "__main__":
    gerar_dataset_utilizadores(1000)
