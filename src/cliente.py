import socket

BUFFER_SIZE = 4096
EXIT_COMMAND = "SAIR"

# Configurações do Cliente
def get_server_info():

    print("=== Coletando dados da requisição ===")

    default_host = '127.0.0.1'  # IP do Servidor (mesmo do servidor)
    default_port = 12345       # Porta do Servidor (mesma do servidor)

    host = input("Digite o IP do servidor (ex: 127.0.0.1): ").strip() or '127.0.0.1'
    if not host:
        host = default_host

    while True:
        port_str = input("Digite a porta do servidor (ex: 12345): ").strip() or '12345'

        try:
            if port_str:
                port = int(port_str)
            else:
                port = default_port

            if port <= 1024:
                print("Portas abaixo de 1024 são reservadas. Escolha outra, porta padrão 12345.")
                continue
            break
            
        except ValueError:
            print("Porta inválida. A porta deve ser um número inteiro.")  
    return host, port

def handle_server_response(client_socket):
    try:
        #timeout para evitar que a thread bloqueie indefinidamente
        client_socket.settimeout(3.0)
        data = client_socket.recv(BUFFER_SIZE)

        if data:
            resposta = data.decode('utf-8')
            print(f"📨 Resposta do Servidor: '{resposta}'")
        else:
            # Se recv() retornar vazio (0 bytes), o servidor fechou a conexão.            
            print("Servidor fechou a conexão")
            return False
    except socket.timeout:
        # Em algumas situações, o servidor pode não responder imediatamente (ex: CHAT sem eco)
        pass 
    except Exception as e:
        print(f"Erro ao receber resposta: {e}")
        return False   

    return True

def start_client():
    """
    Função principal para iniciar o cliente.
    """

    HOST, PORTA = get_server_info()
    
    # Cria o socket do cliente (TCP)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            # 1. Conecta ao servidor
            print(f"\n ---------------------------------------\n")
            print(f"Tentando conectar em {HOST}:{PORTA}...")
            client_socket.connect((HOST, PORTA))
            print("✔️  Conectado ao servidor!")

            mensagem_inicial = "CLIENTE_ONLINE" 
            client_socket.sendall(mensagem_inicial.encode('utf-8'))
            print(f"📤 Enviado: '{mensagem_inicial}'")
            
            while True:
                #Interface do Usuário: Recebe o comando do console
                command = input(f"\n[CLIENTE] Digite o comando (ex:Ola, ARQUIVO nome.txt, SAIR)").strip()

                if not command:
                    continue

                #Parsing e Roteamento de Comando
                parts = command.split(maxsplit=1)
                cmd = parts[0].upper()

                #Enviar "Sair"
                if cmd == EXIT_COMMAND:
                    print(f"📤 Enviando comando '{EXIT_COMMAND}' e encerrando.")
                    # Envia o comando para notificar o servidor
                    client_socket.sendall(command.encode('utf-8'))
                    break

                #Enviar "Arquivo [Nome]" ou "Chat [Mensagem]"
                elif cmd in ["ARQUIVO", "CHAT"]:
                    client_socket.sendall(command.encode('utf-8'))
                    print(f"📤 Comando enviado: '{command}'")

                    if not handle_server_response(client_socket):
                        break
                else:
                    print("Comando desconhecido. Use ARQUIVO, CHAT ou SAIR")

    except socket.error as e:
        print(f"❌  Erro de socket: {e}")
        print("Verifique se o servidor (servidor.py) está rodando.")
    except Exception as e:
        print(f"❌  Erro inesperado: {e}")

    print("🔌  Conexão fechada.")
    print(f"\n ---------------------------------------")

if __name__ == "__main__":
    start_client()