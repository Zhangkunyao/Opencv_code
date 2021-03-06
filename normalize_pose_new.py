# -*- coding: utf-8 -*-
import cv2
import time
import numpy as np
import os
from basic_lib import Get_List,get_bbox
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans



# target video_06
target_pose = {}
target_pose['y_min'] = 807.900398
target_pose['y_middle'] = 944.796877
target_pose['y_max'] = 973.400870
target_pose['h_close'] = 853.156591
target_pose['h_far'] = 804.780441
target_pose['bias'] = 103
# source video_27
source_pose = {}
source_pose['y_min'] = 765.709552
source_pose['y_middle'] = 936.218109
source_pose['y_max'] = 979.515083
source_pose['h_close'] = 746.738775
source_pose['h_far'] = 450.751785
source_pose['h_middle'] = 685.977859
source_pose['bias'] = 60.253976997
# video_27 50
# video_06 103
# scale = target_pose['h_far']/source_pose['h_far'] + (source_pose['y_middle'] - source_pose['y_min'])/(source_pose['y_max'] - source_pose['y_min'])*(target_pose['h_close']/source_pose['h_close'] - target_pose['h_far']/source_pose['h_far'])
scale = (target_pose['h_far']/source_pose['h_far'] + target_pose['h_close']/source_pose['h_close'])/2

target_path   = "/home/kun/Documents/DataSet/video_06/pose"
source_path = "/media/kun/Dataset/Pose/DataSet/new_data/video_32/pose"
save_path = "/media/kun/Dataset/Pose/DataSet/new_data/0001/normal_pose"

_,source_imgs = Get_List(source_path)
source_imgs.sort()
_,target_imgs = Get_List(target_path)
target_imgs.sort()

tmp = os.path.join(source_path,source_imgs[0])
source_pose_img = cv2.imread(tmp)
tmp = os.path.join(target_path,target_imgs[0])
target_pose_img = cv2.imread(tmp)
target_shape = target_pose_img.shape
source_shape = source_pose_img.shape

# point_loc = []
# for i,pose_name in enumerate(source_imgs):
#     tmp = os.path.join(source_path,pose_name)
#     source_pose_img = cv2.imread(tmp)
#     point = get_bbox(source_pose_img)
#
#     pose_roi = source_pose_img[point['ymin']:point['ymax'], point['xmin']:point['xmax'], ...]
#     pose_roi = cv2.resize(pose_roi, (int(scale*(point['xmax']-point['xmin'])),
#                                      int(scale * (point['ymax'] - point['ymin']))),
#                           interpolation=cv2.INTER_CUBIC)
#
#     if (point['ymax']-source_pose['bias']) <= source_pose['y_middle']:
#         y_pose = target_pose['y_min'] + (target_pose['y_middle'] - target_pose['y_min']) / \
#              (source_pose['y_middle'] - source_pose['y_min']) * (point['ymax']-source_pose['bias'] - source_pose['y_min'])
#     else:
#         y_pose = target_pose['y_middle'] + (target_pose['y_max'] - target_pose['y_middle']) / \
#              (source_pose['y_max'] - source_pose['y_middle']) * (point['ymax']-source_pose['bias'] - source_pose['y_middle'])
#     # y_pose = bias = target_pose['y_min'] + (source_pose['y_middle'] - source_pose['y_min']) / \
#     #      (source_pose['y_max'] - source_pose['y_min']) * (target_pose['y_max'] - target_pose['y_min'])-(point['ymax'] - 50)
#
#     y_pose = int(y_pose + target_pose['bias'])
#
#     x_pose = int(point['xmin']/source_shape[1]*target_shape[1])
#     result = np.zeros(target_shape)
#
#     xmin = x_pose
#     ymin = max(y_pose - pose_roi.shape[0],0)
#     xmax = min(xmin + pose_roi.shape[1],target_shape[1])
#     ymax = min(y_pose,target_shape[0])
#
#     result[ymin:ymax,xmin:xmax,...] = pose_roi[pose_roi.shape[0]-(ymax - ymin):pose_roi.shape[0],
#                                       pose_roi.shape[1] - (xmax-xmin):pose_roi.shape[1],...]
#     cv2.imwrite(os.path.join(save_path, pose_name), result)
#     print(i/len(source_imgs))

y_loc = []
for i,pose_name in enumerate(source_imgs):
    tmp = os.path.join(source_path,pose_name)
    source_pose_img = cv2.imread(tmp)
    point = get_bbox(source_pose_img)
    a = point['ymax']
    b = source_pose['y_min']
    if a > b:
        y_loc.append(a)
    print(i / len(source_imgs))

consit = np.array([10 for i in range(len(y_loc))])
y_loc = np.array(y_loc)
point_loc = np.array([consit,y_loc])
point_loc = np.transpose(point_loc)
kmeans_cell = KMeans(n_clusters=3, random_state=9)
y_pred = kmeans_cell.fit_predict(point_loc)
plt.scatter(consit, y_loc, c=y_pred)
plt.show()
print(kmeans_cell.cluster_centers_)