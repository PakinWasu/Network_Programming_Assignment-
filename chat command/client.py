import socket
import threading
import time

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    
    username = input("Enter your username: ")
    client_socket.send(username.encode())
    
    roomid = input("Enter room ID to join: ")
    client_socket.send(roomid.encode())
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()
    
    while True:
        message = input() 
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] You: {message}")
        if message.lower() == 'exit':
            break
        client_socket.send(message.encode())
    
    client_socket.close()

if __name__ == "__main__":
    main()
