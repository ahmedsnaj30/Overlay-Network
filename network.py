import socket
import ssl
import threading
import time

SERVER_IP = '127.0.0.1' # loopback
SERVER_PORT = 5608

registered_clients = {}
client_sockets = []

list_lock = threading.Lock()

def handle_client_reg(client_socket, client_addr):
    while True:
        data = client_socket.recv(1024)
        client_name = data.decode('utf-8') + ".c6610.uml.edu"
        if not client_name:
            break

        if client_name not in registered_clients.values():
            registered_clients[client_addr] = client_name
            client_sockets.append(client_socket)
            print(f"{client_name} registered on Network")
            reg_ack = f"- Registered with name {client_name}"
        else:
            print(f"{client_name} already exists.")
            reg_ack = "- Name already taken."

        client_socket.send(reg_ack.encode('utf-8'))

def send_client_list():
    while True:
        with list_lock:
            client_list = list(registered_clients.values())
            ping_list = [(key, value) for key, value in registered_clients.items()]
            formatted_client_list = "\n".join(f"* {client}" for client in client_list)
            formatted_ping_list = bytes(str(ping_list), encoding='utf-8')
            #*
        for client_socket in client_sockets:
            try:
                client_socket.send(formatted_client_list.encode('utf-8'))
                client_socket.send(formatted_ping_list)

            except Exception as e:
                print(f"Error sending list to client: {e}") 
        time.sleep(10)

def main():     

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')
    context.load_verify_locations(cafile='ca_cert.pem') 
    context.verify_mode = ssl.CERT_REQUIRED

    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((SERVER_IP, SERVER_PORT))
        sock.listen(5)
        print(f"-- Network started at address {SERVER_IP}")
        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
        with context.wrap_socket(sock, server_side=True) as ssock:
    
            update_thread = threading.Thread(target=send_client_list)
            update_thread.start()
            while True:
            
                client_socket, client_addr = ssock.accept()

                print(f"Connected with client {client_addr}")
                client_list_receiver = threading.Thread(target=handle_client_reg,args=(client_socket,client_addr))
                client_list_receiver.start()
        

if __name__ == '__main__':
    main()
