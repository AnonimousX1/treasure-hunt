# Autor: Henrxque
# Descrição: Este código implementa, as teclas dos usuários.
# Data de criação: 16/12/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)


import keyboard

# Controle de estado para evitar repetições
keys_pressed = set()

# Tamanho da matriz
MATRIZ_TAMANHO = 5  # Exemplo: matriz 5x5
ponto = [2, 2]  # Posição inicial do ponto (linha, coluna)


def Centralizar(ponto):
    if (MATRIZ_TAMANHO % 2 == 0):
        x = (MATRIZ_TAMANHO) / 2
        y = (MATRIZ_TAMANHO) / 2
        ponto[0] = x
        ponto[1] = y
    else:
        x = (MATRIZ_TAMANHO - 1) / 2
        y = (MATRIZ_TAMANHO - 1) / 2
        ponto[0] = x
        ponto[1] = y


# Movimentos

def tecla_enter():
    return "Entrar"

def tecla_cima():
    global ponto
    if ponto[0] > 0:  # Verifica se não está na borda superior
        ponto[0] -= 1
    return ponto


def tecla_baixo():
    global ponto
    if ponto[0] < MATRIZ_TAMANHO - 1:  # Verifica se não está na borda inferior
        ponto[0] += 1
    return ponto


def tecla_esquerda():
    global ponto
    if ponto[1] > 0:  # Verifica se não está na borda esquerda
        ponto[1] -= 1
    return ponto


def tecla_direita():
    global ponto
    if ponto[1] < MATRIZ_TAMANHO - 1:  # Verifica se não está na borda direita
        ponto[1] += 1
    return ponto


def key_handler(event):
    global keys_pressed

    # Evita repetir ações enquanto a tecla estiver pressionada
    if event.name not in keys_pressed:
        keys_pressed.add(event.name)

        if event.name == 'up':
            tecla_cima()
        elif event.name == 'down':
            tecla_baixo()
        elif event.name == 'left':
            tecla_esquerda()
        elif event.name == 'right':
            tecla_direita()
        elif event.name == 'enter':
             tecla_enter()

        elif event.name == 'esc':
            print("Saindo...")
            keyboard.unhook_all()  # Desativa todos os eventos de teclado
            exit()

    # Remove a tecla imediatamente para permitir novas capturas
    keys_pressed.discard(event.name)


def key_release(event):
    global keys_pressed
    # Remove a tecla do conjunto quando ela é liberada
    keys_pressed.discard(event.name)


def IniciarTeclas():
    """
    Captura uma única tecla pressionada e retorna seu nome.
    """
    event = keyboard.read_event()  # Captura o evento de teclado
    if event.event_type == "down":  # Verifica se a tecla foi pressionada
        return event.name  # Retorna o nome da tecla pressionada