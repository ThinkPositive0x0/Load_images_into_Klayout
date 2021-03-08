# -*- coding: utf-8 -*-
# @Author: ThinkPositive0x0
# @Email: ThinkPositive0x0@gmail.com
# @Date:   2021-01-22 06:50:28
# @Last Modified by:   ThinkPositive0x0
# @Last Modified time: 2021-01-24 22:39:54

import numpy as np
import os  
import re

class NameParse:
    def __init__(self,directory,file_type=".jpg"):
        self.directory = directory
        self.file_type =file_type
        self.file_paths = []
        self.files = []
        self.axis_x = []
        self.axis_y = []
        # name norm rule
        self.name_rule = re.compile(r'[(](.*?)[)]', re.S)

    def find_all_files(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if os.path.splitext(file)[1] == self.file_type: 
                    self.file_paths.append(os.path.join(root, file))
                    self.files.append(file)
                    # print(os.path.join(root, file))


    def get_coordinate(self,scale = 10):
        '''
        Scale means big mark space divide small mark space.
        '''
        if not self.files:
            self.find_all_files()
        else:
            pass
        for file in self.files:
            file_name = file.split('_')[2]
            axis = file_name.split('.')[0]
            axis = re.findall(self.name_rule, axis)
            bigx = axis[0].split(',')[0]
            bigy = axis[0].split(',')[1]
            smallx = axis[1].split(',')[0]
            smally = axis[1].split(',')[1]
            self.axis_x.append(int(bigx) + int(smallx)/scale) 
            self.axis_y.append(int(bigy) + int(smally)/scale)


if __name__ == "__main__":

    file_type = '.jpg'
    file_dir = "C:\\Users\\dell\\Desktop\\add_images_into_gds_files\\images"

    my_name = NameParse(file_dir,file_type)

    my_name.find_all_files()

    my_name.get_coordinate()

    print(my_name.files,my_name.axis_x,my_name.axis_y)