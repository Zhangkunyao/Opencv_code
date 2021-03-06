# coding=utf-8
import random
import os
import cv2
from basic_lib import Get_List,ImageToIUV,IUVToImage
import numpy as np
import matplotlib.pyplot as plt
'''
先统计test的时候pose查找之间的差距是多少，然后按照这个差距去在训练数据上面贴图
'''

# 剪切图片生成video 为openpose做准备
def img_process(img,loadsize):
    try :
        h, w ,_= img.shape
    except:
        print("hah")
    result = np.zeros((loadsize,loadsize,3))
    if h >= w:
        w = int(w*loadsize/h)
        h = loadsize
        img = cv2.resize(img,(w,h),interpolation=cv2.INTER_CUBIC)
        bias = int((loadsize - w)/2)
        img = np.array(img)
        result[0:h,bias:bias+w,...] = img[0:h,0:w,...]
    if w > h:
        h = int(h * loadsize / w)
        w = loadsize
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_CUBIC)
        bias = int((loadsize - h)/2)
        img = np.array(img)
        result[bias:bias+h,0:w,...] = img[0:h,0:w,...]
    result = result.astype(np.uint8)
    return result

def txt_read(file_path):
    file = open(file_path, 'r')
    listall = file.readlines()
    listall = [i.rstrip('\n').split('\t')[:-1] for i in listall]
    for i in range(len(listall)):
        for j in range(len(listall[i])):
            listall[i][j] = int(listall[i][j])
    file.close()
    return listall

def Mulit_ImageToIUV(im_all,IUV_all):
    TextureIm = np.zeros([24, 200, 200, 3]).astype(np.uint8)
    TextureIm_tmp = np.zeros([24, 200, 200, 3]).astype(np.uint8)
    for im,IUV in zip(im_all,IUV_all):
        U = IUV[:,:,1]
        V = IUV[:,:,2]
        I = IUV[:,:,0]
        ###
        for PartInd in range(1,25):    ## Set to xrange(1,23) to ignore the face part.
            x,y = np.where(I==PartInd)
            u_current_points = U[x,y]   #  Pixels that belong to this specific part.
            v_current_points = V[x,y]
            v_tmp = ((255 - v_current_points) * 199. / 255.).astype(int)
            u_tmp = (u_current_points * 199. / 255.).astype(int)
            TextureIm_tmp[PartInd - 1,v_tmp,u_tmp,...] = im[x, y,...]
        for PartInd in range(1,25):
            x, y = np.where((TextureIm[PartInd - 1,:,:, 0] + TextureIm[PartInd - 1,:,:,2]) == 0)
            TextureIm[PartInd - 1,x, y, ...] = TextureIm_tmp[PartInd - 1,x, y, ...]
        TextureIm_tmp = TextureIm_tmp*0
    generated_image = np.zeros((1200, 800, 3)).astype(np.uint8)
    for i in range(4):
        for j in range(6):
            generated_image[(200 * j):(200 * j + 200), (200 * i):(200 * i + 200),...] = TextureIm[(6 * i + j),...]
    return generated_image

def refresh_IUV(img_path,dense_path):
    im_all = []
    IUV_all = []
    for img,dense in zip(img_path,dense_path):
        im_all.append(cv2.imread(img))
        IUV_all.append(cv2.imread(dense))
    IUV_map_new = Mulit_ImageToIUV(im_all,IUV_all)
    return IUV_map_new

def get_index(body_loc_all,find_body,delt):
    if sum(find_body) == 0:
        return -1
    dist_all = []
    for i in body_loc_all:
        if sum(i) == 0:
            dist = 1000000
        else:
            dist = 0
        for j in range(len(i)):
            dist += abs(find_body[j] - i[j])
        dist_all.append(dist)
    tmp = dist_all.copy()
    tmp.sort()
    for data in tmp:
        if data>delt:
            index = dist_all.index(min(dist_all))
            return index
    return -1

def generate_all_texture(root):
    pose_root = os.path.join(root,'org')
    img_root = os.path.join(root, 'img')
    _, name_pose_all = Get_List(pose_root)
    _, name_img_all = Get_List(img_root)
    name_pose_all.sort()
    name_img_all.sort()
    all = []
    for index in range(len(name_img_all)):
        tmp = os.path.join(img_root,name_img_all[index])
        tmp_1 = os.path.join(pose_root, name_pose_all[index])
        all.append([tmp,tmp_1])
    return all
# init
basic_img = './video/video_06.png'
basic_pose = './video/video_06_IUV.png'
basic_IUV = ImageToIUV(cv2.imread(basic_img),cv2.imread(basic_pose))
IUV_map = ImageToIUV(cv2.imread(basic_img),cv2.imread(basic_pose))
texture_root = '/media/kun/Dataset/Pose/DataSet/new_data/video_06/DensePoseProcess/'
texture_root_all = generate_all_texture(texture_root)

generate_root = '/media/kun/Dataset/Pose/DataSet/new_data/video_06/DensePoseProcess/'
generate_pose_root = os.path.join(generate_root,'org')
_,generate_pose_all = Get_List(generate_pose_root)
generate_pose_all.sort()

texture_file_path = os.path.join(texture_root,'body_loc.txt')
generate_file_path = os.path.join(generate_root,'body_loc.txt')

generate_body_loc = txt_read(generate_file_path)
texture_body_loc = txt_read(texture_file_path)

# #
# fps = 30
# img_size = (1152, 1152)
# fourcc = cv2.VideoWriter_fourcc(*'MJPG')
# video_path = 'video_refresh_all_train.avi'
# videoWriter = cv2.VideoWriter(video_path, fourcc, fps, img_size)

# plan A
# 按照这个指标开始贴图
# bilibili_3 mean=1031.7,std=632.1096
# 机械哥 mean=1085.7,std=618.4771
# 训练数据生成
delt = 0
redio = 0.1
for index,body_loc in enumerate(generate_body_loc):
    source_pose = cv2.imread(os.path.join(generate_pose_root,generate_pose_all[index]))
    find_index = get_index(texture_body_loc, body_loc, delt)
    if find_index == -1:
        source_img = IUVToImage(IUV_map,source_pose)
    else:
        img_path = [texture_root_all[i][0] for i in
                    range(max(find_index - 5, 0), min(max(find_index - 5, 0) + 5, len(texture_root_all)))]
        dense_path = [texture_root_all[i][1] for i in
                      range(max(find_index - 5, 0), min(max(find_index - 5, 0) + 5, len(texture_root_all)))]
        IUV_map_new = refresh_IUV(img_path,dense_path)
        source_img = IUVToImage(IUV_map_new, source_pose)
    source_img = img_process(source_img, 1152)
    # videoWriter.write(source_img)
    cv2.imshow('a',source_img)
    cv2.waitKey(1)
    print(index * 1.0 / len(texture_root_all))
# videoWriter.release()




