# cliente.py
#Thayssa Daniele Pacheco Romão e Matheus Araújo Akiyoshi Loureiro
import socket
import threading 
from utils import FileChecker
from utils.functions import calcula_sha256
import os
import time

BUFFER_SIZE = 4096
EXIT_COMMAND = "SAIR"

# variáveis globais
arquivo_em_download = None
arquivo_lock = threading.Lock()

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

def recv_handler(client_socket):
    """
    Lida com o recebimento de mensagens do servidor.
    """
    global arquivo_em_download


    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                print("\n[DESCONEXÃO] Servidor fechou a conexão. Encerrando escuta.")            
                break
            try:
                resposta = data.decode('utf-8') 
            except UnicodeDecodeError:
                resposta = ""  # evita que o resto quebre

            if resposta.startswith("CHAT_SERVER:"):
                print(f"\n[CHAT RECEBIDO] {resposta[13:].strip()}")
            
            elif resposta.startswith("OK_CHAT"):
                print(f"\nConfirmação do Servidor: {resposta}")

            elif resposta.startswith("ERRO_ARQUIVO_INEXISTENTE"):
                print(f"\nArquivo não encontrado no servidor: {resposta.split()[1]}")
                # Limpa a variável caso estivesse tentando baixar
                arquivo_em_download = None
                continue

            elif resposta.startswith("TAMANHO"):
                if not arquivo_em_download:
                    print("Erro: nenhum arquivo foi solicitado!")
                    continue  

                partes = resposta.split()
                tamanho = int(partes[1])
                hash_servidor = partes[3]

                print(f"\nTamanho: {tamanho} bytes")
                print(f"Hash servidor: {hash_servidor}")
                print(f"Baixando: {arquivo_em_download}")

                # Prepara diretório
                dir_path = os.path.join(os.getcwd(), "recebidos")
                os.makedirs(dir_path, exist_ok=True)
                caminho_final = os.path.join(dir_path, arquivo_em_download)

                with open(caminho_final, "wb") as f:
                    recebido = 0
                    while recebido < tamanho:
                        chunk = client_socket.recv(min(BUFFER_SIZE, tamanho - recebido))
                        if not chunk:
                            raise Exception("Conexão interrompida durante o download")
                        f.write(chunk)
                        recebido += len(chunk)

                    print(f"Download concluído: {caminho_final}")
                
                
                print(f"✔ Arquivo salvo em: {caminho_final}")

                # --- VERIFICAÇÃO DE HASH ---
                hash_local = calcula_sha256(caminho_final)
                if hash_local == hash_servidor:
                    print("Arquivo recebido com sucesso! Hash conferido.")
                else:
                    print("Falha na integridade do arquivo! Hash não confere.")

                # Limpa variável
                arquivo_em_download = None
                continue

            else:
                print(f"\n[SERVIDOR] ")

        except socket.timeout:
            continue 
        except Exception as e:
            print(f"\n[ERRO] Falha na thread de recepção: {e}")
            break


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
            
            #Criação e Início da Thread de Escuta
            client_socket.settimeout(None)
            listener_thread = threading.Thread(target=recv_handler,args=(client_socket,))
            listener_thread.daemon = True
            listener_thread.start()

            while True:
                # --- MENU INTERATIVO --- #
                print("\n" + "="*30)
                print("       MENU DO CLIENTE")
                print("="*30)
                print("1. 💬 Enviar Mensagem (CHAT)")
                print("2. 📂 Arquivo (ARQUIVO)")
                print("3. ❌ Sair (SAIR)")
                print("="*30)
                
                opcao = input("Escolha uma opção (1-3): \n").strip()
                #Interface do Usuário: Recebe o comando do console

                if opcao == "1":
                    mensagem = input("Digite sua mensagem: ").strip()
                    if mensagem:
                        # Monta o protocolo: CHAT <mensagem>
                        comando_final = f"CHAT {mensagem}"
                        client_socket.sendall(comando_final.encode('utf-8'))
                    else:
                        print("⚠️  Mensagem vazia não enviada.")

                # Lógica da Opção 2: ARQUIVO
                elif opcao == "2":  
                    nome_do_arquivo = input("Digite o nome do arquivo que deseja baixar: ").strip()

                    if not nome_do_arquivo:
                        print("Nome inválido.")
                        continue

                    global arquivo_em_download
                    
                    with arquivo_lock:
                        arquivo_em_download = nome_do_arquivo

                    comando = f"ARQUIVO {nome_do_arquivo}"
                    client_socket.sendall(comando.encode('utf-8'))
                    print(f"📤 Solicitado: {comando}")

                elif opcao == "3":
                    print(f"📤 Enviando comando '{EXIT_COMMAND}' e encerrando...")
                    client_socket.sendall(EXIT_COMMAND.encode('utf-8'))
                    break
                
                # Tratamento de erro para opção inválida
                else:
                    print("Opção inválida. Por favor, digite 1, 2 ou 3.")

    except socket.error as e:
        print(f"\nErro de socket: {e}")
        print("Verifique se o servidor (servidor.py) está rodando.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")

    print("Conexão fechada.")
    print(f"---------------------------------------")

if __name__ == "__main__":
    start_client()