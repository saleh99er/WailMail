import os
from mutagen.mp3 import MP3
import math
import concurrent.futures
import queue
import logging
import threading
import time
from enum import Enum

from WailMail_common import *

class DeterminedOS(Enum):
    UNKNOWN = 1
    RASPBIAN = 2
    WINDOWS = 3
    UBUNTU = 4
    UNSUPPORTED = 5

os_determined = DeterminedOS.UNKNOWN

def determine_os():
    global os_determined
    prev_dir = os.getcwd()
    if(os.name == 'nt'):
        os_determined = DeterminedOS.WINDOWS
        return
    elif(os.name == 'posix'):
        try:
            os.chdir('/')
            os.chdir('proc')
            with open('cpuinfo') as f:
                for line in f:
                    if("Raspberry Pi" in line):
                        os_determined = DeterminedOS.RASPBIAN
                        return
        except:
            os_determined = DeterminedOS.UNSUPPORTED
        finally:
            os.chdir(prev_dir)

        index_uname = str(os.uname()).find("Ubuntu")
        if(index_uname > -1):
            os_determined = DeterminedOS.UBUNTU
    else:
        os_determined = DeterminedOS.UNSUPPORTED


def play_based_on_os(audio_filename):
    if(os_determined == DeterminedOS.UNKNOWN):
        determine_os()

    if(os_determined == DeterminedOS.WINDOWS):
        audio_playback = os.system("start " + audio_filename)
        audio = MP3(audio_filename)
        time.sleep(math.ceil(audio.info.length))

    elif(os_determined == DeterminedOS.RASPBIAN):
        audio_playback = os.system("omxplayer -o both " + audio_filename)

    elif(os_determined == DeterminedOS.UBUNTU):
        audio_playback = os.system("mpg123 " + audio_filename)

    else:
        print("UNSUPPORTED")
        audio_playback = -1
    return audio_playback

def audio_player(audio_queue, end_event, logging, check_freq=1):
    os.chdir('static')
    os.chdir('audio')
    while(not end_event.is_set()):
        while(not audio_queue.empty()):
            audio_filename = get_from_queue(audio_queue, end_event)
            logging.info("AC:: got " + audio_filename)
            if audio_filename is not None:
                audio_playback = play_based_on_os(audio_filename)
                logging.info("AC::" + audio_filename + " return code:" + str(audio_playback))
            time.sleep(check_freq)
