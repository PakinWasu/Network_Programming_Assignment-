import socket  # นำเข้าโมดูลสำหรับการทำงานกับซ็อกเก็ต
import threading  # นำเข้าโมดูลสำหรับการทำงานกับเธรด (หลายงานพร้อมกัน)
import time  # นำเข้าโมดูลสำหรับการจัดการเวลา

def receive_messages(client_socket):
    # ฟังก์ชันสำหรับรับข้อความจากเซิร์ฟเวอร์
    while True:  # ทำงานในลูปไม่สิ้นสุด
        try:
            message = client_socket.recv(1024).decode()  # รับข้อมูลจากซ็อกเก็ต (สูงสุด 1024 ไบต์) และแปลงเป็นข้อความ
            if message:  # ถ้ามีข้อความ
                print(message)  # แสดงข้อความ
            else:  # ถ้าไม่มีข้อความ (เช่น การเชื่อมต่อถูกปิด)
                break  # ออกจากลูป
        except Exception as e:  # หากเกิดข้อผิดพลาด
            print(f"Error receiving message: {e}")  # แสดงข้อผิดพลาด
            break  # ออกจากลูป

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้างซ็อกเก็ตแบบ TCP/IP
    client_socket.connect(('localhost', 12345))  # เชื่อมต่อไปยังเซิร์ฟเวอร์ที่ IP 'localhost' และพอร์ต 12345
    
    username = input("Enter your username: ")  # รับชื่อผู้ใช้จากผู้ใช้
    client_socket.send(username.encode())  # ส่งชื่อผู้ใช้ไปยังเซิร์ฟเวอร์
    
    roomid = input("Enter room ID to join: ")  # รับ ID ห้องจากผู้ใช้
    client_socket.send(roomid.encode())  # ส่ง ID ห้องไปยังเซิร์ฟเวอร์
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))  # สร้างเธรดสำหรับรับข้อความ
    receive_thread.start()  # เริ่มเธรด

    while True:  # ลูปหลักของโปรแกรม
        message = input()  # รับข้อความจากผู้ใช้
        timestamp = time.strftime("%H:%M:%S")  # รับเวลาในรูปแบบ ชั่วโมง:นาที:วินาที
        print(f"[{timestamp}] You: {message}")  # แสดงข้อความของผู้ใช้พร้อมเวลา
        if message.lower() == 'exit':  # ถ้าข้อความเป็น 'exit'
            break  # ออกจากลูป
        client_socket.send(message.encode())  # ส่งข้อความไปยังเซิร์ฟเวอร์
    
    client_socket.close()  # ปิดการเชื่อมต่อซ็อกเก็ต

if __name__ == "__main__":
    main()  # เรียกใช้ฟังก์ชัน main เมื่อไฟล์นี้ถูกรัน
