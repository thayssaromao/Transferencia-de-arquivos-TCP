# 📄 Protocolo de Comunicação - Chat e Transferência de Arquivos
Desenvolvido por: Thayssa Daniele Pacheco Romão e Matheus Araújo Akiyoshi Loureiro

Este documento define as especificações do protocolo de camada de aplicação utilizado para a comunicação entre Cliente e Servidor via sockets TCP. O sistema suporta troca de mensagens (Chat), listagem e download de arquivos com verificação de integridade (SHA-256).

## 1. Visão Geral da Conexão
Transporte: TCP/IP.

- Codificação de Texto: UTF-8.

- Buffer Padrão: 1024 bytes (Servidor) / 4096 bytes (Cliente).

- Handshake: Ao conectar, o cliente envia imediatamente a string: `CLIENTE_ONLINE`.

## 2. Formato das Requisições (Cliente → Servidor)
Os comandos são enviados em texto plano. O delimitador entre o comando e o argumento é o caractere de espaço.


| Comando       | Argumento   | Exemplo | Descrição |
| ------------- | ------------- |------------- |------------- 
| CHAT          | `<mensagem>`  |  CHAT Olá    |Envia uma mensagem para o servidor/chat |
| ARQUIVO | `<nome_arquivo>`  | ARQUIVO foto.png|  Solicita o download de um arquivo específico. |
| SAIR | Nenhum  | SAIR|  Solicita o encerramento da conexão. |


# 3. Formato das Respostas (Servidor → Cliente)
O servidor responde com strings prefixadas para identificar o tipo de dado.

Resposta ao cliente quando ele envia uma mensagem:
```bash
  OK_CHAT Recebido: <mensagem_original>
```

Mensagem enviada pelo servidor para todos os clientes(Broadcast):
```bash
 CHAT_SERVER: <mensagem>`
```
Quando o arquivo NÃO existe:
```bash
 ERRO_ARQUIVO_INEXISTENTE <nome_solicitado>
```
Quando o arquivo EXISTE:
```bash
TAMANHO <bytes> SHA256 <hash>
```

# 4. Transferência do Arquivo
- O cliente lê o arquivo em chunks de até 4096 bytes.
- Essa segmentação ocorre somente no cliente, pois o servidor envia o arquivo inteiro

# 5. Verificação de Integridade (SHA-256)
O dono do arquivo (servidor) calcula o SHA-256 usando:
```bash
sha256.update(chunk)
```
O cliente repete o cálculo ao receber o arquivo.
`Se HASH_LOCAL` == `HASH_SERVIDOR`, o download é considerado íntegro.
