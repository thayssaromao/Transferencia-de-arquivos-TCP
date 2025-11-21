import hashlib #necessario pa calcular o SHA-256
import os # Necessário para checar a existência e tamanho do arquivo

def calcula_sha256(filepath):
    """Calcula o hash SHA256 de um aquivo em chuncks."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096),b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

