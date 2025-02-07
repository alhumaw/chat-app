import tkinter as tk
from tkinter import ttk
from client import Client
from crypto import SuperSecret

class Screen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Client")
        self.client_name = None
        self.parse_name()
        

    def set_name(self, event):
        client_input = self.textbox.get()
        self.client_name = client_input
        self.textbox.destroy()
        self.client = Client('127.0.0.1', 7632, self.client_name, update_callback=self.display_message)
        self.client.send_message(self.client_name)
        self.create_widgets()

    def parse_name(self):
        label = tk.Label(self.root, text="Enter your name: ")
        self.textbox = tk.Entry(self.root, font=("Times New Roman", 24)) 
        self.textbox.pack(fill="x", padx=10, pady=5) 
        self.textbox.bind("<Return>", self.set_name)


    def create_widgets(self):
        self.root.geometry("480x480")
        
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        self.text_area = tk.Text(self.chat_frame, wrap=tk.WORD, font=("Times New Roman", 15), state="disabled")
        self.text_area.grid(row=0, column=0, sticky="nsew")
        
        self.chat_frame.rowconfigure(0, weight=1)
        self.chat_frame.columnconfigure(0, weight=1)


        self.textbox = tk.Entry(self.root, font=("Times New Roman", 24)) 
        self.textbox.pack(fill="x", padx=10, pady=5) 
        self.textbox.bind("<Return>", self.parse_entry_text)
        
    def parse_entry_text(self, event):
        client_input = self.textbox.get()
        if client_input.startswith("/accept"):
            parts = client_input.split(" ")
            if len(parts) < 2:
                self._update_text_area("Usage: /accept <sender>")
                self.textbox.delete(0, tk.END)
                return
            sender = parts[1].strip()
            if sender in self.client.pending_requests:
                req = self.client.pending_requests.pop(sender)
                p, g = req['params'].split(";")
                secret = SuperSecret(p=int(p), g=int(g))
                secret.generate_private_key()
                secret.generate_public_key()
                secret.generate_shared_secret(req['public_key'])
                self.client.send_message(f"KEYRESP|{secret.p};{secret.g}|{secret.public_key}|{sender.lower()}")
                self._update_text_area(f"Shared secret is: {secret.shared_secret}")
                self.textbox.delete(0, tk.END)
            else:
                self._update_text_area(f"No pending key exchange from {sender}.")
                self.textbox.delete(0, tk.END)
            return

        # Handle denying a key exchange.
        if client_input.startswith("/deny"):
            parts = client_input.split(" ")
            if len(parts) < 2:
                self._update_text_area("Usage: /deny <sender>")
                self.textbox.delete(0, tk.END)
                return
            sender = parts[1].strip()
            if sender in self.client.pending_requests:
                self.client.pending_requests.pop(sender)
                self._update_text_area(f"Denied key exchange from {sender}.")
                self.textbox.delete(0, tk.END)
            else:
                self._update_text_area(f"No pending key exchange from {sender}.")
                self.textbox.delete(0, tk.END)
            return

        # Initiate a key exchange.
        if client_input.startswith("/sharedsecret"):
            parse_message = client_input.split(" ")
            if len(parse_message) < 2:
                self._update_text_area("Usage: /sharedsecret <receiver>")
                self.textbox.delete(0, tk.END)
                return
            receiver = parse_message[1].strip()

            secret = SuperSecret()
            secret.generate_private_key()
            secret.generate_public_key()
            key_request = f"KEYREQ|{secret.p};{secret.g}|{secret.public_key}|{receiver}"
            client_message = "/sharedsecret " + key_request
            self.secret = secret.secret
            self.public_key = secret.public_key                
            self.client.send_message(client_message)
            self.textbox.delete(0, tk.END)
            return 

        self.client.send_message(client_input)
        self._update_text_area("You: " + client_input)
        self.textbox.delete(0, tk.END)
    
    def display_message(self, message):
        self.root.after(0, lambda: self._update_text_area(message))
    
    def _update_text_area(self, message):
        # Split to see if it is a key exchange message.
        parts = message.split(" ")
        sender = parts[0].rstrip(":")
        command_part = parts[1].strip()
        if command_part.startswith("KEYREQ"):
            key_req_parts = command_part.split("|")
            if len(key_req_parts) >= 4:
                target = key_req_parts[3].strip().lower()
                if target == self.client_name.lower():
                    self.client.pending_requests[sender] = {
                        'params': key_req_parts[1],
                        'public_key': key_req_parts[2]
                    }
                    msg = f"{sender} would like to generate a shared secret with you."
                    self.text_area.config(state="normal")
                    self.text_area.insert(tk.END, msg + "\n")
                    self.text_area.config(state="disabled")
                    msg = f"Type '/accept {sender}' to accept or '/deny {sender}' to decline."
                    self.text_area.config(state="normal")
                    self.text_area.insert(tk.END, msg + "\n")
                    self.text_area.config(state="disabled")
                    return

        elif command_part.startswith("KEYRESP"):
            key_resp_parts = command_part.split("|")
            if len(key_resp_parts) >= 4:
                target = key_resp_parts[3].strip().lower()
                if target == self.client_name.lower():
                    msg = f"{sender} accepted your request to generate a shared secret."
                    self.text_area.config(state="normal")
                    self.text_area.insert(tk.END, msg + "\n")
                    self.text_area.config(state="disabled")
                    p, g = key_resp_parts[1].split(";")
                    secret = SuperSecret(p=int(p), g=int(g))
                    secret.secret = self.secret
                    secret.generate_shared_secret(key_resp_parts[2])
                    msg = f"Shared secret is: {secret.shared_secret}"
                    self.text_area.config(state="normal")
                    self.text_area.insert(tk.END, msg + "\n")
                    self.text_area.config(state="disabled")
                    return
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state="disabled")
    
 

    def run(self):
        self.root.mainloop()

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == '__main__':
    screen = Screen()
    center_window(screen.root)
    screen.run()
