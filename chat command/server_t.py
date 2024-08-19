import socket  # นำเข้าโมดูลสำหรับการทำงานกับซ็อกเก็ต
import threading  # นำเข้าโมดูลสำหรับการทำงานกับเธรด (หลายงานพร้อมกัน)
import time  # นำเข้าโมดูลสำหรับการจัดการเวลา

rooms = {}  # ดิกชันนารีสำหรับเก็บข้อมูลห้องและซ็อกเก็ตที่เชื่อมต่ออยู่
socketroom = {}  # ดิกชันนารีสำหรับเก็บการเชื่อมโยงระหว่างซ็อกเก็ตและห้องที่เชื่อมต่อ
socketname = {}  # ดิกชันนารีสำหรับเก็บชื่อผู้ใช้ของซ็อกเก็ต

def broadcast(roomid, message, sender):
    # ฟังก์ชันสำหรับส่งข้อความไปยังทุกซ็อกเก็ตในห้อง ยกเว้นซ็อกเก็ตของผู้ส่ง
    for client_socket in rooms.get(roomid, []):  # สำหรับซ็อกเก็ตทั้งหมดในห้องที่ระบุ
        if client_socket != sender:  # ถ้าไม่ใช่ซ็อกเก็ตของผู้ส่ง
            try:
                client_socket.send(message.encode())  # ส่งข้อความ
            except Exception as e:  # หากเกิดข้อผิดพลาด
                print(f"Error sending message: {e}")  # แสดงข้อผิดพลาด

def handle_client(client_socket, address):
    # ฟังก์ชันสำหรับจัดการการเชื่อมต่อของลูกค้า
    print(f"Connection from {address} has been established.")  # แสดงข้อความเมื่อมีการเชื่อมต่อใหม่
    
    username = client_socket.recv(1024).decode().strip()  # รับชื่อผู้ใช้จากลูกค้า
    client_socket.send(f"Your username is: {username}".encode())  # ส่งข้อความยืนยันชื่อผู้ใช้กลับไป
    
    roomid = client_socket.recv(1024).decode().strip()  # รับ ID ห้องจากลูกค้า
    client_socket.send(f"\nYour room ID to join is : {roomid}\n{'-'*40} \n".encode())  # ส่งข้อความยืนยัน ID ห้องกลับไป
    socketroom[client_socket] = roomid  # เก็บข้อมูลห้องที่ซ็อกเก็ตนี้เชื่อมต่ออยู่
    socketname[client_socket] = username  # เก็บชื่อผู้ใช้ของซ็อกเก็ตนี้
    
    if roomid not in rooms:  # ถ้าห้องยังไม่มีในดิกชันนารี
        rooms[roomid] = []  # สร้างรายการสำหรับห้องใหม่
    
    rooms[roomid].append(client_socket)  # เพิ่มซ็อกเก็ตเข้าไปในห้องที่ระบุ
    
    # แจ้งให้ห้องทราบว่ามีผู้ใช้ใหม่เข้ามา
    timestamp = time.strftime("%H:%M:%S")  # รับเวลาปัจจุบันในรูปแบบ ชั่วโมง:นาที:วินาที
    broadcast(roomid, f"[{timestamp}] {username} has joined the room.", client_socket)  # ส่งข้อความเข้าห้อง

    while True:  # ลูปหลักสำหรับรับข้อความจากลูกค้า
        try:
            message = client_socket.recv(1024).decode()  # รับข้อความจากลูกค้า
            if message:  # ถ้ามีข้อความ
                timestamp = time.strftime("%H:%M:%S")  # รับเวลาปัจจุบัน
                broadcast(roomid, f"[{timestamp}] {username}: {message}", client_socket)  # ส่งข้อความเข้าห้อง
            else:  # ถ้าไม่มีข้อความ (ลูกค้าอาจปิดการเชื่อมต่อ)
                break  # ออกจากลูป
        except Exception as e:  # หากเกิดข้อผิดพลาด
            print(f"Error receiving message: {e}")  # แสดงข้อผิดพลาด
            break  # ออกจากลูป

    # แจ้งให้ห้องทราบว่ามีผู้ใช้ออกจากห้อง
    rooms[roomid].remove(client_socket)  # ลบซ็อกเก็ตออกจากห้อง
    timestamp = time.strftime("%H:%M:%S")  # รับเวลาปัจจุบัน
    broadcast(roomid, f"[{timestamp}] {username} has left the room.", client_socket)  # ส่งข้อความออกจากห้อง
    
    client_socket.close()  # ปิดการเชื่อมต่อซ็อกเก็ต
    del socketroom[client_socket]  # ลบข้อมูลห้องของซ็อกเก็ต
    del socketname[client_socket]  # ลบข้อมูลชื่อผู้ใช้ของซ็อกเก็ต

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้างซ็อกเก็ตแบบ TCP/IP
    server.bind(('0.0.0.0', 12345))  # ผูกซ็อกเก็ตกับ IP '0.0.0.0' และพอร์ต 12345
    server.listen(5)  # ฟังการเชื่อมต่อสูงสุด 5 รายการ
    print("Server is listening on port 12345")  # แสดงข้อความว่าพร้อมรับการเชื่อมต่อ

    while True:  # ลูปหลักของเซิร์ฟเวอร์
        client_socket, address = server.accept()  # รอรับการเชื่อมต่อจากลูกค้า
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))  # สร้างเธรดสำหรับจัดการลูกค้า
        client_thread.start()  # เริ่มเธรด

if __name__ == "__main__":
    main()  # เรียกใช้ฟังก์ชัน main เมื่อไฟล์นี้ถูกรัน
