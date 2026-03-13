import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 5000
TIMEOUT = 10

# Registro de nós: node_id -> timestamp do último heartbeat
nodes = {}

# Lock para evitar problemas de concorrência
nodes_lock = threading.Lock()


def get_active_nodes():
    """Retorna lista de nós ativos (heartbeat nos últimos TIMEOUT segundos)"""
    current_time = time.time()
    active = []

    with nodes_lock:
        for node_id, last_heartbeat in nodes.items():
            if current_time - last_heartbeat <= TIMEOUT:
                active.append(node_id)

    return active


def process_command(message):
    """Processa comandos recebidos dos clientes"""
    message = message.strip()

    # REGISTER
    if message.startswith("REGISTER:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            nodes[node_id] = time.time()

        return "OK:REGISTERED"

    # HEARTBEAT
    elif message.startswith("HEARTBEAT:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            if node_id in nodes:
                nodes[node_id] = time.time()
                return "OK:HEARTBEAT"
            else:
                return "ERROR:NOT_REGISTERED"

    # LIST
    elif message == "LIST":
        active_nodes = get_active_nodes()
        return "NODES:" + ",".join(active_nodes)

    # QUIT
    elif message.startswith("QUIT:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            if node_id in nodes:
                del nodes[node_id]

        return "OK:BYE"

    else:
        return "ERROR:UNKNOWN_COMMAND"


def handle_client(conn, addr):
    """Thread que gerencia comunicação com um cliente"""
    print(f"[CONNECTION] Cliente conectado: {addr}")

    try:
        while True:
            data = conn.recv(1024)

            if not data:
                break

            message = data.decode().strip()
            print(f"[RECEIVED] {message}")

            response = process_command(message)

            conn.sendall((response + "\n").encode())

            # encerra conexão após QUIT
            if response == "OK:BYE":
                break

    except Exception as e:
        print(f"[ERROR] {addr} -> {e}")

    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[STARTED] Servidor escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    main()