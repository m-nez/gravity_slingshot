# -*- coding: UTF-8 -*-

"""
    Classes for Gravity Slingshot.
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

import pygame
from time import time, sleep
from os import listdir
from os.path import isfile, join
from copy import deepcopy

class Window:
    def __init__(self):
        self.size = [800, 600]
        self.caption = "Window"
        self.screen = None
        self.refresh_rate = 30
        self.fullscreen = False
        self.modes = pygame.display.list_modes()
        self.mode_index = -3%len(self.modes)
        self.fps = 30

    def set(self):
        pygame.display.set_caption(self.caption)
        flag = 0
        if self.fullscreen:
            flag |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(self.size, flag)
    def set_size(self, new_size):
        self.size = new_size
        self.set()
    def set_caption(self, new_caption):
        self.caption = new_caption
        self.set()
    def flip(self):
        pygame.display.flip()
    def clear_screen(self, color = (0,0,0)):
        self.screen.fill(color)

class Time:
    def __init__(self):
        self.previous_time = time()
        self.current_time = self.previous_time
        self.delta_time = 0.0
        self.timer_run = False
        self.fps = 30
        self.cached_time = 0.0
    def update(self):
        self.previous_time = self.current_time
        self.current_time = time()
        self.delta_time = self.current_time - self.previous_time
        if self.timer_run:
            self.cached_time += self.delta_time
    def timer_start(self):
        self.cached_time = 0.0
        self.timer_run = True
    def timer_stop(self):
        self.timer_run = False
    def timer_resume(self):
        self.timer_run = True
    def wait_frame(self, fps=30):
        dt = time() - self.current_time
        if dt < 1.0/fps:
            sleep(1.0/fps - dt)

class VisibleObject:
    """
    Drawable Object
    """
    def __init__(self):
        self.name = "Name"
        self.location = [0.0, 0.0]
        self.size = [1.0, 1.0]
        self.visible = True
        self.fixed = True
        self.scene = None
        self.image_pack = None
        self.button = None
        """
        Fixed object is rendered in fixed screen coordinates(Upper left corner is self.location).
        Its width and height are percentages of screen size set by self.size variable.
        """
        self.images = []
        self.scaled_images = []
        self.frame = 0
        self.scale = 1.0
        self.render_layer = 0
    def add_to_scene(self, scene):
        scene.visible_objects.append(self)
        self.scene = scene
    def draw(self):
        if self.button != None:
            self.location = self.button.location

        if self.scaled_images != [] and self.visible:
            if self.fixed:
                self.scene.window.screen.blit(self.scaled_images[self.frame],
                        (
                            self.location[0]*self.scene.window.size[0] - self.scaled_images[self.frame].get_width()/2,
                            self.location[1]*self.scene.window.size[1] - self.scaled_images[self.frame].get_height()/2
                            )
                        )
            else:
                self.scene.window.screen.blit(self.scaled_images[self.frame], 
                        (
                            (self.scale * (self.location[0] - self.scene.camera[0])) - self.scaled_images[self.frame].get_width()/2,
                            (self.scale * (self.location[1] - self.scene.camera[1])) - self.scaled_images[self.frame].get_height()/2
                            )
                        )
    def frame_next(self):
        if self.scaled_images != []:
            self.frame = (self.frame + 1) % len(self.images)



    def scale_images2(self):
        self.scaled_images = []
        if self.fixed:
            for img in self.images:
                self.scaled_images.append(
                    pygame.Surface(
                        (
                        int(self.size[0] * self.scene.window.size[0]),
                        int(self.size[1] * self.scene.window.size[1])
                        ), img)
                    )

        else:
            for img in self.images:
                self.scaled_images.append(
                    pygame.Surface(
                        (
                        int(img.get_width()*self.scale*self.size[0]),
                        int(img.get_height()*self.scale*self.size[1])
                        ), img)
                    )



    def scale_images(self):
        self.scaled_images = []
        if self.fixed:
            for img in self.images:
                self.scaled_images.append(
                    pygame.transform.scale(img, (
                        int(self.size[0] * self.scene.window.size[0]),
                        int(self.size[1] * self.scene.window.size[1])
                        )
                        )
                    )

        else:
            for img in self.images:
                self.scaled_images.append(
                    pygame.transform.scale(img, (
                        int(img.get_width()*self.scale*self.size[0]),
                        int(img.get_height()*self.scale*self.size[1])
                        )
                        )
                    )
    def set_images(self, images):
        self.images = images
        self.scale_images()
    def auto_set_images(self):
        if self.image_pack != None:
            self.set_images(self.scene.images[self.image_pack])
    def set_scale(self, new_scale):
        self.scale = new_scale
        self.scale_images()
    def set_size(self, new_size):
        self.size = new_size
        self.scale_images()
    def bind_camera(self):
        self.scene.camera_bound=True
        self.scene.camera_object = self

class TextObject(VisibleObject):
    def __init__(self):
        self.name = "Name"
        self.location = [0.0, 0.0]
        self.size = [1.0, 1.0]
        self.text = "Text"
        self.color = [255,255,255,255]
        self.visible = True
        self.fixed = True
        self.changing = False
        self.bound = False
        self.max_chars = 32
        self.scene = None
        self.button = None
        self.stretch = True
        #True = size[0]; False = size[1]
        #Used for unstretched text
        self.use_width = False
        self.dimension_modifier = 1

        """
        Fixed object is rendered in fixed screen coordinates(Upper left corner is self.location).
        Its width and height are percentages of screen size set by self.size variable.
        """
        fonts = listdir("fonts")
        fonts.sort()  # listdir returns files in arbitrary order
        self.font = pygame.font.Font(join("fonts", fonts[0]), 32)
        self.images = []
        self.scaled_images = []
        self.frame = 0
        self.scale = 1.0
        self.render_layer = 2
    def bind(self, binding):
        try:
            eval(binding)
            self.bound = True
            self.text = binding
        except:
            bound = False
    def add_to_scene(self, scene, binding = None):
        scene.text_objects.append(self)
        self.scene = scene
        if binding != None:
            self.bind(binding)
    def generate_image(self):
        if self.bound:
            self.images = [self.font.render(str(eval(self.text))[:self.max_chars], False, self.color)]
        else:
            self.images = [self.font.render(str(self.text)[:self.max_chars], False, self.color)]
        if not self.stretch:
            w_to_h = self.images[0].get_width()/self.images[0].get_height()
            if self.use_width:
                self.size[1]=self.size[0]/w_to_h*self.dimension_modifier
            else:
                self.size[0]=self.size[1]*w_to_h*self.dimension_modifier
        self.scale_images()
    def auto_set_images(self):
        self.generate_image()
    def set_text(self, new_text):
        self.text = new_text
        self.bound = False
    def draw(self):
        if self.scaled_images == [] or self.changing:
            self.generate_image()
        VisibleObject.draw(self)

class TextWall:
    """
    Text block
    """
    def __init__(self):
        self.size=[1.0,0.1]
        #location of first line
        self.location =[0,0]
        self.text = ""
        self.color=[255,255,255,255]
        self.stretch=False
        self.lines = []
        self.dimension_modifier = 1.0
    def add_to_scene(self,scene):
        texts=self.text.split('\n')
        for i, text in enumerate(texts):
            line = TextObject()
            self.lines.append(line)
            line.add_to_scene(scene)
            line.stretch = self.stretch
            line.text = text
            line.max_chars = len(text)
            line.location = [
                    self.location[0],
                    self.location[1]+self.size[1]*i
                    ]
            line.size=self.size
            line.color=self.color
            line.dimension_modifier = self.dimension_modifier
class Button(VisibleObject):
    def __init__(self):
        self.name = "Name"
        self.location = [0.0, 0.0]
        self.size = [1.0, 1.0]
        self.scene = None
        self.down_action = "print('Click')"
        self.up_action = "None"
        self.vis_obj = VisibleObject()
        self.vis_obj.button = self
        self.clicked = False
        self.slider = None
    def add_to_scene(self, scene):
        scene.button_objects.append(self)
        self.scene = scene
        if self.vis_obj.image_pack != None:
            self.vis_obj.add_to_scene(scene)
    def play_action(self, action):
        exec(action)
    def mouse_over(self, pos):
        if (self.location[0]-self.size[0]/2)*self.scene.window.size[0] < pos[0] and (self.location[0]+self.size[0]/2)*self.scene.window.size[0] > pos[0]:
            if (self.location[1]-self.size[1]/2)*self.scene.window.size[1] < pos[1] and (self.location[1]+self.size[1]/2)*self.scene.window.size[1] > pos[1]:
                return True
        return False
    def draw(self):
        if self.vis_obj.image_pack != None:
            self.vis_obj.draw()

class Slider():
    """
    Slider object can be manipulated using mouse.
    It has a value (1.0 - 0.0) corresponding with its button location.
    """
    def __init__(self):
        self.button = Button()
        self.button.slider = self
        self.button.down_action = "self.slider.active = True"
        self.button.up_action = "self.slider.active = False"
        self.vis_obj = VisibleObject()
        self.vis_obj.slider = self
        self.scene = None
        self.vertical = True
        self.inverse = False
        self.location = [0.0,0.0]
        self.length = 0.5
        self.active = False
        self.value = 0.0
        self.action = "None"
    def add_to_scene(self,scene):
        scene.slider_objects.append(self)
        self.scene = scene
        self.button.add_to_scene(scene)
        self.vis_obj.add_to_scene(scene)
        if self.vertical:
            loc = self.location[1]
        else:
            loc = self.location[0]
        if self.inverse:
            sign = 1
        else:
            sign = -1
        low = loc - (self.length/2.0*sign)
        if self.vertical:
            self.button.location = [
                    self.location[0],
                    low + (sign*self.value*self.length)
                    ]
        else:
            self.button.location = [
                    low + (sign*self.value*self.length),
                    self.location[1]
                    ]

    def update(self):
        m_coord = pygame.mouse.get_pos()
        m_coord = (float(m_coord[0]), float(m_coord[1]))
        if self.vertical:
            coord = m_coord[1] / self.scene.window.size[1]
            loc = self.location[1]
        else:
            coord = m_coord[0] / self.scene.window.size[0]
            loc = self.location[0]
        if self.inverse:
            sign = 1
        else:
            sign = -1
        high = loc + (self.length/2*sign)
        low = loc - (self.length/2*sign)
        val = ((-sign * low) + coord * sign) / self.length
        if val > 1:
            val = 1
        elif val < 0:
            val = 0
        self.value = val

        if self.vertical:
            self.button.location = [
                    self.location[0],
                    low + (sign*val*self.length)
                    ]
        else:
            self.button.location = [
                    low + (sign*val*self.length),
                    self.location[1]
                    ]

        exec(self.action)


class Path(VisibleObject):
    """
    Representation of object's trajectory
    """
    def __init__(self, obj):
        self.name = "Path"
        self.obj = obj
        self.location = [0.0, 0.0]
        self.size = [1.0, 1.0]
        self.visible = True
        self.fixed = False
        self.images = []
        self.scaled_images = []
        self.frame = 0
        self.scale = 1.0
        self.coordinates = []
        self.active = False
        self.wait_time = 0.0
        self.period = 1.0
        self.scene = obj.scene
        self.image_pack = None
        self.render_layer = 1
    def add_coord(self, coord):
        if self.active:
            self.coordinates.append(deepcopy(coord))
    def wait_time_update(self, dt):
        if self.active:
            self.wait_time += dt
            if self.wait_time > self.period:
                self.add_coord(self.obj.location)
                self.wait_time = 0.0
    def clear_coords(self):
        self.coordinates = []
    def draw(self):
        if self.scaled_images != [] and self.visible:
            for coord in self.coordinates:
                self.scene.window.screen.blit(self.scaled_images[self.frame], 
                        (
                            (self.scale * (coord[0] - self.scene.camera[0])) - self.scaled_images[self.frame].get_width()/2,
                            (self.scale * (coord[1] - self.scene.camera[1])) - self.scaled_images[self.frame].get_height()/2
                            )
                        )

class PhysicalObject(VisibleObject):
    """
    Interactive Object
    """
    
    def __init__(self):
        self.name = "Physical Object"
        self.location = [0.0, 0.0]
        self.size = [1.0, 1.0]
        self.visible = True
        self.fixed = False
        self.image_pack = None
        self.button = None
        self.images = []
        self.scaled_images = []
        self.scale = 1.0
        self.frame = 0
        self.radius = 120.0
        self.mass = 1.0
        self.velocity = [0.0, 0.0]
        self.scene = None
        self.path = Path(self)
        self.projectile = False
        self.attractor = False
        self.obstacle = False
        self.attraction = 1.0
        self.affected_by_gravity = False
        self.goal = False
        self.render_layer = 2
    def add_to_scene(self, scene):
        scene.physical_objects.append(self)
        scene.visible_objects.append(self.path)
        self.scene = scene
        self.path.scene = scene
    def update_path(self):
        self.path.add_coord(self.location)
    def accelerate(self, force = [0.0, 0.0], delta_time = 0.0):
        """
        accelerate([force_x, force_y], delta_time)
        """
        self.velocity[0] += force[0] / self.mass * delta_time
        self.velocity[1] += force[1] / self.mass * delta_time

    def apply_velocity(self, delta_time):
        self.location[0] += self.velocity[0] * delta_time
        self.location[1] += self.velocity[1] * delta_time

    def get_vect_to(self, obj):
        """
        get_vect_to([x, y])
        Returns distance to object and normalized vector.
        [distance, [x, y]]
        """
        vect = [
                obj.location[0] - self.location[0],
                obj.location[1] - self.location[1]
                ]
        distance = (vect[0]**2 + vect[1]**2)**0.5
        
        if distance != 0.0:
            return [distance, [vect[0]/distance, vect[1]/distance]]
        else:
            return [0.0, [0.0, 0.0]]

    def collides_sphere(self, physobj):
        """
        collides_sphere(PhysicalObject):
        """
        if self.get_vect_to(physobj)[0] < self.radius + physobj.radius:
            return True
        else:
            return False
    def elastic_collision(self, physobj):
        """
        Don't use! Illogical!
        """
        vect = self.get_vect_to(physobj)
        vel1 = (self.velocity[0]**2+self.velocity[1]**2)**0.5
        vel2 = (physobj.velocity[0]**2+physobj.velocity[1]**2)**0.5
        v1 = ((self.mass - physobj.mass) * vel1 + 2 * physobj.mass * vel2) / (self.mass + physobj.mass)
        v2 = ((physobj.mass - self.mass) * vel1 + 2 * self.mass * vel2) / (self.mass + physobj.mass)
        self.velocity=[-vect[1][0]*v1, -vect[1][1]*v2]
        physobj.velocity = [vect[1][0]*v2,vect[1][1]*v2]
    def apply_gravity(self, physobjs, delta_time):
        """
        Calculates gravitational force and applies it as acceleration.
        """
        x = 0.0
        y = 0.0
        for obj in physobjs:
            vect = self.get_vect_to(obj)
            if vect[0] != 0.0:
                x += obj.mass * obj.attraction * vect[1][0] / vect[0]**2
                y += obj.mass * obj.attraction * vect[1][1] / vect[0]**2

        self.accelerate([x,y], delta_time)

class Scene:
    def __init__(self):
        self.name = "Scene Name"
        self.game = None
        self.physical_objects = []
        self.visible_objects = []
        self.text_objects = []
        self.button_objects = []
        self.slider_objects = []
        self.images = {}
        self.font = None
        self.window = None
        self.time = Time()
        self.scale = 1.0
        self.camera = [0,0]
        self.camera_bound = False
        self.camera_object_index = 0
        self.attraction = 1.0
        self.running = True
        self.animation_period = 0.1
        self.animation_wait_time = 0.0
        self.time_goals = [20.0, 30.0, 50.0]
        self.time_limit = None
        self.projectile_hit = 0
        self.goal_hit = 0
        self.attractor_hit = 0
        self.obstacle_hit = 0
        self.attractor_hit_to_lose = 1
        self.goal_hit_to_win = 1
        self.obstacle_hit_to_lose =1
        self.clear_buffer = True
        self.render_layers = [[],[],[],[],[],[],[],[],[],[]]
        self.start_action="None"
    def assign_to_render_layers(self):
        self.render_layers =[[],[],[],[],[],[],[],[],[],[]]
        for obj in self.physical_objects+self.visible_objects+self.text_objects:
            self.render_layers[obj.render_layer].append(obj)
    def update_camera(self):
        if self.camera_bound:
            self.camera = deepcopy(self.physical_objects[self.camera_object_index % len(self.physical_objects)].location)
            self.camera[0] -= self.window.size[0]/2/self.scale
            self.camera[1] -= self.window.size[1]/2/self.scale

    def move_camera(self, x=0, y=0):
        if not self.camera_bound:
            self.camera[0]+=x
            self.camera[1]+=y
    def end(self):
        self.running = False
    def win(self):
        if self.goal_hit >= self.goal_hit_to_win:
            return True
        else:
            return False
    def loss(self):
        time = False
        if self.time_limit != None:
            if self.time.cached_time > self.time_limit:
                time = True
        if time or self.attractor_hit >= self.attractor_hit_to_lose or self.obstacle_hit >= self.obstacle_hit_to_lose:
            return True
        else:
            return False
    def rate(self):
        rating = 3
        if self.time.cached_time < self.time_goals[0]:
            rating = 0
        elif self.time.cached_time < self.time_goals[1]:
            rating = 1
        elif self.time.cached_time < self.time_goals[2]:
            rating = 2
        return rating
    def outcome(self):
        """
        0 - None
        1 - Win
        2 - Loss
        Returns Win/Loss, time, rating
        """
        if self.loss():
            return [2, self.time.cached_time, self.rate()]
        elif self.win():
            return [1, self.time.cached_time, self.rate()]
        else:
            return [0, self.time.cached_time, 3]
    def check_end(self):
        if self.loss() or self.win():
            self.end()
    def mouse_set(self, pos):
        pos = pos[0]*self.window.size[0], pos[1]*self.window.size[1]
        pygame.mouse.set_pos(pos)
    def add_image_dir(self, directory):
        """
        add_image_dir(image_folder)
        """
        name = directory[directory.rfind("/") + 1:]
        for file in listdir(directory):
            if file[0] != ".":
                if isfile(directory+"/"+file):
                    if not name in self.images:
                        self.images[name] = []
                    self.images[name].append(pygame.image.load(directory+"/"+file))
                else:
                    self.add_image_dir(directory+"/"+file)
    def generate_text(self):
        for obj in self.text_objects:
            obj.generate_image()
    def draw(self, clear = True):
        Dt = DebugTimer()
        if clear:
            self.window.clear_screen()
        #Dt.start()
        for layer in self.render_layers:
            for obj in layer:
                obj.draw()
                #Dt.spst([obj, obj.name])

        self.window.flip()
    def set_scale(self, new_scale):
        self.scale = new_scale
        for obj in self.visible_objects + self.physical_objects + self.text_objects:
            if obj.fixed == False:
                obj.set_scale(self.scale)
    def apply_gravity(self):
        """
        Applies gravity to all objects affected_by_gravity.
        """
        for i in range(len(self.physical_objects)):
            if self.physical_objects[i].affected_by_gravity:
                self.physical_objects[i].apply_gravity(
                        self.physical_objects[:i] + self.physical_objects[i + 1:],
                        self.time.delta_time
                        )
    def apply_velocity(self):
        for obj in self.physical_objects:
            obj.apply_velocity(self.time.delta_time)
    def path_wait_time_update(self):
        for obj in self.physical_objects:
            if obj.path.active:
                obj.path.wait_time_update(self.time.delta_time)
    def get_object_named(self, name):
        all_objs = self.visible_objects + self.physical_objects + self.text_objects
        for obj in all_objs:
            if obj.name == name:
                return obj
    def animate(self):
        self.animation_wait_time += self.time.delta_time
        if self.animation_period < self.animation_wait_time:
            self.animation_wait_time = 0.0
            for obj in self.physical_objects + self.visible_objects:
                obj.frame_next()
    def button_down_action(self, mouse_pos):
        for obj in self.button_objects:
            if obj.mouse_over(mouse_pos):
                obj.play_action(obj.down_action)
                obj.clicked = True
    def button_up_action(self, mouse_pos=(0,0)):
        for obj in self.button_objects:
            if obj.clicked:
                obj.play_action(obj.up_action)
                obj.clicked = False
    def bind_camera(self):
        if self.physical_objects != []:
            self.camera_bound = True
    def toggle_camera(self):
        if self.camera_bound:
            self.camera_bound = False
        else:
            self.bind_camera()
    def change_camera_object(self, amount):
        if self.physical_objects != []:
            self.camera_object_index = (self.camera_object_index + amount) % len(self.physical_objects)
    def change_scale(self, amount, mode="a"):
        old_scale = self.scale
        new_scale = self.scale
        if mode == "a":
            new_scale = self.scale + amount
        elif mode == "m":
            new_scale = self.scale * amount
        if new_scale < 0.05:
            new_scale = 0.05
        elif new_scale > 1.0:
            new_scale = 1.0
        self.set_scale(new_scale)
        self.camera[0] += (1/old_scale-1/new_scale)*self.window.size[0]/2
        self.camera[1] += (1/old_scale-1/new_scale)*self.window.size[1]/2

    def handle_input(self):
        pressed_keys =  pygame.key.get_pressed()
        if pressed_keys[ord("w")]:
            self.move_camera(0,-128*self.time.delta_time/self.scale)
        if pressed_keys[ord("s")]:
            self.move_camera(0,128*self.time.delta_time/self.scale)
        if pressed_keys[ord("a")]:
            self.move_camera(-128*self.time.delta_time/self.scale)
        if pressed_keys[ord("d")]:
            self.move_camera(128*self.time.delta_time/self.scale)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.button_down_action(pygame.mouse.get_pos())

                if event.button == 4:
                    self.change_scale(0.05)
                if event.button == 5:
                    self.change_scale(-0.05)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.button_up_action(pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.end()
                if event.key == pygame.K_q:
                    self.change_camera_object(-1)
                if event.key == pygame.K_e:
                    self.change_camera_object(1)
                if event.key == pygame.K_c:
                    self.toggle_camera()

    def check_sliders(self):
        for slider in self.slider_objects:
            if slider.active:
                slider.update()
    def resolve_collisions(self):
        loop_end_index = len(self.physical_objects)
        objects_to_remove = []
        for i in range(loop_end_index-1):
            obj1 = self.physical_objects[i]
            for j in range(i+1, loop_end_index):
                obj2 = self.physical_objects[j]
                if obj1.collides_sphere(obj2):
                    if obj1.projectile:
                        self.projectile_hit += 1
                    if obj1.attractor:
                        self.attractor_hit += 1
                        objects_to_remove.append(obj1)
                    if obj1.goal:
                        self.goal_hit += 1
                    if obj1.obstacle:
                        self.obstacle_hit += 1
                    if obj2.projectile:
                        self.projectile_hit += 1
                    if obj2.attractor:
                        self.attractor_hit += 1
                        objects_to_remove.append(obj2)
                    if obj2.goal:
                        self.goal_hit += 1
                    if obj2.obstacle:
                        self.obstacle_hit += 1
        for obj in objects_to_remove:
            try:
                self.physical_objects.remove(obj)
                for layer in self.render_layers:
                    if obj in layer:
                        layer.remove(obj)
            except:
                pass
    def change_attraction(self):
        for obj in self.physical_objects:
            if obj.attractor:
                obj.attraction = self.attraction
    def auto_set_images(self):
        for obj in self.visible_objects + self.physical_objects + self.text_objects:
            obj.auto_set_images()
    def run(self):
        self.running = True
        self.images = self.game.images
        self.auto_set_images()
        self.assign_to_render_layers()
        self.set_scale(self.scale)
        self.time.timer_start()
        self.bind_camera()
        exec(self.start_action)
        while self.running:
            self.time.update()
            self.handle_input()
            self.check_sliders()
            self.change_attraction()
            self.apply_gravity()
            self.apply_velocity()
            self.path_wait_time_update()
            self.resolve_collisions()
            self.check_end()
            self.update_camera()
            self.draw(self.clear_buffer)
            self.time.wait_frame(self.window.fps)

        return self.outcome()

class DebugTimer:
    def __init__(self):
        self.bt = 0.0
        self.at = 0.0
        self.running = False
        self.base_size = 13
        self.base = []
        for i in range(self.base_size):
            self.base.append(0.0)
        self.num_samples = 0
    def start(self):
        self.bt = time()
        self.running = False
    def stop(self, mess):
        self.at = time()
        print(mess, self.at - self.bt)
    def spst(self, mess):
        self.at = time()
        print(mess, self.at - self.bt)
        self.bt = time()
    def spst_to_base(self, num):
        self.at = time()
        self.base[num] += self.at - self.bt
        self.bt = time()
    def sample_add(self):
        self.num_samples += 1
    def print_base(self):
        for i in range(self.base_size):
            print(i, self.base[i]/self.num_samples)
    def sum_avg_base(self):
        s = 0.0
        for i in range(self.base_size):
            s += self.base[i]
        s/=self.num_samples
        return s
