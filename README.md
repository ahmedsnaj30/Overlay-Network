# Overlay-Network
An overlay network enabling clients to register, connect, and communicate with each other on a secure centralized server. 

## Notes
pip install argparse pycryptodome

(possibly need to do this)
sudo cp ca_cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates


Overlay Network:
Create an encrypted overlay network and create clients that utilize this overlay network for discovery and communication with other connected clients.

Should use a single network endpoint and multiple clients capable of connecting to this network. Clients should communicate with eachother as long as they are on the same network.

Each client's is "clientx.c6610.uml.edu" where x is the number.

Flow 1 -> Each client registers with the network.

Flow 2 -> Every 10 seconds, clients connect to the network to retrieve the names of all other connected clients.

Flow 3 -> Every 15 seconds, each running client establishes connections with other sending a PING message. Each client responds with a PONG. 

Client:
    - Entity initiating TLS Handshake
    - Example: Web browser
    - Optionally authenticated

Server:
    - Entity receiving the TLS Handshake
    - Web Server
    - Always authenticated -> provides certificate to client to validates its identity

Certificate Authority:
    - Governing entity that issues certs to servers
    - Trusted by Client and Server
