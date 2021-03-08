# -*- coding: utf-8 -*-
# @Author: ThinkPositive0x0
# @Email: ThinkPositive0x0@gmail.com
# @Date:   2021-01-22 07:32:12
# @Last Modified by:   ThinkPositive0x0
# @Last Modified time: 2021-01-28 15:31:59

import platform
import cv2 as cv
import numpy as np
from modules.name_parse import NameParse
from modules.find_center import ShapeAnalysis
import pya
import os
import json

class CalculateMatrix():
    '''
        Default file type is jpg.
        Defaul marks layout is 4x3. So landmarks layout is 120um x 80um.
    '''
    def __init__(self,directory,file_type=".jpg"):
        self.top_lefts = []
        self.top_rights = []
        self.down_lefts = []
        self.down_rights = []
        self.Trans_matrix = []
        self.path = directory
        self.img_h = 0
        self.img_w = 0

        my_name = NameParse(directory,file_type)

        my_name.find_all_files()

        my_name.get_coordinate()

        self.file_paths = my_name.file_paths

        file_name_index = 0
        for file_path in my_name.file_paths:
            print(file_path)
            ld = ShapeAnalysis(file_path)
            ld.analysis()
            positions = np.array(ld.contour_position)
            average_position = []
            sum_position = []
            for i in range(int(len(positions)/2)):
                average_position.append((positions[2*i]+positions[2*i+1])/2)
                sum_position.append(np.sum((positions[2*i]+positions[2*i+1])/2))

            self.img_h = ld.img_h
            self.img_w = ld.img_w

            min_position = average_position[np.argmin(sum_position)]
            max_position = average_position[np.argmax(sum_position)]

            # Search the corner mark of the picture
            average_position = np.array(average_position)
            x_index = np.lexsort(average_position[:,::-1].T)
            x_min_index = x_index[:2] # compare 2 min x marks
            x_max_index = x_index[-2:] # compare 2 max x marks
            judge_y_max=[]
            judge_y_min=[]
            for i in x_min_index:
                judge_y_max.append(average_position[i])
            for i in x_max_index:
                judge_y_min.append(average_position[i])

            judge_y_max = np.array(judge_y_max)
            judge_y_min = np.array(judge_y_min)

            y_max_idx = judge_y_max[np.lexsort(judge_y_max.T)]
            down_left = y_max_idx[-1]
            y_min_idx = judge_y_min[np.lexsort(judge_y_min.T)]
            top_right = y_min_idx[0]

            self.top_lefts = min_position
            self.top_rights = top_right
            self.down_lefts = down_left
            self.down_rights = max_position

            self.pixel_trans_to_klayot_like()

            print("top_left: ",self.top_lefts)
            print("top_right: ",self.top_rights)
            print("down_left: ",self.down_lefts)
            print("down_right: ",self.down_rights)

            # Landmarks image (in pixel coordinates)
            landmarks_img = [
                  pya.DPoint(self.top_lefts[0],self.top_lefts[1]),
                  pya.DPoint(self.top_rights[0],self.top_rights[1]),
                  pya.DPoint(self.down_lefts[0],self.down_lefts[1]),
                  pya.DPoint(self.down_rights[0],self.down_rights[1])
                ]

            # Landmarks layout (in micrometers)
            mark_x_dl = my_name.axis_x[file_name_index]*400
            mark_y_dl = my_name.axis_y[file_name_index]*400
            file_name_index +=1

            # Landmarks layout x:120um y:80um
            landmarks_layout = [
              pya.DPoint(mark_x_dl, mark_y_dl+80),
              pya.DPoint(mark_x_dl+120, mark_y_dl+80),
              pya.DPoint(mark_x_dl, mark_y_dl),
              pya.DPoint(mark_x_dl+120,mark_y_dl )
            ]
            # Calculate transform matrix
            matrix = pya.Matrix3d()
            matrix.adjust(landmarks_img, landmarks_layout, pya.Matrix3d.AdjustAll, -1)
            print(matrix)

            self.Trans_matrix.append(matrix)
            

    def pixel_trans_to_klayot_like(self):

        # inverse y
        self.top_lefts = np.array(self.top_lefts) * np.array([1,-1])
        self.top_rights = np.array(self.top_rights) * np.array([1,-1])
        self.down_lefts = np.array(self.down_lefts) * np.array([1,-1])
        self.down_rights = np.array(self.down_rights) * np.array([1,-1])
        
        dim = np.array([-1*self.img_w/2,self.img_h/2])
        print("dim: ",dim)
        # offset zero (In opencV top left is zero but in klayout is the center of picture)
        self.top_lefts = self.top_lefts + dim
        self.top_rights = self.top_rights + dim
        self.down_lefts = self.down_lefts + dim
        self.down_rights = self.down_rights + dim

    def save(self):

        savefile = SaveJson()
        item = []
        for i in range(len(self.file_paths)):
            item.append({
            "file_path" : self.file_paths[i],
            "Trans_matrix" : str(self.Trans_matrix[i])
            })

        matrix_information = {
        "info": item
        }
        
        savefile.save_file(self.path+"\\matrix.json",matrix_information)

class SaveJson(object):

    def save_file(self, path, item):
        # Change python dict to json string. (set indent to auto indent)
        item = json.dumps(item,indent=4)
        try:
            if not os.path.exists(path):
                with open(path, "w", encoding='utf-8') as f:
                    f.write(item + "\n")
                    print("^_^ write success")
            else:
                with open(path, "w", encoding='utf-8') as f:
                    f.write(item + "\n")
                    print("^_^ write success")
        except Exception as e:
            print("write error==>", e)


if __name__ == "__main__":

    print('Python Version:' + platform.python_version())
    print('OpenCV Version:' + cv.__version__)

    file_type = '.jpg'
    # file_dir = "images"
    file_dir = "F:\\My_Research\\InAs_Nanowires_IOS\\0_Fabrication_Steps\\0_EBL_Design\\2021_1_28\\Optical_Images\\InAs_S10_auto"
    find_matrix = CalculateMatrix(file_dir,file_type)
    print("\n\n\n")
    find_matrix.save()
    # print(find_matrix.Trans_matrix)
