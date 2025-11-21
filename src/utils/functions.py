import hashlib #necessario pa calcular o SHA-256
import os # Necessário para checar a existência e tamanho do arquivo

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
