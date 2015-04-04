# -*- coding: UTF-8 -*-

"""
    Main game class for Gravity Slingshot game.
    Copyright (C) 2014 Michał Nieznański

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

from level_tools import *
import sys

def help():
    print("""
self.load_run(path_to_gsl_file) - play levels
"""
    )

class Game(Scene):
    def __init__(self):
        self.window = Window()
        self.channel=pygame.mixer.find_channel()
        self.load_display()
        self.images = {}
        self.running = False
        self.add_image_dir("images")
        self.levels = listdir("levels")
        self.levels = [level for level in self.levels if level[0] !='.']
        self.level_info =["N/A", "N/A", "N/A"]
        self.level_index = 0
        self.level_outcome = None
        fill_save_dir()
        self.saves = listdir("saves")
        self.saves = [save for save in self.saves if save[0] != '.']
        self.saves = proper_sort(self.saves)
        self.current_scenes = []
        self.current_song = -1
        self.error_message=""
        if self.saves != []:
            self.level_info = load_save(self.saves[self.level_index])
    def save_display(self, size = None, fullscreen = None, fps = None):
        if size == None:
            size = self.window.modes[self.window.mode_index]
        if fullscreen == None:
            fullscreen=self.window.fullscreen
        if fps == None:
            fps = self.window.fps
        if not "display.cfg" in listdir("config"):
            size = pygame.display.list_modes()[-1]
            fullscreen = False
            
        disp = open("config/display.cfg", 'w')
        disp.write("%r\n%r\n%r\n%r" % (size, fullscreen, fps, self.channel.get_volume()) )
        disp.close()
    def load_display(self):
        if not "display.cfg" in listdir("config"):
            self.save_display()
        disp = open("config/display.cfg")
        self.window.size = eval(disp.readline().strip())
        self.window.fullscreen = eval(disp.readline().strip())
        self.window.fps = eval(disp.readline().strip())
        self.channel.set_volume(eval(disp.readline().strip()))
        disp.close()
    def add_to_game(self, level):
        loaded_level = load_level(level)
        if type(loaded_level) != Scene:
            print(loaded_level)
        loaded_level.game = self
        loaded_level.window = self.window
        return loaded_level
    def redraw_all_scenes(self):
        for scene in self.current_scenes:
            for layer in scene.render_layers:
                for obj in layer:
                    obj.scale_images()
    def run_scene(self, scene):
        if scene != None:
            scene.run()
    def load_run(self, level):
        scene = self.add_to_game(level)
        self.current_scenes.append(scene)
        scene.run()
        self.current_scenes.remove(scene)
        self.redraw_all_scenes()
    def change_level(self, amount):
        self.level_index = (self.level_index+amount)%len(self.levels)
        self.level_info = load_save(self.saves[self.level_index])
        for scene in self.current_scenes:
            scene.generate_text()
        self.redraw_all_scenes()
    def play_level(self):
        level_name = self.saves[self.level_index][:self.saves[self.level_index].find(".")]
        if level_name+"_brief.gsl" in listdir("briefing"):
            brief = self.add_to_game("briefing/"+level_name+"_brief.gsl")
            brief.run()
        level = self.add_to_game("levels/"+self.saves[self.level_index][:self.saves[self.level_index].find(".")]+".gsl")
        self.current_scenes.append(level)
        outcome = level.run()
        self.current_scenes.remove(level)
        if self.level_info[2] != "Success": 
            if outcome[0] == 2:
                self.level_info[2] = "Fail"
            elif outcome[0] == 1:
                self.level_info[2] = "Success"
            else:
                self.level_info[2] = "Abandon"
            self.level_info[1] = str(outcome[1])
        elif self.level_info[2] == "Success":
            if eval(self.level_info[1]) > outcome[1]:
                self.level_info[1] = str(outcome[1])
        overwrite_save(self.saves[self.level_index],self.level_info)
        if outcome[0] == 2:
            self.load_run("menus/fail.gsl")
        elif outcome[0] == 1:
            self.load_run("menus/success.gsl")
        self.redraw_all_scenes()
    def error(self, text=None):
        if text != None:
            self.error_message=text
        self.load_run("menus/error.gsl")
    def custom_action(self):
        if not sys.stdout.isatty():
            self.error("Error: Not run from tty")
        elif self.window.fullscreen:
            self.error("Error: Can't access from fullscreen")
        else:
            action = raw_input("Enter action:\n>>>")
            exec(action)
            return 0
    def play_sound(self, path):
        sound = pygame.mixer.Sound(path)
        sound.play()
    def queue_song(self,path):
        sound = pygame.mixer.Sound(path)
        print("Sound queued:", path)
        self.channel.queue(sound)
    def next_song(self):
        directory = "music/loop"
        songs = listdir(directory)
        songs = [song for song in songs if song[0] != '.']
        songs = proper_sort(songs)
        if len(songs) != 0:
            self.current_song = (self.current_song + 1) % len(songs)
            s=pygame.mixer.Sound(join(directory, songs[self.current_song]))
            self.channel.queue(s)
    def handle_music(self):
        if not self.channel.get_busy():
            self.next_song()

    def run(self):
        self.load_run("menus/logo.gsl")
        self.load_run("menus/main_menu.gsl")

