# -*- coding: utf-8 -*-
# @Author: ThinkPositive0x0
# @Email: ThinkPositive0x0@gmail.com
# @Date:   2021-01-22 06:47:48
# @Last Modified by:   ThinkPositive0x0
# @Last Modified time: 2021-01-23 19:14:52

import cv2 as cv
import numpy as np
import os  
import platform
import time
from scipy.optimize import fmin_slsqp
import random
  
def file_name(file_dir,file_type):   
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == file_type:  
                L.append(os.path.join(root, file))  
    return L

def find_all_files(directory,file_type):
    for root, dirs, files in os.walk(directory):
        #yield root
        for file in files:
            if os.path.splitext(file)[1] == file_type: 
                yield os.path.join(root, file)


class CrossMark:
    def __init__(self,centroid,scale,angle=1):
        self.shapes = np.array([[-55,-5],
                    [-55,5],
                    [-5,5],
                    [-5,55],
                    [5,55],
                    [5,5],
                    [55,5],
                    [55,-5],
                    [5,-5],
                    [5,-55],
                    [-5,-55],
                    [-5,-5]])

        self.centroid = centroid
        self.scale = scale
        self.angle = angle

        # Scale shapes to real diameters
        self.shapes = self.shapes * self.scale

        # Rotation shapes
        if self.angle != 0 :
            self.rotate_contour()

        # Translation to some point
        self.shapes = self.shapes + self.centroid

        # Reshape to CV2-images-like array
        self.shapes = self.shapes.reshape((-1,1,2))

        #Round to int not just round down
        self.shapes = np.round(self.shapes)
        self.shapes = self.shapes.astype(np.int32)

        # Transform to cv contour.
        self.contour = cv.approxPolyDP(self.shapes,0,True)

    def cart2pol(self,x, y):
        theta = np.arctan2(y, x)
        rho = np.hypot(x, y)
        return theta, rho


    def pol2cart(self,theta, rho):
        x = rho * np.cos(theta)
        y = rho * np.sin(theta)
        return x, y


    def rotate_contour(self):

        xs, ys = self.shapes[:,0] , self.shapes[:,1]
        thetas, rhos = self.cart2pol(xs, ys)
        
        thetas = np.rad2deg(thetas)
        thetas = (thetas + self.angle) % 360
        thetas = np.deg2rad(thetas)
        
        xs, ys = self.pol2cart(thetas, rhos)
        
        self.shapes[:,0] = xs
        self.shapes[:,1] = ys

    def dist_point_to_contour(self,point):
        distance = cv.pointPolygonTest(self.contour,point,True)
        return distance

def loss_function(parameter,*args):
    x_position = parameter[0]
    y_position = parameter[1]
    scale = args[0]
    position = [x_position,y_position]
    my_contour = CrossMark(position,scale)
    squre_dist = 0
    new_contour = args[1]

    for i in range(len(new_contour)):
        dist = my_contour.dist_point_to_contour(tuple(new_contour[i]))
        squre_dist += dist**2
    return squre_dist

class ShapeAnalysis:
    def __init__(self,file_path):
        self.file_path = file_path
        self.src = cv.imread(file_path)
        self.contour_position = []
        self.img_h = 0
        self.img_w = 0

    def analysis(self):
        h, w, ch = self.src.shape
        print(self.src.shape)
        result = np.zeros((h, w, ch), dtype=np.uint8)
        # 二值化图像
        print("start to detect lines...\n")
        #custom_threshold(self.src)
        #canny_test(self.src)
        self.src = cv.cvtColor(self.src, cv.COLOR_BGR2GRAY)
        # self.src = cv.GaussianBlur(self.src,(5,5),0) #高斯模糊
        self.src = cv.bilateralFilter(self.src,3,38,38) #双边滤波

        binary = self.auto_canny(self.src)
        # cv.imwrite(file_path.replace(".jpg","_binary.jpg"), binary)
        self.img_h = h
        self.img_w = w
        # src_img = cv.imread(self.file_path)
        binary = cv.resize(binary, (0, 0), fx=4, fy=4)
        src_img = cv.resize(cv.imread(self.file_path), (0, 0), fx=4, fy=4)

        #ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
        # contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        # contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_L1)
        # contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL,  cv.CHAIN_APPROX_NONE)

        # Initialize mark vector index.
        index_count = 0 
        # Initialize mark vector.
        new_contour = []
        x_vector = []
        y_vector = []
        w_vector = []
        h_vector = []
        old_x,old_y,old_w,old_h = -3,-3,-3,-3

        for cnt in range(len(contours)):
            # green boundingRect
            x, y, w, h = cv.boundingRect(contours[cnt])
            # 过滤噪点,加权平均
            # if (w > 50) & (h > 50) & (w < 150) & (h<150):
            if (w > 200) & (h > 200) & (w < 600) & (h<600):
                x_vector.append(x)
                y_vector.append(y)
                w_vector.append(w)
                h_vector.append(h)
                new_contour.append(np.squeeze(contours[cnt]))
            else :
                index_count += 1       
        for cnt in range(len(x_vector)):
            # green boundingRect
            x, y, w, h = x_vector[cnt],y_vector[cnt],w_vector[cnt],h_vector[cnt]

            if cnt >0:
                if (abs(old_x - x)<14) & (abs(old_y - y)<14) & (abs(old_w+old_h-w-h)<30):
                    x = round((x+old_x)/2)
                    y = round((y+old_y)/2)
                else:
                    r = (x_vector[cnt]-x_vector[cnt-1])**2 + (y_vector[cnt]-y_vector[cnt-1])**2
                    r = np.around(np.sqrt(r), 2)
                    # print("space: ",str(r))
                    # cv.putText(self.src_img,str(cnt),(x_vector[cnt],y_vector[cnt]),cv.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (100, 200, 200), 2)
            # cv.rectangle(self.src, (x, y), (x+w, y+h), (0,200,0), 1)
            # cv.circle(src_img, (x+round(w/2), y+round(h/2)), 1, (0, 255, 0), 0)
            old_x,old_y,old_w,old_h = x,y,w,h

            parameter = [x+w/2,y+h/2]
            bounds = [(x,x+w),(y,y+h)]
            # args = tuple([0.81686,new_contour[cnt]])
            args = tuple([3.2672,new_contour[cnt]])
            r1, res_fun, res_nit, res_stat, res_message = fmin_slsqp(loss_function,parameter,args=args,iter = 100,bounds = bounds,epsilon=0.6, iprint=0,full_output=1)
            # print('x : '+ str(round(r1[0],4)))
            # print('y:' + str(round(r1[1],4)))
            # print("error: ",res_fun,"\n")

            my_contour_auto = CrossMark([round(r1[0],4),round(r1[1],4)],3.2672)
            cv.drawContours(src_img,my_contour_auto.contour,-1,(25,25,25),2)
            # print(int(round(r1[0])), int(round(r1[1])))
            
            cv.circle(src_img, (int(round(r1[0])), int(round(r1[1]))), 1, (25, 25, 25), 2)

            self.contour_position.append([r1[0]/4,r1[1]/4])


        file_name = self.file_path.split('\\')[-1]
        file_name = file_name.split('.')[0]
        cv.putText(src_img,file_name,(100, 130),cv.FONT_HERSHEY_SCRIPT_COMPLEX, 5, (100, 200, 200), 5)
        cv.drawContours(src_img,new_contour,-1,(0,255,0),1)
        # resize to nomal size
        src_img = cv.resize(src_img, (0, 0), fx=0.25, fy=0.25)
        cv.imwrite(self.file_path+".centered.JPG",src_img)

    def auto_canny(self, image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)

        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv.Canny(image, lower, upper)
        # return the edged image
        return edged

if __name__ == "__main__":
    print('Python Version:' + platform.python_version())
    print('OpenCV Version:' + cv.__version__)
    file_type = '.jpg'
    file_dir = input("Please input file dir.\n")
    file_paths = find_all_files(file_dir,file_type)
    for file_path in file_paths:
        print(file_path)
        ld = ShapeAnalysis(file_path)
        ld.analysis()
        cv.destroyAllWindows()


        