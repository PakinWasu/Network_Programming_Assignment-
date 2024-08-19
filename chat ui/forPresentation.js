const path = require('path'); // เรียกใช้โมดูล path เพื่อจัดการกับเส้นทางไฟล์
const express = require('express'); // เรียกใช้ express framework
const http = require('http'); // เรียกใช้โมดูล http สำหรับสร้าง HTTP server
const moment = require('moment'); // เรียกใช้ moment เพื่อจัดการกับวันที่และเวลา
const socketio = require('socket.io'); // เรียกใช้ socket.io เพื่อสร้างการเชื่อมต่อแบบเรียลไทม์

const PORT = process.env.PORT || 3000; // กำหนดค่าพอร์ตเป็นค่าจาก environment หรือใช้พอร์ต 3000

const app = express(); // สร้าง express application
const server = http.createServer(app); // สร้าง HTTP server จาก express application

const io = socketio(server); // สร้าง instance ของ socket.io และผูกกับ HTTP server

app.use(express.static(path.join(__dirname, 'public'))); // กำหนด express ให้เสิร์ฟไฟล์ static จากโฟลเดอร์ 'public'

let rooms = {}; // เก็บข้อมูลห้องแชทและสมาชิกในห้องแต่ละห้อง
let socketroom = {}; // เก็บข้อมูลว่าผู้ใช้แต่ละ socket อยู่ในห้องไหน
let socketname = {}; // เก็บชื่อของผู้ใช้แต่ละ socket
let micSocket = {}; // เก็บสถานะไมโครโฟนของแต่ละ socket
let videoSocket = {}; // เก็บสถานะวิดีโอของแต่ละ socket
let roomBoard = {}; // เก็บข้อมูลกระดานวาดภาพของแต่ละห้อง

io.on('connect', socket => { // เมื่อมีผู้ใช้เชื่อมต่อ socket

    socket.on("join room", (roomid, username) => { // เมื่อผู้ใช้เข้าร่วมห้องแชท

        socket.join(roomid); // ผู้ใช้เข้าร่วมห้องตาม roomid
        socketroom[socket.id] = roomid; // บันทึกห้องที่ผู้ใช้เข้าร่วม
        socketname[socket.id] = username; // บันทึกชื่อผู้ใช้
        micSocket[socket.id] = 'on'; // กำหนดสถานะไมโครโฟนเป็น 'on'
        videoSocket[socket.id] = 'on'; // กำหนดสถานะวิดีโอเป็น 'on'

        if (rooms[roomid] && rooms[roomid].length > 0) { // ถ้ามีผู้ใช้ในห้องนี้แล้ว
            rooms[roomid].push(socket.id); // เพิ่มผู้ใช้ใหม่เข้าไปในห้อง
            socket.to(roomid).emit('message', `${username} joined the room.`, 'Bot', moment().format("h:mm a")); // แจ้งผู้ใช้คนอื่นว่ามีผู้ใช้ใหม่เข้าห้อง
            io.to(socket.id).emit('join room', rooms[roomid].filter(pid => pid != socket.id), socketname, micSocket, videoSocket); // ส่งข้อมูลผู้ใช้ในห้องให้ผู้ใช้ใหม่
        } else {
            rooms[roomid] = [socket.id]; // ถ้าห้องยังไม่มีผู้ใช้ ให้สร้างห้องใหม่
            io.to(socket.id).emit('join room', null, null, null,null); // ส่งข้อมูลว่าผู้ใช้เป็นคนแรกในห้อง
        }

        io.to(roomid).emit('user count', rooms[roomid].length); // แจ้งจำนวนผู้ใช้ในห้อง

    });

    socket.on('action', msg => { // ฟังการกระทำต่างๆ จากผู้ใช้
        if (msg == 'mute') // ถ้าเป็นการปิดไมโครโฟน
            micSocket[socket.id] = 'off'; // เปลี่ยนสถานะไมโครโฟนเป็น 'off'
        else if (msg == 'unmute') // ถ้าเป็นการเปิดไมโครโฟน
            micSocket[socket.id] = 'on'; // เปลี่ยนสถานะไมโครโฟนเป็น 'on'
        else if (msg == 'videoon') // ถ้าเป็นการเปิดวิดีโอ
            videoSocket[socket.id] = 'on'; // เปลี่ยนสถานะวิดีโอเป็น 'on'
        else if (msg == 'videooff') // ถ้าเป็นการปิดวิดีโอ
            videoSocket[socket.id] = 'off'; // เปลี่ยนสถานะวิดีโอเป็น 'off'

        socket.to(socketroom[socket.id]).emit('action', msg, socket.id); // ส่งการกระทำไปยังผู้ใช้คนอื่นในห้อง
    })

    socket.on('video-offer', (offer, sid) => { // เมื่อมีการส่งวิดีโอข้อเสนอจากผู้ใช้
        socket.to(sid).emit('video-offer', offer, socket.id, socketname[socket.id], micSocket[socket.id], videoSocket[socket.id]); // ส่งวิดีโอข้อเสนอไปยังผู้รับ
    })
    socket.on('video-answer', (answer, sid) => { // เมื่อมีการตอบรับวิดีโอข้อเสนอ
        socket.to(sid).emit('video-answer', answer, socket.id); // ส่งการตอบรับกลับไปยังผู้ใช้ที่เริ่มการเชื่อมต่อ
    })

    socket.on('new icecandidate', (candidate, sid) => { // เมื่อมีการส่ง candidate ของ WebRTC
        socket.to(sid).emit('new icecandidate', candidate, socket.id); // ส่ง candidate ไปยังผู้รับ
    })
    socket.on('message', (msg, username, roomid) => { // เมื่อมีการส่งข้อความในห้อง
        io.to(roomid).emit('message', msg, username, moment().format("h:mm a")); // ส่งข้อความไปยังผู้ใช้ทุกคนในห้อง
    })
    socket.on('getCanvas', () => { // เมื่อผู้ใช้ร้องขอข้อมูลกระดานวาดภาพ
        if (roomBoard[socketroom[socket.id]]) // ถ้ามีกระดานวาดภาพในห้อง
            socket.emit('getCanvas', roomBoard[socketroom[socket.id]]); // ส่งข้อมูลกระดานวาดภาพกลับไป
    });
    socket.on('draw', (newx, newy, prevx, prevy, color, size) => { // เมื่อมีการวาดบนกระดาน
        socket.to(socketroom[socket.id]).emit('draw', newx, newy, prevx, prevy, color, size); // ส่งข้อมูลการวาดไปยังผู้ใช้คนอื่นในห้อง
    })
    socket.on('clearBoard', () => { // เมื่อมีการล้างกระดานวาด
        socket.to(socketroom[socket.id]).emit('clearBoard'); // แจ้งผู้ใช้คนอื่นในห้องให้ล้างกระดานวาด
    });
    socket.on('store canvas', url => { // เมื่อมีการบันทึกกระดานวาดเป็นภาพ
        roomBoard[socketroom[socket.id]] = url; // บันทึกภาพของกระดานวาดในห้อง
    })
    
    socket.on('disconnect', () => { // เมื่อผู้ใช้ตัดการเชื่อมต่อ
        if (!socketroom[socket.id]) return; // ถ้าไม่มีข้อมูลห้องของผู้ใช้ ให้หยุดการทำงาน
        socket.to(socketroom[socket.id]).emit('message', `${socketname[socket.id]} left the chat.`, `Bot`, moment().format("h:mm a")); // แจ้งผู้ใช้คนอื่นว่ามีผู้ใช้ออกจากห้อง
        socket.to(socketroom[socket.id]).emit('remove peer', socket.id); // แจ้งให้ลบผู้ใช้ออกจากระบบ

        var index = rooms[socketroom[socket.id]].indexOf(socket.id); // ค้นหาตำแหน่งของผู้ใช้ในห้อง
        rooms[socketroom[socket.id]].splice(index, 1); // ลบผู้ใช้ออกจากห้อง

        io.to(socketroom[socket.id]).emit('user count', rooms[socketroom[socket.id]].length); // อัพเดทจำนวนผู้ใช้ในห้อง
        delete socketroom[socket.id]; // ลบข้อมูลห้องของผู้ใช้
    });
})

// เริ่มเซิร์ฟเวอร์และฟังที่พอร์ตที่กำหนด
server.listen(PORT, () => console.log(`Server is up and running on port ${PORT}`)); 
