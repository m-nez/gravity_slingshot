# -*- coding: UTF-8 -*-

"""
    Music channel for Gravity Slingshot.
    Copyright (C) 2016 Michał Nieznański

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from threading import Thread, Lock
from os import listdir
from os.path import join
from time import sleep
import pygame

class Channel(Thread):
    def __init__(self, songs):
        Thread.__init__(self)
        self.setDaemon(True)
        self.volume_lock = Lock()
        self.songs_dir = songs
        self.songs = sorted(s for s in listdir(songs) if s[0] != ".")
        self.current_song = 0
        self.channel=pygame.mixer.find_channel()
    def next_song(self):
        if len(self.songs) != 0:
            self.current_song = (self.current_song + 1) % len(self.songs)
            s=pygame.mixer.Sound(join(self.songs_dir, self.songs[self.current_song]))
            self.channel.queue(s)
    def run(self):
        while True:
            if not self.channel.get_busy():
                self.next_song()
            sleep(0.5)
    def set_volume(self, v):
        with self.volume_lock:
            self.channel.set_volume(v)
    def get_volume(self):
        return self.channel.get_volume()
