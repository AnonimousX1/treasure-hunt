# Autor: Henrxque
# Descrição: Este código implementa o gerenciamento dos comandos enviados ao servidor
# Data de criação: 02/01/2024
# Versão: 1.0
# Licença: MIT (se aplicável, caso contrário, use a licença apropriada)


from rImportar import threading, pickle, socket, time, respostaJogadores, Salas, Jogadores, lock

# Função para determinar a nova posição do jogador
def determinarNovaPosicao(coordenadas, comando, mapa):
    linha, coluna = coordenadas
    nova_linha, nova_coluna = linha, coluna

    if comando == "up" and linha > 0:
        nova_linha -= 1
    elif comando == "down" and linha < len(mapa) - 1:
        nova_linha += 1
    elif comando == "left" and coluna > 0:
        nova_coluna -= 1
    elif comando == "right" and coluna < len(mapa[0]) - 1:
        nova_coluna += 1
    else:
        print("Movimento inválido: fora dos limites do mapa.")
        return None

    return nova_linha, nova_coluna

def pegarTesouro(id_Jogador, nova_linha, nova_coluna, sala_atual):
    jogador = Jogadores[id_Jogador]

    with lock:
        # Considera semáforos na sala principal
        if sala_atual == "Principal":
            tesouros_semaforos = Salas[sala_atual].get("tesouros_semaforos", {})
            semaforo_tesouro = tesouros_semaforos.get((nova_linha, nova_coluna), threading.Semaphore(1))
            if not semaforo_tesouro.acquire(blocking=False):
                print(f"Tesouro em ({nova_linha}, {nova_coluna}) já foi adquirido por outro jogador.")
                return

        jogador["tesouros_jogador"] += 1
        Salas[sala_atual]["tesouros_restantes"] -= 1
        Salas[sala_atual]["mapa"][nova_linha][nova_coluna] = " . "

    print(f"Jogador {id_Jogador} pegou um tesouro!")
    print(f"Restam: {Salas[sala_atual]['tesouros_restantes']} tesouros na sala {sala_atual}")

# Função para gerenciar o movimento do jogador
def gerenciarMovimento(id_Jogador, comando):
    jogador = Jogadores[id_Jogador]
    sala_atual = jogador["coordenadas_sala"]
    antiga_posicao = tuple(jogador["coordenadas_jogador"])  # Salva a posição antiga

    mapa_atual = Salas[sala_atual]["mapa"]

    nova_posicao = determinarNovaPosicao(jogador["coordenadas_jogador"], comando, mapa_atual)
    if not nova_posicao:
        return False  # Movimento inválido
    nova_linha, nova_coluna = nova_posicao

    # Remover sombra ao entrar na sala de tesouro
    antiga_linha, antiga_coluna = antiga_posicao
    if sala_atual == "Principal" and mapa_atual[nova_linha][nova_coluna] == " P ":
        mapa_atual[antiga_linha][antiga_coluna] = " . "

    if not verificarColisoes(id_Jogador, nova_posicao, mapa_atual, sala_atual):
        return False  # Movimento bloqueado

    # Verificar se o jogador está pegando um tesouro
    if mapa_atual[nova_linha][nova_coluna] == " T ":
        pegarTesouro(id_Jogador, nova_linha, nova_coluna, sala_atual)

    atualizarCoordenadas(id_Jogador, nova_posicao)
    atualizarMapa(id_Jogador, antiga_posicao)

    return True

# Função para verificar colisões
def verificarColisoes(id_Jogador, nova_posicao, mapa_atual, sala_atual):
    nova_linha, nova_coluna = nova_posicao

    if mapa_atual[nova_linha][nova_coluna] == " X ":
        print(f"Movimento inválido: posição ({nova_linha}, {nova_coluna}) já ocupada por outro jogador.")
        return False

    if sala_atual == "Principal" and mapa_atual[nova_linha][nova_coluna] == " P ":
        portal = Salas.get((nova_linha, nova_coluna))
        if portal and not portal["semaforo"].acquire(blocking=False):
            print(f"Movimento inválido: portal em ({nova_linha}, {nova_coluna}) está ocupado.")
            return False

    return True

# Função para atualizar as coordenadas do jogador
def atualizarCoordenadas(id_Jogador, nova_posicao):
    jogador = Jogadores[id_Jogador]
    linha, coluna = nova_posicao
    sala_atual = jogador["coordenadas_sala"]

    jogador["coordenadas_jogador"] = (linha, coluna)

    if sala_atual == "Principal" and Salas["Principal"]["mapa"][linha][coluna] == " P ":
        #pega esta nova sala
        nova_sala = (linha, coluna)
        jogador["coordenadas_sala"] = (linha, coluna)
        jogador["coordenadas_jogador"] = (0, 0)
        jogador["em_sala_de_tesouro"] = True

        # Inicia o gerenciamento da sala de tesouro em uma thread
        threading.Thread(target=gerenciarSalaTesouro, args=(id_Jogador, nova_sala), daemon=True).start()


    # informo que se linha e coluna são negativas então jogador foi expulso da sala
    elif linha < 0 and coluna < 0:
        jogador["coordenadas_sala"] = "Principal"
        jogador["coordenadas_jogador"] = (0, 0)
        jogador["em_sala_de_tesouro"] = False

    # Continua a escuta de comandos na sala principal
    print(f"Jogador {id_Jogador} agora está em {jogador['coordenadas_sala']} com coordenadas {jogador['coordenadas_jogador']}.")

# Função para atualizar o mapa
def atualizarMapa(id_Jogador, antiga_posicao):
    jogador = Jogadores[id_Jogador]
    sala_atual = jogador["coordenadas_sala"]
    nova_linha, nova_coluna = jogador["coordenadas_jogador"]

    antiga_linha, antiga_coluna = antiga_posicao

    if sala_atual == "Principal":
        mapa_principal = Salas["Principal"]["mapa"]
        mapa_principal[antiga_linha][antiga_coluna] = " . "
        mapa_principal[nova_linha][nova_coluna] = " X "
        respostaJogadores(None, id_Jogador)
    else:
        sala_tesouro = Salas[sala_atual]
        mapa_tesouro = sala_tesouro["mapa"]
        mapa_tesouro[antiga_linha][antiga_coluna] = " . "
        mapa_tesouro[nova_linha][nova_coluna] = " X "
        respostaJogadores(jogador["socket"], id_Jogador)

# Função para gerenciar movimentos na sala de tesouro com temporizador de 15 segundos
def gerenciarSalaTesouro(id_Jogador, sala_tesouro):
    jogador = Jogadores[id_Jogador]
    client_socket = jogador["socket"]
    client_socket.settimeout(10)  # Timeout para não bloquear indefinidamente, passou 10 segundos derruba
    tempo_inicio = time.time()
    tempo_maximo = 7  # Tempo máximo em segundos

    try:
        while True:
            if time.time() - tempo_inicio >= tempo_maximo:
                print(f"Tempo esgotado: jogador {id_Jogador} foi expulso da sala de tesouro.")
                break

            try:
                comando = client_socket.recv(4096).decode('utf-8')  # Recebendo comando do cliente
            except socket.timeout:
                continue  # Timeout do socket, volta para o loop para verificar o tempo restante

            if not comando:
                print(f"Jogador {id_Jogador} desconectado dentro da sala de tesouro.")
                break

            if comando in ["up", "down", "left", "right"]:
                # Reaproveitando a função gerenciarMovimento
                if not gerenciarMovimento(id_Jogador, comando):
                    print(f"Movimento inválido para jogador {id_Jogador}.")
                else:
                    print(f"Jogador {id_Jogador} se moveu dentro da sala de tesouro com o comando '{comando}'.")
            else:
                print(f"Comando desconhecido '{comando}' recebido do jogador {id_Jogador}.")

    except Exception as e:
        print(f"Erro na sala de tesouro para jogador {id_Jogador}: {e}")

    finally:
        with lock:
            linha, coluna =  jogador["coordenadas_jogador"]
            Salas[sala_tesouro]["semaforo"].release()
            Salas[sala_tesouro]["mapa"][linha][coluna] = " . "  # Libera a posição no mapa
        client_socket.settimeout(None)  # Retorna ao modo de bloqueio padrão
        atualizarCoordenadas(id_Jogador, (-1, -1))# Marca que o jogador está fora da sala
        print(f"Jogador {id_Jogador} foi expulso e retornado à sala principal.")