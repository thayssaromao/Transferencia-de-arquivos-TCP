# cliente.py
import socket
import threading # Novo
from utils import FileChecker
import os
import time

BUFFER_SIZE = 4096
EXIT_COMMAND = "SAIR"

# variáveis globais
lista_arquivos_servidor = []
arquivo_solicitado = ""
arquivo_lock = threading.Lock()  # sincroniza acesso a arquivo_solicitado


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
    global lista_arquivos_servidor
    global arquivo_solicitado

    while True:
        try:
            
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                print("\n[DESCONEXÃO] Servidor fechou a conexão. Encerrando escuta.")            
                break
                       
            resposta = data.decode('utf-8') 

            if resposta.startswith("CHAT_SERVER:"):
                print(f"\n[CHAT RECEBIDO] {resposta[13:].strip()}")
            
            elif resposta.startswith("OK_CHAT"):
                print(f"\nConfirmação do Servidor: {resposta}")
            
            elif ";" in resposta or resposta == "VAZIO":
                lista_arquivos_servidor.clear()

                if resposta == "VAZIO":
                    lista_arquivos_servidor.append("VAZIO")
                else:
                    arquivos = [a.strip() for a in resposta.split(";") if a.strip()]
                    lista_arquivos_servidor.extend(arquivos)
                continue

            elif resposta.startswith("TAMANHO "):
                with arquivo_lock:
                    if not arquivo_solicitado:
                        # Se não houver arquivo definido, espera um pouco
                        time.sleep(0.1)
                        if not arquivo_solicitado:
                            print("❌ Erro: nenhum arquivo foi solicitado. Ignorando pacote.")
                            continue
                    nome_do_arquivo = arquivo_solicitado  # captura a variável dentro do lock
                try:
                
                    partes = resposta.split()
                    tamanho = int(partes[1])
                    hash_servidor = partes[3]

                    print(f"\n📥 Tamanho recebido: {tamanho} bytes")
                    print(f"🔐 Hash SHA-256: {hash_servidor}")

                    # SALVAR EM PASTA 'recebidos' DENTRO DO PROJETO
                    dir_path = os.path.join(os.getcwd(), "recebidos")
                    os.makedirs(dir_path, exist_ok=True)
                    caminho_final = os.path.join(dir_path, nome_do_arquivo)

                    with open(caminho_final, "wb") as f:
                        recebido = 0
                        while recebido < tamanho:
                            bytes_restantes = min(BUFFER_SIZE, tamanho - recebido)
                            chunk = client_socket.recv(bytes_restantes)
                            if not chunk:
                                raise Exception("Conexão interrompida durante o download")
                            f.write(chunk)
                            recebido += len(chunk)


                    print(f"✅ Download concluído: {caminho_final}")
                except Exception as e:
                    print(f"❌ Erro ao salvar arquivo: {e}")
                finally:
                    with arquivo_lock:
                        arquivo_solicitado = ""
                continue 
            else:
                #print(f"\n[SERVIDOR] {resposta}")
                print(f"\n[SERVIDOR]")

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
                # --- MENU INTERATIVO ---
                print("\n" + "="*30)
                print("       MENU DO CLIENTE")
                print("="*30)
                print("1. 💬 Enviar Mensagem (CHAT)")
                print("2. 📂 Baixar Arquivo (ARQUIVO)")
                print("3. ❌ Sair (SAIR)")
                print("="*30)
                
                opcao = input("Escolha uma opção (1-3): \n").strip()
                #Interface do Usuário: Recebe o comando do console
                #command = input(f"\n[CLIENTE] Digite o comando (ex:Ola, ARQUIVO nome.txt, SAIR)").strip()

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
                    print("\n📂 Solicitando lista de arquivos...")

                    lista_arquivos_servidor.clear()
                    client_socket.sendall("LISTAR_ARQUIVOS".encode('utf-8'))

                    # espera thread preencher a lista
                    while not lista_arquivos_servidor:
                        time.sleep(0.1)

                    arquivos = lista_arquivos_servidor.copy()
                    lista_arquivos_servidor.clear()

                    if arquivos[0] == "VAZIO":
                        print("❌ Servidor não possui arquivos.")
                        continue

                    print("\n--- Arquivos disponíveis ---")
                    for i, nome in enumerate(arquivos):
                        print(f"[{i+1}] {nome}")

                    escolha = input("\nEscolha o número do arquivo: ").strip()

                    try:
                        indice = int(escolha) - 1
                        if 0 <= indice < len(arquivos):
                            with arquivo_lock:
                                arquivo_solicitado = arquivos[indice]
                            comando = f"ARQUIVO {arquivo_solicitado}"
                            client_socket.sendall(comando.encode('utf-8'))
                            print(f"📤 Solicitado: {arquivo_solicitado}")
                        else:
                            print("Número inválido.")
                    except ValueError:
                        print("Entrada inválida, digite apenas números.")


                elif opcao == "3":
                    print(f"📤 Enviando comando '{EXIT_COMMAND}' e encerrando...")
                    client_socket.sendall(EXIT_COMMAND.encode('utf-8'))
                    break
                
                # Tratamento de erro para opção inválida
                else:
                    print("⚠️  Opção inválida. Por favor, digite 1, 2 ou 3.")

    except socket.error as e:
        print(f"\n❌  Erro de socket: {e}")
        print("Verifique se o servidor (servidor.py) está rodando.")
    except Exception as e:
        print(f"\n❌  Erro inesperado: {e}")

    print("🔌  Conexão fechada.")
    print(f"---------------------------------------")

if __name__ == "__main__":
    start_client()