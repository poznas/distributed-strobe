import os

import pygame
from pygame import mixer
from pygame.mixer import SoundType

from util.logger import logger

PLAYBACK_LATENCY = 50  # ms

sound: SoundType


def init_mixer():
    mixer.pre_init(22050, -16, 2, 512)
    mixer.init()
    pygame.init()


def load_audio_file(filename: str):
    init_mixer()

    global sound
    sound = pygame.mixer.Sound(filename)
    sound.set_volume(1.0)

    logger.info(f"▶ audio file loaded [{os.stat(filename).st_size}]: '{filename}'")


def play_music():
    logger.info("▶ play music")
    sound.play()


def stop_music():
    logger.info("❌ stop music")
    sound.stop()




# load_audio_file(sys.argv[1])
# play_music()
# sleep(100)
