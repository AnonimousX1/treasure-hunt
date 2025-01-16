# Autor: Henrxque
# Descrição: Este código implementa os mapas jogaveis pelos jogadores
# Data de criação: 02/01/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)


from rImportar import random, math, Salas, Semaphore

def criarSalaPrincipal(tamanho_sala_principal, qtd_tesouros_principal, qtd_portais, tamanho_sala_tesouro):
    """
    Cria a sala principal e associa portais a salas de tesouro.
    """
    matriz_principal = [[" . " for _ in range(tamanho_sala_principal)] for _ in range(tamanho_sala_principal)]

    # Garante que a posição inicial do jogador esteja livre
    matriz_principal[0][0] = " . "

    # Adiciona tesouros na sala principal
    tesouros_semaforos = {}
    for tesouro_id in range(qtd_tesouros_principal):
        while True:
            x, y = random.randint(0, tamanho_sala_principal - 1), random.randint(0, tamanho_sala_principal - 1)
            if matriz_principal[x][y] == " . ":
                matriz_principal[x][y] = " T "
                tesouros_semaforos[(x, y)] = Semaphore(1)
                break

    # Adiciona portais e cria salas de tesouro
    for portal_id in range(qtd_portais):
        while True:
            x, y = random.randint(0, tamanho_sala_principal - 1), random.randint(0, tamanho_sala_principal - 1)
            if matriz_principal[x][y] == " . ":
                matriz_principal[x][y] = " P "
                qtd_tesouros_tesouro = random.randint(1, tamanho_sala_tesouro ** 2 // 5)
                Salas[(x, y)] = {
                    "mapa": criarSalaTesouro(tamanho_sala_tesouro, qtd_tesouros_tesouro),
                    "semaforo": Semaphore(1),
                    "tesouros_restantes": qtd_tesouros_tesouro,
                }
                break
            elif matriz_principal[x][y] == " T ":
                # Sorteia novamente para evitar conflito com tesouro
                continue

    # Adiciona a sala principal no dicionário
    Salas["Principal"] = {
        "mapa": matriz_principal,
        "tesouros_restantes": qtd_tesouros_principal,
        "tesouros_semaforos": tesouros_semaforos,  # Associa os semáforos aos tesouros
    }


def criarSalaTesouro(tamanho_sala_tesouro, qtd_tesouros_tesouro):
    """
    Cria uma sala de tesouro com tesouros distribuídos aleatoriamente.
    """
    if math.pow(tamanho_sala_tesouro, 2) <= qtd_tesouros_tesouro:
        print("Quantidade de tesouros é maior ou igual ao tamanho da sala!")
        return None

    matriz_tesouro = [[" . " for _ in range(tamanho_sala_tesouro)] for _ in range(tamanho_sala_tesouro)]

    for _ in range(qtd_tesouros_tesouro):
        while True:
            x, y = random.randint(0, tamanho_sala_tesouro - 1), random.randint(0, tamanho_sala_tesouro - 1)
            if matriz_tesouro[x][y] == " . ":
                matriz_tesouro[x][y] = " T "
                break

    return matriz_tesouro

#Testes
'''
criarSalaPrincipal(5,5,6,3) #Log
print(f"Get: {Salas['Principal']}") #Log
print(f"Indices: {Salas['Principal']['mapa']}")
'''