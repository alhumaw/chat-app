import socket
from threading import Thread
import os

class Client:
    def __init__(self, HOST, PORT, name, update_callback=None):
        self.update_callback = update_callback
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.name = name
        self.pending_requests = {}
        Thread(target=self.receive_message, daemon=True).start()
        self.public_key = None
        self.secret = None

    def talk_to_server(self):
        self.socket.send(self.name.encode())
        Thread(target=self.receive_message, daemon=True).start()
        self.send_message()

    def send_message(self, message):
        full_message = self.name + ": " + str(message)
        self.socket.send(full_message.encode())
      
    def receive_message(self):
        while True:
            server_message = self.socket.recv(1024).decode()
            if not server_message.strip():
                os._exit(0)
            if self.update_callback:
                self.update_callback(server_message)



if __name__ == '__main__':
    Client('127.0.0.1', 7632)
