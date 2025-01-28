import subprocess

# CA key/cert generation

def gen_ca_key(ca_key='ca_key.pem'):
    subprocess.run(['openssl', 'genrsa', '-out', ca_key, '4096'], check=True)

def gen_ca_cert(ca_key='ca_key.pem', ca_cert='ca_cert.pem'):
    subprocess.run([
        'openssl', 'req', '-x509', '-new', '-nodes', '-key', ca_key,
        '-sha256', '-days', '1024', '-out', ca_cert,
        '-subj', '/CN=CA Certificate'
    ], check=True)

gen_ca_key()
gen_ca_cert()

# Server cert/key/csr generation

def gen_server_key(server_key_path='server_key.pem', key_size=2048):
    subprocess.run(['openssl', 'genrsa', '-out', server_key_path, str(key_size)])

def gen_server_csr(server_key_path='server_key.pem', csr_path='server.csr'):
    subprocess.run(['openssl', 'req', '-new', '-key', server_key_path, '-out', csr_path, '-subj', '/CN=Server'], check=True)

def gen_server_cert(server_csr_path='server.csr', ca_cert_path='ca_cert.pem', ca_key_path='ca_key.pem', server_cert_path='server_cert.pem'):
    subprocess.run([
        'openssl', 'x509', '-req', '-in', server_csr_path, '-CA', ca_cert_path,
        '-CAkey', ca_key_path, '-CAcreateserial', '-out', server_cert_path,
        '-days', '500', '-sha256', '-extfile', 'extfile.cnf', '-extensions', 'v3_req'
    ], check=True)

gen_server_key()
gen_server_csr()
gen_server_cert()

# Client key/csr/cert generation

def gen_client_key(client_key_path, key_size):
    subprocess.run(['openssl', 'genrsa', '-out', client_key_path, str(key_size)])

def gen_client_csr(client_key_path, csr_path, common_name):
    subprocess.run(['openssl', 'req', '-new', '-key', client_key_path, '-out', csr_path, '-subj', f'/CN={common_name}'], check=True)

def gen_client_cert(client_csr_path, ca_cert_path, ca_key_path, client_cert_path):
    subprocess.run([
        'openssl', 'x509', '-req', '-in', client_csr_path, '-CA', ca_cert_path,
        '-CAkey', ca_key_path, '-CAcreateserial', '-out', client_cert_path,
        '-days', '500', '-sha256', '-extfile', 'extfile.cnf', '-extensions', 'v3_req'
    ], check=True)

for i in range(1, 4):  # Change the range based on the number of clients you want
    gen_client_key(f'client{i}_key.pem', 2048)
    gen_client_csr(f'client{i}_key.pem', f'client{i}_csr.pem', f'Client{i}')
    gen_client_cert(f'client{i}_csr.pem', 'ca_cert.pem', 'ca_key.pem', f'client{i}_cert.pem')
