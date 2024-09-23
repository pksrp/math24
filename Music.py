import pygame

def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load("music.mp3")  # Specify the music file path
    pygame.mixer.music.play()