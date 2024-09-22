import pygame

def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load("background_music.mp3")  # เปลี่ยนชื่อไฟล์ตามที่คุณมี
    pygame.mixer.music.play(-1)  # เล่นวนไปเรื่อยๆ

def stop_music():
    pygame.mixer.music.stop()
