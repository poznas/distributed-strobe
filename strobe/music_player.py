import os
from typing import List

import pygame
from pygame import mixer
from pygame.mixer import SoundType

from util.logger import logger

PLAYBACK_LATENCY = 50  # ms

AUDIO_DIR = 'static/audio'

COUNTDOWN_SEQUENCE = [f"{AUDIO_DIR}/glass-C#6.ogg"] + \
                     ([f"{AUDIO_DIR}/glass-D6.ogg"] * 3) + \
                     [f"{AUDIO_DIR}/glass-D5.ogg"]

countdown_sounds: List[SoundType]
sound: SoundType


def init_mixer():
    mixer.pre_init(22050, -16, 2, 512)
    mixer.init()
    pygame.init()

    global countdown_sounds
    countdown_sounds = [pygame.mixer.Sound(file) for file in COUNTDOWN_SEQUENCE]


def register_countdown(register_task: callable):
    sequence_size = len(COUNTDOWN_SEQUENCE)

    for i in range(sequence_size):
        register_task(i - sequence_size, play_next_countdown_note)


def play_next_countdown_note():
    logger.info(f"▶ countdown: {len(countdown_sounds)}")
    countdown_sounds.pop().play()


def load_audio_file(filename: str):
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
