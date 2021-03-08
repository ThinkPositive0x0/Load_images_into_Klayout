# -*- coding: utf-8 -*-
# @Author: ThinkPositive0x0
# @Email: ThinkPositive0x0@gmail.com
# @Date:   2021-01-22 19:28:54
# @Last Modified by:   ThinkPositive0x0
# @Last Modified time: 2021-01-23 19:15:35

import json
import pya
import re

with open("C:\\Users\\dell\\Desktop\\add_images_into_gds_files\\images\\matrix.json","r") as load_f:
    load_dict = json.load(load_f)

print()
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
    # matrix m11 m12 m13 m21 m22 m23 m31 m32 m33
    matrix = pya.Matrix3d(m[0][0],m[0][1],m[0][2],m[1][0],m[1][1],m[1][2],m[2][0],m[2][1],m[2][2])
    print(path+".centered.JPG")
    print(type(matrix))
    #add_images = pya.Image(path)