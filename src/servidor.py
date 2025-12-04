# servidor.py
#Thayssa Daniele Pacheco Romão e Matheus Araújo Akiyoshi Loureiro
import socket
import threading
import os
import time
from utils.functions import calcula_sha256

# Configurações do Servidor
HOST = '127.0.0.1' 
PORTA = 12345       # Porta TCP para escutar (acima de 1024)
BUFFER_SIZE = 1024 # Tamanho padrão de buffer

SERVER_FILES_DIR = "files"

# Lista global para armazenar conexões ativas
clientes_conectados = []
clientes_lock = threading.Lock()  # Para sincronizar acesso à lista

def handle_client(conn, addr):
    print(f"✔️  [NOVA CONEXÃO WEB] {addr} conectado.")

    try:
        # Recebe a requisição do navegador
        request = conn.recv(BUFFER_SIZE).decode('utf-8')
        
        if not request:
            return

        # Pega a primeira linha da requisição (Ex: "GET /index.html HTTP/1.1")
        #
        linhas = request.split('\r\n')
        primeira_linha = linhas[0].split()

        if len(primeira_linha) < 2:
            return 
        
        metodo = primeira_linha[0]   # Ex: GET
        arquivo_solicitado = primeira_linha[1] # Ex: /index.html

        # Se o navegador pedir apenas "/", vamos entregar um "index.html" padrão
        if arquivo_solicitado == "/":
            arquivo_solicitado = "/index.html"

        # Remove a barra inicial para achar o arquivo na pasta (Ex: "files/index.html")
        caminho_arquivo = os.path.join(SERVER_FILES_DIR, arquivo_solicitado.lstrip('/'))

        # Lógica de Resposta
        if os.path.exists(caminho_arquivo) and os.path.isfile(caminho_arquivo):
            # 1. Definir o Tipo de Conteúdo (MIME Type)
            content_type = "application/octet-stream" # Padrão
            if caminho_arquivo.endswith(".html") or caminho_arquivo.endswith(".htm"):
                content_type = "text/html"
            elif caminho_arquivo.endswith(".jpg") or caminho_arquivo.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif caminho_arquivo.endswith(".png"):
                content_type = "image/png"

            # 2. Ler o arquivo em binário
            with open(caminho_arquivo, "rb") as f:
                conteudo = f.read()

            # 3. Montar o Cabeçalho HTTP 200 OK
            header = "HTTP/1.1 200 OK\r\n"
            header += f"Content-Type: {content_type}\r\n"
            header += f"Content-Length: {len(conteudo)}\r\n"
            header += "Connection: close\r\n\r\n" # Avisa que vai fechar após enviar

            # 4. Enviar Cabeçalho + Conteúdo
            conn.sendall(header.encode('utf-8') + conteudo)
            print(f"📤 Enviado: {arquivo_solicitado} - 200 OK")

        else:
            # Tratamento de Erro 404 (Arquivo não encontrado)
            corpo_erro = "<h1>404 - Arquivo Nao Encontrado</h1><p>O arquivo solicitado nao existe no servidor.</p>"
            
            header = "HTTP/1.1 404 Not Found\r\n"
            header += "Content-Type: text/html\r\n"
            header += f"Content-Length: {len(corpo_erro)}\r\n"
            header += "Connection: close\r\n\r\n"

            conn.sendall(header.encode('utf-8') + corpo_erro.encode('utf-8'))
            print(f"⚠️  Erro 404: {arquivo_solicitado} não encontrado.")

    except Exception as e:
        print(f"[ERRO] Cliente {addr}: {e}")
    finally:
        conn.close() # No HTTP 1.0/Simplificado, fechamos a conexão após a resposta

# Ao rodar o servidor, abra uma pagina no navegador http://127.0.0.1:12345/index.html
#teste de erro com http://127.0.0.1:12345/abacate.html

# VERSAO ANTIGA TCP

# def handle_client(conn, addr):
#     print(f"✔️  [NOVA CONEXÃO] {addr} conectado.")

#     with clientes_lock:
#         clientes_conectados.append(conn)
#         print(f"Ativas: {len(clientes_conectados)} clientes.")
#     try:
#         while True:
#             data = conn.recv(BUFFER_SIZE)
#             if not data:
#                 print(f"🔌  [CLIENTE {addr}] Desconectou.")
#                 break

#             mensagem = data.decode('utf-8', errors='ignore')

#             if mensagem.strip().upper() == "SAIR":
#                 print(f"🔌  [CLIENTE {addr}] Enviou comando SAIR. Encerrando conexão.")
#                 break

#             # ENVIAR ARQUIVO SOLICITADO
#             if mensagem.startswith("ARQUIVO "):
#                 partes = mensagem.split(" ", 1)
#                 nome_arquivo = partes[1]

#                 caminho = os.path.join(SERVER_FILES_DIR, nome_arquivo)

#                 if not os.path.exists(caminho):
#                     erro = f"ERRO_ARQUIVO_INEXISTENTE {nome_arquivo}"
#                     print(erro)
#                     conn.sendall(erro.encode('utf-8'))
#                     continue

#                 # Lê arquivo
#                 with open(caminho, "rb") as f:
#                     conteudo = f.read()

#                 tamanho = len(conteudo)
#                 hash_sha256 = calcula_sha256(caminho)

#                 #Envia cabeçalho com tamanho e hash
#                 cabecalho = f"TAMANHO {tamanho} SHA256 {hash_sha256}"
#                 conn.sendall((cabecalho + "\n").encode('utf-8'))
#                 time.sleep(0.05)  # força separação entre pacotes
#                 conn.sendall(conteudo)

#                 print(f"📤 Arquivo '{nome_arquivo}' enviado ({tamanho} bytes).")
#                 continue    

#             # CHAT / mensagens normais
#             print(f"[MENSAGEM] {addr}: {mensagem}")

#             resposta = f"OK_CHAT Recebido: {mensagem}"
#             conn.sendall(resposta.encode('utf-8'))

#     except Exception as e:
#         print(f"[ERRO] Cliente {addr}: {e}")
#     finally:
#         # Remove cliente da lista quando desconectar
#         with clientes_lock:
#             if conn in clientes_conectados:
#                 clientes_conectados.remove(conn)
#             print(f"[CLIENTE {addr}] Conexão encerrada.")
#             print(f"Ativas: {len(clientes_conectados)} clientes.")
#         conn.close()


def broadcast_chat(mensagem):
    with clientes_lock:
        for cliente in clientes_conectados:
            try:
                cliente.sendall(f"CHAT_SERVER: {mensagem}".encode('utf-8'))
            except:
                pass  # Ignora erros de clientes desconectados

def server_chat_console():
    print("Servidor pronto para enviar mensagens!")
    print("Servidor: ", end="", flush=True)

    while True:
        msg = input()
        if msg.strip():  # Evita enviar mensagens vazias
            broadcast_chat(msg)


def start_server():
    """
    Função principal para iniciar o servidor.
    """
    # socket.AF_INET: Usando IPv4
    # socket.SOCK_STREAM: Usando TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Define uma opção para reutilizar o endereço/porta 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Vincula (bind) o socket ao HOST e PORTA
        server_socket.bind((HOST, PORTA))

        # Coloca o socket em modo de escuta (listen)
        server_socket.listen()
        print(f"\n ---------------------------------------\n")
        print(f"🚀  Servidor TCP Multithread ouvindo em {HOST}:{PORTA}...\n")

        chat_thread = threading.Thread(target=server_chat_console)
        chat_thread.daemon = True
        chat_thread.start()

        while True:

            conn, addr = server_socket.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServidor sendo desligado...")
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
    finally:
  
        server_socket.close()
        print("Servidor desligado.")

if __name__ == "__main__":
    start_server()