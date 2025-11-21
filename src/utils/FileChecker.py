import os

# Diretório onde os arquivos de teste estão localizados
FILE_STORAGE_DIR = "../files"

def file_exists(filename):
    return os.path.exists(filename)

def file_size_mb(filename):
    if not file_exists(filename):
        return 0
    return os.path.getsize(filename) / (1024 * 1024)

def send_file_not_found(conn, filename):
    """Envia um status de erro ao cliente."""
    # Simulação de conexão para teste local
    error_message = f"0 {filename} Arquivo não encontrado."
    if hasattr(conn, 'sendall'):
        conn.sendall(error_message.encode('utf-8'))
    print(f"❌ [CLIENTE SIMULADO] Erro: Arquivo '{filename}' não encontrado.")

def list_directories(FILE_STORAGE_DIR):
    files_list = []
    if os.path.exists(FILE_STORAGE_DIR):
        # Filtra apenas arquivos (ignora subpastas)
        files_list = [f for f in os.listdir(FILE_STORAGE_DIR) if os.path.isfile(os.path.join(FILE_STORAGE_DIR, f))]
    for index, filename in enumerate(files_list):
        print(f"[{index + 1}] {filename}")

# print(f"\n=== Listando Arquivos disponíveis em '{FILE_STORAGE_DIR}' ===")
# list_directories(FILE_STORAGE_DIR)