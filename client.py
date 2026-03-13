import socket
import time
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

HEARTBEAT_INTERVAL = 5
LIST_INTERVAL = 10
RUN_TIME = 30


def send_command(sock, command):
    """Envia comando ao servidor e retorna a resposta"""
    sock.sendall((command + "\n").encode())
    response = sock.recv(1024).decode().strip()
    print(f"[SERVER] {response}")
    return response


def main():

    if len(sys.argv) < 2:
        print("Uso: python client.py <node_id>")
        return

    node_id = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    print(f"[CONNECTED] Node {node_id}")

    # registro
    send_command(sock, f"REGISTER:{node_id}")

    start_time = time.time()
    last_heartbeat = 0
    last_list = 0

    while True:

        current_time = time.time()

        # envia heartbeat
        if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
            send_command(sock, f"HEARTBEAT:{node_id}")
            last_heartbeat = current_time

        # consulta nós ativos
        if current_time - last_list >= LIST_INTERVAL:
            send_command(sock, "LIST")
            last_list = current_time

        # encerra após RUN_TIME segundos
        if current_time - start_time >= RUN_TIME:
            send_command(sock, f"QUIT:{node_id}")
            break

        time.sleep(1)

    sock.close()
    print("[DISCONNECTED]")


if __name__ == "__main__":
    main()