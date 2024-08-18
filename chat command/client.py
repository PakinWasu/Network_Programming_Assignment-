import asyncio
import socket
import struct

async def receive_messages(sock):
    while True:
        data, _ = await asyncio.get_event_loop().run_in_executor(None, sock.recvfrom, 1024)
        print(data.decode())

async def main():
    multicast_group = ('224.0.0.1', 5000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', multicast_group[1]))
    
    mreq = struct.pack('4sl', socket.inet_aton(multicast_group[0]), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    asyncio.create_task(receive_messages(sock))
    
    while True:
        message = input()
        sock.sendto(message.encode(), multicast_group)

asyncio.run(main())
