# Resolução de problemas de procura:
#      - Não informada:
#               - BFS (Breadth first search)
#               - DFS (Depth first search)
#               - Custo Uniforme (Dijkstra)
#      - Informada:
#               - Greedy (Gulosa)
#               - A*



# Gualtar -6- São Mamede -8- Lamaçães -3- Freião -6- Nogueiró
#    |           | 
#    8           3 - Sobreposta -6- Noguriró
#    |                  |
# São Vitor -6- São Vicente -8- Nogueiró
# 
# BFS: Gualtar, São Vitor, São Vicente, Nogueiró (menos arestas)
#
# DFS:  Gualtar, São Mamede, Lamaçães, Freião, Nogueiró (6+8+3+6=23) (vai por um caminho até enocntrar o final(lado esquerdo))
#
# Custo Uniforme: Gualtar, São Mamede, Sobreposta, Nogueiró
# (Este basicamente fez as contas todas de todos os caminhos possíveis, no entanto, aquele que dá como resposta é o com menor custo)