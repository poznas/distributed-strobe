import pygame
from pygame import mixer
from pygame.mixer import SoundType

PLAYBACK_LATENCY = 150  # ms

mixer.pre_init(22050, -16, 2, 512)
mixer.init()
pygame.init()

sound: SoundType


def load_audio_file(filename):
    global sound
    sound = pygame.mixer.Sound(filename)
    sound.set_volume(1.0)


def play_music():
    print("▶ play music")
    sound.play()


def stop_music():
    print("❌ stop music")
    sound.stop()
