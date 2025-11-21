import socket
import threading
import hashlib #necessario pa calcular o SHA-256
import os # Necessário para checar a existência e tamanho do arquivo

# Configurações do Servidor
HOST = '127.0.0.1' 
PORTA = 12345       # Porta TCP para escutar (acima de 1024)
BUFFER_SIZE = 1024 # Tamanho padrão de buffer

# Diretório onde os arquivos de teste estão localizados
FILE_STORAGE_DIR = "server_files"

def calcula_sha256(filepath):
    """Calcula o hash SHA256 de um aquivo em chuncks."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096),b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def send_file_not_found(conn, filename):
    """Envia um status de erro ao cliente."""
    # Protocolo: STATUS_ERROR(0) Nome_do_Arquivo
    error_message = f"0 {filename} Arquivo não encontrado."
    conn.sendall(error_message.encode('utf-8'))
    print(f"❌ [CLIENTE {conn.getpeername()}] Erro: Arquivo '{filename}' não encontrado.")

def handle_client(conn, addr):
    """
    Função executada por cada thread para lidar com um cliente individual.
    """
    print(f"✔️  [NOVA CONEXÃO] {addr} conectado.")

    try:
        # Loop para lidar com o cliente
        while True:
            # 1. Recebe dados do cliente
            # recv(1024) lê até 1024 bytes
            data = conn.recv(1024)
            
            # Se recv() retornar 0 bytes, o cliente fechou a conexão
            if not data:
                print(f"🔌  [CLIENTE {addr}] Desconectou.")
                break

            mensagem_cliente = data.decode('utf-8')
            print(f"🖥️  [CLIENTE {addr}] Recebeu: '{mensagem_cliente}'")

            # 2. Envia a resposta "Hello World" (ou um eco)
            # Para este "Hello World", vamos apenas ecoar a mensagem de volta
            # com um prefixo.
            resposta = f"Servidor diz: Olá, {addr}! Você enviou: '{mensagem_cliente}'"
            
            # sendall() garante que todos os dados sejam enviados
            conn.sendall(resposta.encode('utf-8'))
            print(f"📤  [CLIENTE {addr}] Enviou: '{resposta}'")

    except socket.error as e:
        # Trata erros de conexão (ex: cliente fecha abruptamente)
        print(f"❌  [ERRO CLIENTE {addr}] {e}")
    finally:
        # 3. Fecha a conexão com este cliente
        print(f"🔒  [CLIENTE {addr}] Fechando conexão.")
        conn.close()

def start_server():
    """
    Função principal para iniciar o servidor.
    """
    # Cria o socket do servidor
    # socket.AF_INET: Usando IPv4
    # socket.SOCK_STREAM: Usando TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Define uma opção para reutilizar o endereço/porta (útil para testes rápidos)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Vincula (bind) o socket ao HOST e PORTA
        server_socket.bind((HOST, PORTA))

        # Coloca o socket em modo de escuta (listen)
        server_socket.listen()
        print(f"\n ---------------------------------------\n")
        print(f"🚀  Servidor TCP Multithread ouvindo em {HOST}:{PORTA}...\n")

        while True:
            # Aguarda (bloqueia) por uma nova conexão
            # accept() retorna um novo socket (conn) para comunicação 
            # com o cliente e o endereço (addr) do cliente.
            conn, addr = server_socket.accept()

            # Cria e inicia uma nova thread para lidar com o cliente
            # A thread principal (esta) volta imediatamente para o accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            
            # Mostra quantas threads (clientes) estão ativas
            # (-1 para não contar a thread principal)
            print(f"Ativas: {threading.active_count() - 1} conexões de clientes.")

    except KeyboardInterrupt:
        print("\n🛑  Servidor sendo desligado...")
    except Exception as e:
        print(f"❌  Erro ao iniciar o servidor: {e}")
    finally:
        # Fecha o socket principal do servidor
        server_socket.close()
        print("Servidor desligado.")

if __name__ == "__main__":
    start_server()