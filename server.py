import socket
from threading import Thread

class Server:
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print("Server waiting for connection") 

    def listen(self):
        while True:
            client_socket, address= self.socket.accept()
            print("Connection From: " + str(address))
            client_name = client_socket.recv(1024).decode().split(":")[0]
            client = {'client_name': client_name, 'client_socket': client_socket}
            self.broadcast_message(client_name, client_name + " has joined the chat!")

            Server.Clients.append(client)
            Thread(target = self.handle_new_client, args = (client,)).start()
    
    def route_message(self, sender: str, receiver: str, message: str):
        for client in self.Clients:
            if client['client_name'].lower() == receiver.lower():
                full_message = f"{sender}: {message}"
                client['client_socket'].send(full_message.encode())
                return True
        return False
    
    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        while True:
            # Listen out for messages and broadcast the message to all clients.
            client_message = client_socket.recv(1024).decode()
            # If the message is bye, remove the client from the list of clients and
            # close down the socket.
            if not client_message.strip():
                self.broadcast_message(client_name, client_name + " has left the chat!")
                Server.Clients.remove(client)
                client_socket.close()
                break
            # ['Alex:', '/dm', 'Daniel', 'hey', 'loser']
            elif client_message.strip().startswith(client_name + ": /dm"):
                split_msg = client_message.split(" ")
                message = " ".join(split_msg[3:])
                self.route_message(split_msg[0].rstrip(":"), split_msg[2], message)
            # ['Alex:', /sharedsecret, 'KEYREQ|p=23;g=5|12345|daniel']
            elif client_message.strip().startswith(client_name + ": /sharedsecret"):
                split_msg = client_message.split(" ")
                key_req = split_msg[2]
                self.route_message(split_msg[0].rstrip(":"), key_req.split("|")[3], key_req)
            elif "KEYRESP" in client_message:
                split_msg = client_message.split(" ")
                key_req = split_msg[1]
                self.route_message(split_msg[0].rstrip(":"), key_req.split("|")[3], key_req)
            else: 
                # Send the message to all other clients
                self.broadcast_message(client_name, client_message)


    def broadcast_message(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_name = client['client_name']
            if client_name != sender_name:
                client_socket.send(message.encode())

    
if __name__ == '__main__':
  server = Server('127.0.0.1', 7632)
  server.listen()