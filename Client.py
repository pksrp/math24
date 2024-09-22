import socket
import pygame
from music import play_music

# ตั้งค่าไคลเอนต์เชื่อมต่อกับเซิร์ฟเวอร์
SERVER = "127.0.0.1"  # ใช้ IP ของเซิร์ฟเวอร์ที่คุณต้องการเชื่อมต่อ
PORT = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))  # เชื่อมต่อไปยังเซิร์ฟเวอร์

# ตั้งค่า UI ของ Pygame
pygame.init()
win = pygame.display.set_mode((500, 500))  # สร้างหน้าต่างแสดงผลขนาด 500x500
pygame.display.set_caption("Game 24 Multiplayer")
font = pygame.font.SysFont("comicsans", 30)  # ฟอนต์สำหรับแสดงข้อความ
bg_color = (255, 255, 255)  # สีพื้นหลัง

# ตัวแปรสำหรับเก็บข้อมูลในเกม
expression = ""  # เก็บสมการที่ผู้เล่นพิมพ์
result = ""  # เก็บผลลัพธ์ที่ได้จากเซิร์ฟเวอร์
game_started = False  # ตัวแปรบอกสถานะว่าเกมเริ่มแล้วหรือยัง

# ฟังก์ชันสำหรับการวาดหน้าต่าง UI
def redraw_window():
    win.fill(bg_color)
    text = font.render(f"Expression: {expression}", True, (0, 0, 0))  # แสดงสมการที่ผู้เล่นพิมพ์
    result_text = font.render(f"Result: {result}", True, (0, 0, 0))  # แสดงผลลัพธ์
    win.blit(text, (50, 50))
    win.blit(result_text, (50, 100))
    pygame.display.update()  # อัปเดตหน้าจอ

# ฟังก์ชันสำหรับส่งสมการไปยังเซิร์ฟเวอร์
def send_expression(expression):
    client.send(expression.encode('utf-8'))  # ส่งสมการไปยังเซิร์ฟเวอร์
    return client.recv(1024).decode('utf-8')  # รับผลลัพธ์กลับมา

# ฟังก์ชันหลักที่เรียกใช้ UI และรันเกม
def main():
    global expression, result, game_started
    run = True
    play_music()

    # แจ้งเซิร์ฟเวอร์ว่าผู้เล่นพร้อม
    client.send("PLAYER_READY".encode('utf-8'))

    while run:
        redraw_window()  # อัปเดต UI ทุกครั้งที่มีการเปลี่ยนแปลง

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.send("DISCONNECT".encode('utf-8'))  # ส่งข้อความ DISCONNECT ไปที่เซิร์ฟเวอร์เมื่อปิดเกม
                run = False  # หยุดลูปเกม

            # รอจนกว่าเกมจะเริ่ม
            if not game_started:
                msg = client.recv(1024).decode('utf-8')  # รอรับข้อความจากเซิร์ฟเวอร์
                if msg == "GAME_START":
                    game_started = True  # เกมเริ่มได้เมื่อเซิร์ฟเวอร์ส่งข้อความว่าเริ่มเกม

            # การจัดการคีย์บอร์ดเมื่อเกมเริ่ม
            if event.type == pygame.KEYDOWN and game_started:
                if event.key == pygame.K_RETURN:
                    result = send_expression(expression)  # ส่งสมการไปเซิร์ฟเวอร์และรับผลลัพธ์
                    expression = ""  # รีเซ็ตสมการหลังจากกด Enter
                elif event.key == pygame.K_BACKSPACE:
                    expression = expression[:-1]  # ลบตัวอักษรล่าสุดเมื่อกด Backspace
                else:
                    expression += event.unicode  # เพิ่มตัวอักษรลงในสมการที่ผู้เล่นพิมพ์

    pygame.quit()  # ปิด Pygame เมื่อเกมจบ

# เรียกใช้ฟังก์ชัน main() ทันทีเมื่อเปิดไฟล์
if __name__ == "__main__":
    main()
