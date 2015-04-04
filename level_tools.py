# -*- coding: UTF-8 -*-

"""
    Tools for managing levels for Gravity Slingshot game.
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

from classes import *

def load_level(path):
    """
    gravity slingshot level loader
    """
    gsl_file = open(path)
    current_class = None
    current_object = None
    # List of all scene objects names
    objects = {}
    object_list = []
    for line in gsl_file:
        line = line.strip()
        f_char = line[:1]
        if f_char == '>':
            current_class = line[1:]
        elif f_char == '<':
            current_class = None
        elif f_char == '[':
            current_object = line[1:]
            if current_class != None:
                objects[current_object]=eval(current_class+"()")
                object_list.append(objects[current_object])
        elif f_char == ']':
            if current_object == None:
                return  "Error: Unexpected ] No current object"
            else:
                current_object = None
        elif f_char == "-":
            if current_object == None:
                return  "Error: Unexpected - No current object"
            else:
                exec("objects[\""+current_object+"\"]."+line[1:])

    gsl_file.close()
    level_found = False
    for obj in object_list:
        # fix for python2
        if obj.__class__ == Scene:
            level = obj
            level_found = True
    object_list.remove(level)
    if not level_found:
        return "No Scene declared"
    for obj in object_list:
        if type(obj) != Scene:
            obj.add_to_scene(level)
    return level

def overwrite_save(file_name, name_time_comp):
    save = open("saves/"+file_name, "w")
    save.writelines([str(name_time_comp[0])+"\n", str(name_time_comp[1])+"\n", str(name_time_comp[2])])
    save.close()

def fill_save_dir(overwrite=False):
    saves = listdir("saves")
    levels = listdir("levels")
    level=levels[0]
    for level in levels:
        if not level[:level.find(".")]+".gss" in saves or overwrite:
            save = open("saves/"+level[:level.find(".")]+".gss", "w")
            level = open("levels/"+level)
            save.writelines([level.readline(),"No Time Yet\n", "False"])
            save.close()
            level.close()

def load_save(file_name):
    save = open("saves/"+file_name)
    name_time_comp = []
    for line in save:
        name_time_comp.append(line.rstrip())
    save.close()
    return name_time_comp

def proper_sort(unsorted):
    tmp_sort = sorted(unsorted, key = len)
    max_length = tmp_sort[-1]
    min_length = tmp_sort[0]
    start_point = 0

    current_length = len(tmp_sort[0])
    final_sort = [[]]
    fs_iterator = 0
    for i, item in enumerate(tmp_sort):
        if len(item) != current_length:
            current_length = len(item)
            fs_iterator += 1
            final_sort.append([])
        final_sort[fs_iterator].append(item)
    final_merged = []
    for i in final_sort:
        i = sorted(i)
        final_merged.extend(i)
    
    return final_merged
            


