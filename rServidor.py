# Autor: Henrxque
# Descrição: Este código implementa um servidor que recebe comandos de clientes independentes, e atualiza conforme a sincronização especificada nos arquivos.
# Data de criação: 16/12/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)


from rImportar import socket, threading, time, pickle, respostaJogadores, Salas, Jogadores, lock, id_unico_jogador
from rGerenciar import gerenciarMovimento, gerenciarSalaTesouro

from rMapas import criarSalaPrincipal

IP, PORTA = '192.168.0.176', 8080

def addJogador(client_socket, client_address):
    global id_unico_jogador

    with lock:  # Bloqueia para evitar condições de corrida
        id_atual = id_unico_jogador

        Jogadores[id_atual] = {
            "socket": client_socket,
            "ip": client_address[0],
            "porta": client_address[1],
            "coordenadas_jogador": (0, 0),
            "coordenadas_sala": "Principal",
            "em_sala_de_tesouro": False,
            "ativo": True,
            "tesouros_jogador": 0,
        }
        id_unico_jogador += 1
        return id_atual

def movimentoJogadores(client_socket, id_Jogador):
    # Fica ouvindo os comando dos jogadores
    try:
        while True:
            #print(f"LOG: Verificando status do jogador {Jogadores[id_Jogador]['em_sala_de_tesouro']}")
            if Jogadores[id_Jogador]["em_sala_de_tesouro"]:
                time.sleep(0.5) # se o jogador ficar 10 segundos sem mexer ele é desconectado
                continue

            comando = client_socket.recv(4096).decode('utf-8')
            if not comando:  # Cliente desconectado
                print(f"Jogador - {id_Jogador}, IP: {Jogadores[id_Jogador]['ip']} desconectado.")
                break

            if comando in ["up", "down", "left", "right"]:
                #print(f"Jogador - {id_Jogador} IP:{Jogadores[id_Jogador]['ip']} enviou movimento: {comando}")
                gerenciarMovimento(id_Jogador, comando)

            elif comando == "enter":
                print(f"Jogador - {id_Jogador} IP:{Jogadores[id_Jogador]['ip']} entrou na sala principal.")
                respostaJogadores(client_socket, id_Jogador)

            elif comando == "esc":
                print(f"Jogador - {id_Jogador}, IP: {Jogadores[id_Jogador]['ip']} saiu do jogo.")
                Jogadores[id_Jogador]['socket'].close()

                # Liberar semáforo do portal ou sala de tesouro
                linha, coluna = Jogadores[id_Jogador]["coordenadas_jogador"]
                sala_atual = Jogadores[id_Jogador]["coordenadas_sala"]

                if sala_atual != "Principal" and "semaforo" in Salas[sala_atual]:
                    with lock:
                        Salas[sala_atual]["semaforo"].release()

                # Limpar sombra do mapa
                if sala_atual in Salas:
                    with lock:
                        Salas[sala_atual]["mapa"][linha][coluna] = " . "

                # Remover jogador
                with lock:
                    del Jogadores[id_Jogador]
                break

                # Responde o jogador ou jogadores
            respostaJogadores(client_socket, id_Jogador)

    except Exception as e:
        print(f"Erro ao receber comando do {Jogadores[id_Jogador]['ip']}: {e}")

def hospedar():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORTA))
    server_socket.listen()
    print("Criando salas...")
    criarSalaPrincipal(15,15, 4, 6)

    print("Servidor pronto e aguardando conexões !")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexão estabelecida com {client_address}")

        id_Jogador = addJogador(client_socket, client_address)

        # Cria uma thread para lidar com o cliente
        client_thread = threading.Thread(target=movimentoJogadores, args=(client_socket, id_Jogador))
        client_thread.start()

hospedar()

#Teste
'''
addJogador(1,(2,2))
print(f"Jogadores: {Jogadores}")
print(f"Um jogador: {Jogadores[0]}")
print(f"Mapa de um jogador - Get: {Jogadores[0].get('coordenadas_sala')}, normal: {Jogadores[0]['coordenadas_sala']}")
'''