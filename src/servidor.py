# servidor.py
import socket
import threading
import os
from utils.functions import calcula_sha256

# Configurações do Servidor
HOST = '127.0.0.1' 
PORTA = 12345       # Porta TCP para escutar (acima de 1024)
BUFFER_SIZE = 1024 # Tamanho padrão de buffer

SERVER_FILES_DIR = "files"

def handle_client(conn, addr):
    print(f"✔️  [NOVA CONEXÃO] {addr} conectado.")

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print(f"🔌  [CLIENTE {addr}] Desconectou.")
                break

            mensagem = data.decode('utf-8', errors='ignore')

             # -------------------------------------------------------
            # 📁 LISTAR ARQUIVOS
            # -------------------------------------------------------
            if mensagem == "LISTAR_ARQUIVOS":
                try:
                    arquivos = os.listdir(SERVER_FILES_DIR)
                    # Apenas arquivos, ignorar pastas
                    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(SERVER_FILES_DIR, f))]
                    resposta = ";".join(arquivos) if arquivos else "VAZIO"
                except:
                    resposta = "ERRO_LISTAR"

                conn.sendall(resposta.encode('utf-8'))
                continue

            # -------------------------------------------------------
            # 📄 ENVIAR ARQUIVO SOLICITADO
            # -------------------------------------------------------
            if mensagem.startswith("ARQUIVO "):
                partes = mensagem.split(" ", 1)
                nome_arquivo = partes[1]

                caminho = os.path.join(SERVER_FILES_DIR, nome_arquivo)

                # Verifica se arquivo existe
                if not os.path.exists(caminho):
                    erro = f"ERRO_ARQUIVO_INEXISTENTE {nome_arquivo}"
                    conn.sendall(erro.encode('utf-8'))
                    continue

                # Lê arquivo
                with open(caminho, "rb") as f:
                    conteudo = f.read()

                tamanho = len(conteudo)
                hash_sha256 = calcula_sha256(caminho)

                # 1️⃣ Envia cabeçalho com tamanho e hash
                cabecalho = f"TAMANHO {tamanho} SHA256 {hash_sha256}"
                conn.sendall(cabecalho.encode('utf-8'))

                # 2️⃣ Envia bytes do arquivo
                conn.sendall(conteudo)

                print(f"📤 Arquivo '{nome_arquivo}' enviado ({tamanho} bytes).")
                continue    

            # CHAT / mensagens normais
            print(f"💬 [MENSAGEM] {addr}: {mensagem}")

            resposta = f"OK_CHAT Recebido: {mensagem}"
            conn.sendall(resposta.encode('utf-8'))

    except Exception as e:
        print(f"❌ [ERRO] Cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"🔒 [CLIENTE {addr}] Conexão encerrada.")

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