# Import_images_into_Klayout
Import optical or SEM images into Klayout gds files.

## 0. Install the necessary python packages

Install opencv, klayout, scipy and numpy python packages.

```cmd
pip install opencv-python
pip install opencv-contrib-python
pip install klayout
pip install scipy numpy
```


## 1. Find Center of images
Use the python package OpenCV to find the contours of crossmarks in image. The distance between the points on the contour line and our standard crossmark contour is defined as a loss function. The minimization solution of this function with respect to the center position is then obtained via the python scipy package.


## 2. Calculate the transform matrix

[Klayout Standalone Python Module](https://github.com/klayoutmatthias/klayout/wiki/klayout---Standalone-KLayout-Python-Module) porvide a  class Matrix3d that we can use to calculate the transformation matrix of the images we want to import into klayout.

```python
import pya
# Landmarks image (in pixel coordinates)
landmarks_img = [
	pya.DPoint(0,0),
	pya.DPoint(0,100),
	pya.DPoint(100,0),
	pya.DPoint(100,100)
	]
matrix = pya.Matrix3d()
matrix.adjust(landmarks_img, landmarks_layout, pya.Matrix3d.AdjustAll, -1)
```


## 3. Add images into Klayout
Use Klayout macron to add images. In klayout software interface press "F5" to run macron.

```python
import json
import pya
import re
app = pya.Application.instance()
mw = app.main_window()
view = mw.current_view()

matrix_directory = "Replaced this with your File:\\path\to\Images"
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
```
