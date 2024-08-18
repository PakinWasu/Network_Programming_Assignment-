import socket
import threading
import time

# เก็บข้อมูลห้องและผู้ใช้
rooms = {}
socketroom = {}
socketname = {}

def broadcast(roomid, message, sender):
    for client_socket in rooms.get(roomid, []):
        if client_socket != sender:
            try:
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Error sending message: {e}")

def handle_client(client_socket, address):
    print(f"Connection from {address} has been established.")
    
    username = client_socket.recv(1024).decode().strip()
    client_socket.send(f"Your username is: {username}".encode())
    
    roomid = client_socket.recv(1024).decode().strip()
    client_socket.send(f"\nYour room ID to join is : {roomid}\n{'-'*40} \n".encode())
    socketroom[client_socket] = roomid
    socketname[client_socket] = username
    
    if roomid not in rooms:
        rooms[roomid] = []
    
    rooms[roomid].append(client_socket)
    
    # Notify room of new user
    timestamp = time.strftime("%H:%M:%S")
    broadcast(roomid, f"[{timestamp}] {username} has joined the room.", client_socket)
    
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                timestamp = time.strftime("%H:%M:%S")
                broadcast(roomid, f"[{timestamp}] {username}: {message}", client_socket)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break
    
    # Notify room of user leaving
    rooms[roomid].remove(client_socket)
    timestamp = time.strftime("%H:%M:%S")
    broadcast(roomid, f"[{timestamp}] {username} has left the room.", client_socket)
    
    client_socket.close()
    del socketroom[client_socket]
    del socketname[client_socket]

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("Server is listening on port 12345")

    while True:
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

if __name__ == "__main__":
    main()
