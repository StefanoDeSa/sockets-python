import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 5000
TIMEOUT = 10

nodes = {}
nodes_lock = threading.Lock()


def log(msg):
    """Log com timestamp"""
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] {msg}")


def get_active_nodes():
    """Retorna lista de nós ativos"""
    current_time = time.time()
    active = []

    with nodes_lock:
        for node_id, last_heartbeat in nodes.items():
            if current_time - last_heartbeat <= TIMEOUT:
                active.append(node_id)

    return active


def monitor_expired_nodes():
    """Thread que detecta nós expirados"""
    while True:
        current_time = time.time()

        with nodes_lock:
            for node_id, last_heartbeat in nodes.items():
                if current_time - last_heartbeat > TIMEOUT:
                    log(f"[EXPIRED] Nó {node_id} expirou")

        time.sleep(1)


def process_command(message):
    message = message.strip()

    if message.startswith("REGISTER:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            nodes[node_id] = time.time()

        log(f"[REGISTER] Nó registrado: {node_id}")

        return "OK:REGISTERED"

    elif message.startswith("HEARTBEAT:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            if node_id in nodes:
                nodes[node_id] = time.time()
                log(f"[HEARTBEAT] Recebido de {node_id}")
                return "OK:HEARTBEAT"
            else:
                return "ERROR:NOT_REGISTERED"

    elif message == "LIST":
        active_nodes = get_active_nodes()
        log(f"[LIST] Nós ativos: {active_nodes}")
        return "NODES:" + ",".join(active_nodes)

    elif message.startswith("QUIT:"):
        node_id = message.split(":", 1)[1]

        with nodes_lock:
            if node_id in nodes:
                del nodes[node_id]

        log(f"[DISCONNECT] Nó removido: {node_id}")

        return "OK:BYE"

    else:
        log(f"[ERROR] Comando desconhecido: {message}")
        return "ERROR:UNKNOWN_COMMAND"


def handle_client(conn, addr):
    log(f"[CONNECTION] Cliente conectado: {addr}")

    try:
        while True:
            data = conn.recv(1024)

            if not data:
                break

            message = data.decode().strip()
            log(f"[RECEIVED] {message}")

            response = process_command(message)

            conn.sendall((response + "\n").encode())

            if response == "OK:BYE":
                break

    except Exception as e:
        log(f"[ERROR] {addr} -> {e}")

    finally:
        conn.close()
        log(f"[DISCONNECTED] {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    log(f"[STARTED] Servidor escutando em {HOST}:{PORT}")

    # thread de monitoramento
    monitor_thread = threading.Thread(target=monitor_expired_nodes, daemon=True)
    monitor_thread.start()

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    main()