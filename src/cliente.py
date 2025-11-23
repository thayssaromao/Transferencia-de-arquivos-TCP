# cliente.py
import socket
import threading # Novo
from utils import FileChecker
import os
import time


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

def recv_handler(client_socket):
    """
    Lida com o recebimento de mensagens do servidor.
    """
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                print("\n[DESCONEXÃO] Servidor fechou a conexão. Encerrando escuta.")            
                break
            
            resposta = data.decode('utf-8')

            if resposta.startswith("CHAT_SERVER:"):
                # Move o cursor para uma nova linha para não interromper o input do usuário
                print(f"\n💬 [CHAT RECEBIDO] {resposta[13:].strip()}")
                print(f"[CLIENTE] Digite o comando (ex: CHAT Ola, ARQUIVO nome.txt, SAIR): ", end="", flush=True)    

            elif resposta.startswith("OK_CHAT"):
                print(f"Confirmação do Servidor: {resposta}")

            else:
                print(f"\n[SERVIDOR] {resposta}")

            print("\n(Pressione Enter para ver o menu ou digite sua opção...): ", end="", flush=True)
        
        except socket.timeout:
            continue 
        except Exception as e:
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
                print("2. 📂 Enviar Arquivo (ARQUIVO)")
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
                    dir_path = FileChecker.FILE_STORAGE_DIR
                    
                    if not os.path.exists(dir_path):
                        print(f"❌ Diretório '{dir_path}' não existe. Criando...")
                        os.makedirs(dir_path, exist_ok=True)

                    # 1. Obter lista real de arquivos (para poder indexar)
                    lista_arquivos = []
                    try:
                        lista_arquivos = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                    except Exception as e:
                        print(f"Erro ao ler diretório: {e}")
                        continue

                    if not lista_arquivos:
                        print(f"⚠️  Nenhum arquivo encontrado na pasta '{dir_path}'. Adicione arquivos lá para testar.")
                        continue

                    # 2. Exibir lista numerada
                    print(f"\n--- Arquivos disponíveis em '{dir_path}' ---")
                    for i, arquivo in enumerate(lista_arquivos):
                        print(f"[{i + 1}] {arquivo}")
                    
                    # 3. Escolher arquivo pelo número
                    escolha = input("\nDigite o NÚMERO do arquivo para enviar: ").strip()

                    try:
                        indice = int(escolha) - 1 # Ajusta pois lista começa em 0 e menu em 1
                        
                        if 0 <= indice < len(lista_arquivos):
                            nome_arquivo = lista_arquivos[indice] # Pega o nome baseado no número
                            caminho_completo = os.path.join(dir_path, nome_arquivo)
                            tamanho_arquivo = os.path.getsize(caminho_completo)

                            print(f"Preparando para enviar '{nome_arquivo}' ({tamanho_arquivo} bytes)...")
                            
                            # Envia Cabeçalho
                            cabecalho = f"ARQUIVO {nome_arquivo} {tamanho_arquivo}"
                            client_socket.sendall(cabecalho.encode('utf-8'))
                            
                            time.sleep(0.1) # Pausa técnica

                            # Envia Conteúdo Binário
                            try:
                                with open(caminho_completo, "rb") as f:
                                    bytes_enviados = 0
                                    while True:
                                        bytes_read = f.read(BUFFER_SIZE)
                                        if not bytes_read:
                                            break
                                        client_socket.sendall(bytes_read)
                                        bytes_enviados += len(bytes_read)
                                        #print(f"\rEnviando: {bytes_enviados}/{tamanho_arquivo} bytes...", end="")
                                
                                print(f"\n📤 Arquivo '{nome_arquivo}' enviado com sucesso!")
                            
                            except Exception as e:
                                print(f"\n❌ Erro ao ler/enviar arquivo: {e}")

                        else:
                            print("❌ Número inválido. Escolha um número da lista.")
                    
                    except ValueError:
                        print("❌ Entrada inválida. Digite apenas o número.")
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