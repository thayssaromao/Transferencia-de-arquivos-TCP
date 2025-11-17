import socket

# Configurações do Cliente
HOST = '127.0.0.1'  # IP do Servidor (mesmo do servidor)
PORTA = 12345       # Porta do Servidor (mesma do servidor)

def start_client():
    """
    Função principal para iniciar o cliente.
    """
    # Cria o socket do cliente (TCP)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            # 1. Conecta ao servidor
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

if __name__ == "__main__":
    start_client()