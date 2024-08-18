import asyncio
import socket
import struct
import datetime

class MulticastChatRoom:
    def __init__(self, multicast_group, port):
        self.multicast_group = multicast_group
        self.port = port
        self.clients = []

    async def broadcast(self, message):
        for client in self.clients:
            client.sendto(message.encode(), self.multicast_group)

async def handle_client(sock, chat_room):
    while True:
        data, addr = await asyncio.get_event_loop().run_in_executor(None, sock.recvfrom, 1024)
        message = data.decode()
        timestamped_message = f"{datetime.datetime.now()} - {addr}: {message}"
        print(timestamped_message)
        await chat_room.broadcast(timestamped_message)

async def main():
    multicast_group = ('224.0.0.1', 5000)
    port = 5000
    chat_room = MulticastChatRoom(multicast_group, port)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    
    mreq = struct.pack('4sl', socket.inet_aton(multicast_group[0]), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    async def send_messages():
        while True:
            message = input()
            chat_room.broadcast(message)

    asyncio.create_task(handle_client(sock, chat_room))
    await send_messages()

asyncio.run(main())
