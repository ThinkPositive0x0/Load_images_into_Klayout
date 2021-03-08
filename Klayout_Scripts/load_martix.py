# -*- coding: utf-8 -*-
# @Author: ThinkPositive0x0
# @Email: ThinkPositive0x0@gmail.com
# @Date:   2021-01-22 19:28:54
# @Last Modified by:   ThinkPositive0x0
# @Last Modified time: 2021-01-23 19:52:48

import json
import pya
import re
app = pya.Application.instance()
mw = app.main_window()
view = mw.current_view()

matrix_directory = "F:\\My_Research\\InAs_Nanowires_IOS\\0_Fabrication_Steps\\0_EBL_Design\\2021_1_19\\Optical_Images\\InAs_S10_auto"
matrix_path = matrix_directory + "\\matrix.json"

with open(matrix_path,"r") as load_f:
    load_dict = json.load(load_f)

matrix_rule = re.compile(r'[(](.*?)[)]', re.S)
for i in range(len(load_dict["info"])):
    path  = load_dict["info"][i]["file_path"]
    matrix = load_dict["info"][i]["Trans_matrix"]
    matrix = re.findall(matrix_rule, matrix)
    m = [[],[],[]]
    for i in range(len(matrix)):
        matrix_elements = matrix[i].split(",")
        for element in matrix_elements:
            m[i].append(float(element))
    
    add_images = pya.Image(path+".centered.JPG")
    matrix = pya.Matrix3d(m[0][0],m[0][1],m[0][2],m[1][0],m[1][1],m[1][2],m[2][0],m[2][1],m[2][2])
    add_images = add_images.transformed(matrix)

    view.insert_image(add_images)
