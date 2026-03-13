
# Sistema Distribuído com Registro de Nós e Heartbeat

## Descrição

Este projeto implementa um sistema distribuído simples utilizando **Python 3** e **comunicação via sockets TCP**.

O sistema é composto por:

- **Servidor (`server.py`)**: responsável por registrar nós, receber heartbeats e manter a lista de nós ativos.
- **Clientes (`client.py`)**: representam nós do sistema distribuído que se registram no servidor, enviam heartbeats periódicos e consultam a lista de nós ativos.

O objetivo do sistema é simular um mecanismo simples de **descoberta de nós e monitoramento de disponibilidade**, comum em sistemas distribuídos.

---

# Arquitetura do Sistema

O sistema segue uma arquitetura **cliente-servidor**.

```
            +----------------------+
            |       Servidor       |
            |      server.py       |
            |----------------------|
            | Registro de nós      |
            | Controle de heartbeat|
            | Lista de nós ativos  |
            +----------+-----------+
                       |
      ------------------------------------------
      |                  |                     |
+-----------+      +-----------+        +-----------+
|  Cliente  |      |  Cliente  |        |  Cliente  |
| client.py |      | client.py |        | client.py |
|  node1    |      |  node2    |        |  node3    |
+-----------+      +-----------+        +-----------+
```

Cada cliente representa um **nó do sistema distribuído**.

---

# Funcionamento

## Registro de nós

Quando um cliente se conecta ao servidor, ele envia:

REGISTER:<node_id>

O servidor registra o nó e armazena o horário do último heartbeat.

Resposta do servidor:

OK:REGISTERED

---

## Heartbeat

Os clientes enviam periodicamente mensagens de heartbeat para indicar que continuam ativos.

Mensagem enviada:

HEARTBEAT:<node_id>

Resposta do servidor:

OK:HEARTBEAT

O servidor atualiza o timestamp do último heartbeat recebido.

---

## Listagem de nós ativos

Um cliente pode solicitar a lista de nós ativos enviando:

LIST

Resposta:

NODES:node1,node2,node3

Um nó é considerado **ativo** se tiver enviado heartbeat nos últimos **10 segundos**.

Nós inativos **não aparecem na lista**.

---

## Desconexão

Quando o cliente deseja encerrar sua participação no sistema, envia:

QUIT:<node_id>

Resposta:

OK:BYE

O servidor remove o nó da lista de registrados.

---

# Estrutura do Projeto

```
projeto/
│
├── server.py
├── client.py
└── README.md
```

---

# Requisitos

- Python 3
- Apenas bibliotecas padrão do Python

Bibliotecas utilizadas:

- socket
- threading
- time
- sys

---

# Como Executar

## 1. Iniciar o servidor

Execute o servidor em um terminal:

```
python server.py
```

Saída esperada:

```
[STARTED] Servidor escutando em 0.0.0.0:5000
```

---

## 2. Executar clientes

Em novos terminais, execute os clientes com identificadores diferentes.

Exemplo:

```
python client.py node1
```

```
python client.py node2
```

```
python client.py node3
```

---

# Testando a Expiração de Nós

O sistema considera um nó ativo se ele enviar heartbeat nos últimos **10 segundos**.

Para demonstrar a expiração:

1. Inicie o servidor
2. Execute um ou mais clientes
3. **Pare um cliente antes dele enviar o comando `QUIT`** (por exemplo usando `CTRL + C`)

Após aproximadamente **10 segundos**, o servidor exibirá um log indicando que o nó expirou.

Exemplo de log:

```
[EXPIRED] Nó node1 expirou
```

Isso demonstra o mecanismo de **detecção de falha por ausência de heartbeat**, comum em sistemas distribuídos.

---

# Logs do Servidor

O servidor registra eventos importantes no terminal:

- Conexão de clientes
- Registro de nós
- Heartbeats recebidos
- Listagem de nós ativos
- Desconexão de nós
- Expiração de nós

Exemplo:

```
[CONNECTION] Cliente conectado: ('127.0.0.1', 52001)
[REGISTER] Nó registrado: node1
[HEARTBEAT] Recebido de node1
[LIST] Nós ativos: ['node1']
[EXPIRED] Nó node1 expirou
```

---

# Limitações

Este sistema é uma **implementação didática** e possui algumas limitações:

- não possui persistência de dados
- não possui autenticação
- não possui criptografia
- não possui tolerância avançada a falhas

Essas funcionalidades poderiam ser adicionadas em versões futuras.

---

# Conclusão

O projeto demonstra conceitos básicos de **sistemas paralelos e distribuídos**, incluindo:

- comunicação em rede via TCP
- descoberta de nós
- monitoramento de disponibilidade
- detecção de falha via heartbeat

A implementação foi feita utilizando apenas bibliotecas padrão do Python, mantendo o sistema simples e adequado para fins acadêmicos.
