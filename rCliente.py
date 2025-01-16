# Autor: Henrxque
# Descrição: Este código implementa um cliente que se conecta a um servidor, envia comandos de teclado e recebe atualizações do servidor.
# Data de criação: 16/12/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)

import os
import pickle
import socket
import threading
import rTeclas

IP, PORTA = '192.168.0.176', 8080


def Cliente(IP, PORTA):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORTA))

    print("Conectado ao servidor. Pressione teclas para enviar.")

    ''' Thread para ouvir atualizações do servidor'''
    threading.Thread(target=OuvirServidor, args=(client_socket,), daemon=True).start()


    ''' Loop principal para capturar entradas do teclado'''
    while True:
        tecla = rTeclas.IniciarTeclas()  # Captura a tecla
        if tecla:
            if tecla == "esc":
                print("Saindo do Game...")
                client_socket.send(tecla.encode('utf-8'))  # Envia a tecla ao servidor
                client_socket.close()
                break

            elif tecla in ["enter", "up", "down", "left", "right"]:
                print(f"Enviando comando: {tecla}")
                client_socket.send(tecla.encode('utf-8'))  # Envia o comando ao servidor

def OuvirServidor(client_socket):
    '''Função para escutar atualizações do servidor continuamente'''
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                print("Conexão com o servidor perdida.")
                break
            matriz = pickle.loads(data)
            LimparTela()  # Limpa o terminal antes de imprimir o mapa
            print("Mapa Atualizado:")
            ImprimirTela(matriz)
        except Exception as e:
            print(f"Erro ao receber dados do servidor: {e}")
            break

def LimparTela():
    '''Limpa o terminal.'''
    os.system('cls' if os.name == 'nt' else 'clear')

def ImprimirTela(matriz):
    if isinstance(matriz, list):
        for linha in matriz:
            print("|", end=" ")
            for elemento in linha:
                print(f"{elemento}", end=" ")
            print("|")

Cliente(IP, PORTA)