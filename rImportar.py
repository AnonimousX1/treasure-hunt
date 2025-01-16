# Autor: Henrxque
# Descrição: Este código importa todas as bibliotecas necessárias durante a execução do servidor
# Data de criação: 02/01/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)


import pickle
import socket
import threading
import math
import random
import time

from threading import Semaphore

#Estruturas
Jogadores = {}
Salas = {}

#Controladores
id_unico_jogador = 0
lock = threading.Lock()  # Evita condições de corrida na criação do jogador

#Funções comuns
def enviarParaTodos(Sala):
    """Envia a matriz para todos os jogadores conectados."""
    data = pickle.dumps(Sala)
    desconectados = []

    # Enviar dados para todos os jogadores
    for id_Jogador, jogador in list(Jogadores.items()):
        try:
            jogador["socket"].send(data)
        except Exception as e:
            print(f"Erro ao enviar dados para o jogador {id_Jogador}: {e}")
            desconectados.append(id_Jogador)

    return desconectados  # Retorna jogadores desconectados para remoção

def respostaJogadores(client_socket, id_Jogador):
    # Responde a os movimento dos jogadores
    try:
        if Jogadores[id_Jogador]["coordenadas_sala"] == "Principal":
            # Envia a matriz atualizada para todos os jogadores
            desconectados = enviarParaTodos(Salas['Principal']['mapa'])

            # Remove jogadores desconectados
            with lock:
                for id_jogador_desconectado in desconectados:
                    Jogadores.pop(id_jogador_desconectado, None)
        else:
            sala_atual = Salas[ Jogadores[id_Jogador]["coordenadas_sala"] ]['mapa']
            client_socket.send(pickle.dumps(sala_atual))

    except Exception as e:
        print(f"Erro ao enviar dados ao jogador {id_Jogador}: {e}")
