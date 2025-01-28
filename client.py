import socket
import ssl
import argparse
import threading
import time

ping_list = []

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5608
PORT_START = 40000
CLIENT_SERVER_PORT_DICT = {'client1': 43501, 'client2': 43502, 'client3': 43503, 'client4': 43504, 'client5': 43505}

# Function to receive client list
def get_client_list(client_socket): # while loop made it loop a lot
    while True:
        try:
            client_list_data = client_socket.recv(1024)
            client_list = client_list_data.decode('utf-8')  # separate lines
            
            ping_list_data = client_socket.recv(1024)
            global ping_list
            decoded_ping_list = ping_list_data.decode('utf-8')  # separate lines
            ping_list = eval(decoded_ping_list)
            print("- Found client(s):\n", client_list)
        except Exception as e:
            print(f"Error receiving client list: {e}")
            break

def send_pings(connected, socket_list, CLIENT_NAME):
    while True:
        for sock in socket_list:
            i=0
            print(f"< {connected[i][1]}: PING")
            sock.send(f"< {CLIENT_NAME}.c6610.uml.edu: PING".encode('utf-8'))
            pong = (sock.recv(1024)).decode("utf-8")
            print(pong)
            i+=1

        time.sleep(15)

def open_connections(CLIENT_NAME):
    connected = []
    socket_list = []

    while True:
        for client in ping_list:
            if client[1][:7] == CLIENT_NAME: # dont ping yourself
                pass
            elif client not in connected: 
                CLIENT_SERVER_PORT = int(CLIENT_SERVER_PORT_DICT[client[1][:7]])
                
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations('ca_cert.pem')

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                ssock = context.wrap_socket(sock, server_hostname=SERVER_IP)
                ssock.connect((SERVER_IP, CLIENT_SERVER_PORT))
                connected.append(client)
                socket_list.append(ssock)
                client_thread = threading.Thread(target=send_pings, args=(connected, socket_list,CLIENT_NAME,))
                client_thread.daemon = True
                client_thread.start()             

def recieve_pings(CLIENT_NAME):
    client_cert = CLIENT_NAME + "_cert.pem"
    client_key = CLIENT_NAME + "_key.pem"

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((SERVER_IP, CLIENT_SERVER_PORT_DICT[CLIENT_NAME]))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            client_socket, addr = ssock.accept()
            while True:
                ping = (client_socket.recv(1024)).decode("utf-8")
                if ping:
                    client_socket.send((f"> {CLIENT_NAME}.c6610.uml.edu: PONG").encode("utf-8"))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--network", type=str)
    parser.add_argument("--name", type=str)

    args = parser.parse_args()

    SERVER_IP = args.network
    CLIENT_NAME = args.name
    
    client_cert = CLIENT_NAME + "_cert.pem"
    client_key = CLIENT_NAME + "_key.pem"

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile='ca_cert.pem')
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=SERVER_IP) as ssock:
            ssock.connect((SERVER_IP, SERVER_PORT))
            ssock.send(CLIENT_NAME.encode('utf-8'))

            response = ssock.recv(1024)
            print(f"{response.decode('utf-8')}")

            recv_list_thread = threading.Thread(target=get_client_list, args=(ssock,))
            recv_list_thread.start()

            recv_pings_thread = threading.Thread(target=recieve_pings, args=(CLIENT_NAME,))
            recv_pings_thread.start()

            send_pings_thread = threading.Thread(target=open_connections, args=(CLIENT_NAME,))
            send_pings_thread.start()

            while True:
                pass

if __name__ == '__main__':
    main()  
