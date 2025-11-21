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

            # 2. Envia a mensagem "Hello"
            mensagem = "Olá Servidor (Hello World!)"
            client_socket.sendall(mensagem.encode('utf-8'))
            print(f"📤  Enviado: '{mensagem}'")

            # 3. Recebe a resposta "World"
            data = client_socket.recv(1024)
            resposta = data.decode('utf-8')
            
            print(f"📨  Resposta do Servidor: '{resposta}'")

    except socket.error as e:
        print(f"❌  Erro de socket: {e}")
        print("Verifique se o servidor (servidor.py) está rodando.")
    except Exception as e:
        print(f"❌  Erro inesperado: {e}")

    print("🔌  Conexão fechada.")
    print(f"\n ---------------------------------------")

if __name__ == "__main__":
    start_client()