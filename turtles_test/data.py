import pandas as pd
import numpy as np
import torchvision.transforms as transforms


def get_angle(args):
    if(args is not None and args.angle_range!=360):
        angle = int(np.random.uniform(-args.angle_range,args.angle_range,1))
        if(angle<0):
            angle=360+angle
    else:
        angle = int(np.random.normal(0,100,1))
        angle = angle if(angle>0) else 360-angle
    return angle


import torch
from .utils.coco import COCO
from .utils.progress_bar.bar import Bar
import skimage.io as io
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import pickle
from .utils.bbox_util import *
import cv2
import os
# plt.switch_backend('tkagg')

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

class Data_turtles():
    def __init__(self, dataDir = None, dataType='train2020',
                    experiment_type = '', args = None):
        if(args.filename_test):
            self.data = args.filename_list
            self.args = args
            return

        if(dataDir == None):
            self.dataDir = '../datasets/{}/orientation.{}.coco'.format(args.animal,args.animal)
        else:
            self.dataDir = dataDir
        self.dataType = dataType
        self.annFile='{}/annotations/instances_{}.json'.format(self.dataDir,dataType)
        self.coco=COCO(self.annFile)
        # display COCO categories and supercategories
        cats = self.coco.loadCats(self.coco.getCatIds())
        nms=[cat['name'] for cat in cats]

        # print('\tCOCO categories: \n\t{}'.format(' '.join(nms)))
        # set category as supercategory to get all categories
        # nms = set([cat['supercategory'] for cat in cats])
        # print('\tCOCO supercategories: \n\t{}\n'.format(' '.join(nms)))

        # get all images containing given categories, select one at random
        print(nms)
        self.catIds = self.coco.getCatIds(catNms=nms[min(len(nms)-1,1)]);
        self.imgIds = self.coco.getImgIds(catIds=self.catIds);
        self.args = args
        self.experiment_type = experiment_type
        print("Loading Data: {}".format(dataType))
        self.preprocess_images()

        # need to shuffle if using pickle to load
        # np.random.shuffle(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        resize_to = 224
        if(self.args is not None and self.args.filename_test):
            filename = self.data[index]
            print(filename)
            try:
                image = io.imread('../'+filename,False)
            except FileNotFoundError:
                image = io.imread(filename,False)

            # I_rot = rotate_im(image,-78)
            # plt.imshow(I_rot)
            # plt.show()

            I = transforms.ToPILImage()(image)
            I = transforms.Resize((resize_to,resize_to))(I)
            I = transforms.ToTensor()(I)

            if(self.args.show):
                return I/255,image,filename
            else:
                return I/255
        # preprocess all images
        image, poly, theta = self.data[index]
        # process as each image is loaded
        # image, poly, theta, view = self.get_image(index)
        # view = False

        # print(poly)
        # print(theta)


        angle = get_angle(self.args)

        theta = theta*180/np.pi
        h,w = image.shape[:2]
        cx,cy = w/2,h/2
        frame = np.array([[0,0],
                          [w,0],
                          [w,h],
                          [0,h]])



        mer = self.MER(poly,*image.shape[:2])
        I = rotate_im(image,theta)
        mer_rot = np.round(rotate_box(mer,theta,cx,cy,h,w).reshape((4,2)))
        mir = self.MIR(theta*np.pi/180, mer[2,1]-mer[0,1], mer[1,0]-mer[0,0], self.MER(mer_rot, *I.shape[:2]))
        I = I[mir[0,1]:mir[2,1],mir[0,0]:mir[2,0]]

        # show the stages of cropping the image
        # if( self.args is not None and self.args.show):
            # =============================================
            # original image

            # print(poly)
            # self.ax = plt.gca()
            # self.show_annotation(frame)
            # # self.show_MER(mer)
            # plt.axis('off')
            # plt.imshow(image)
            # plt.show()
            # =============================================
            # rotated image

            # I_rot = rotate_im(image,theta)
            # frame_rot = np.round(rotate_box(frame,theta,cx,cy,h,w).reshape((4,2)))
            # frame_rot_mir = self.MIR(theta*np.pi/180,h,w,frame)
            # self.ax = plt.gca()
            # self.show_MER(frame_rot)
            # self.show_MER(frame_rot_mir)
            # plt.imshow(I_rot)
            # plt.show()
            # # # =============================================
            # # augment image

            # I_aug = rotate_im(I_rot,angle)
            # frame_aug = np.round(rotate_box(frame_rot,angle,cx,cy,h,w).reshape((4,2)))
            # frame_aug_mir = self.MIR((angle+theta)*np.pi/180,h,w,frame)
            # self.ax = plt.gca()
            # self.show_MER(frame_aug)
            # self.show_MER(frame_aug_mir)
            # plt.imshow(I_aug)
            # plt.show()


        # ==============================================
        # augment image
        I_rot = rotate_im(image,angle)
        frame_rot = np.round(rotate_box(frame,angle,cx,cy,h,w).reshape((4,2)))
        frame_rot_mir = self.MIR(angle*np.pi/180,h,w,frame)
        a = -(theta-angle)
        I_crop = I_rot[frame_rot_mir[0,1]:frame_rot_mir[2,1],frame_rot_mir[0,0]:frame_rot_mir[2,0]]

        if(self.args is not None and self.args.show):
            # show augmented image
            self.ax = plt.gca()
            self.show_MER(frame_rot)
            self.show_MER(frame_rot_mir)
            plt.imshow(I_rot)
            plt.show()

            # # orient image
            I_cor = rotate_im(I_rot,a)
            plt.imshow(I_cor)
            plt.show()

            # show cropped image
            plt.imshow(I_crop)
            plt.show()

        if(a>360):
            a = a%360
        if(a<0):
            a = 360+a





        I = transforms.ToPILImage()(I_crop)
        I = transforms.Resize((resize_to,resize_to))(I)
        # I = transforms.functional.affine(I,angle,(0,0),1,0)
        # I = transforms.Grayscale()(I)
        I = transforms.ToTensor()(I)


        image_normalized = I/255#transforms.Normalize(self.means, self.stds)(I)



        if(self.args is not None and self.args.type.startswith('classification')):
            # nCalsses should be a factor of 360
            angle = int(angle/int(360/self.args.nClasses))


        if(self.args is not None and (self.experiment_type=='test' or self.experiment_type=='example')):
            # image = rotate_im(image,theta)
            image = transforms.ToPILImage()(image)
            image = transforms.Resize((resize_to,resize_to))(image)
            # image = transforms.functional.affine(image,angle,(0,0),1,0)
            image = transforms.ToTensor()(image)
            # plt.imshow(image_normalized.permute(1, 2, 0)*255)
            # plt.show()
            if(theta>360):
                theta=theta%360
            if(theta<0):
                theta=360+theta
            return image_normalized, image, theta

        # during training
        return image_normalized, a

    def MIR(self, angle, im_h, im_w, mer):

        new_height = mer[2,1]-mer[0,1]
        new_width = mer[1,0]-mer[0,0]

        # ======================================
        """
        Given a rectangle of size wxh that has been rotated by 'angle' (in
        radians), computes the width and height of the largest possible
        axis-aligned rectangle within the rotated rectangle.
        Source: http://stackoverflow.com/questions/16702966/rotate-image-and-crop-out-black-borders
        """

        quadrant = int(np.floor(angle / (np.pi / 2))) & 3
        sign_alpha = angle if ((quadrant & 1) == 0) else np.pi - angle
        alpha = (sign_alpha % np.pi + np.pi) % np.pi

        bb_w = im_w * np.cos(alpha) + im_h * np.sin(alpha)
        bb_h = im_w * np.sin(alpha) + im_h * np.cos(alpha)

        gamma = np.arctan2(bb_w, bb_w) if (im_w < im_h) else np.arctan2(bb_w, bb_w)

        delta = np.pi - alpha - gamma

        length = im_h if (im_w < im_h) else im_w

        d = length * np.cos(alpha)
        a = d * np.sin(alpha) / np.sin(delta)

        y = a * np.cos(gamma)
        x = y * np.tan(gamma)

        rot_w = bb_w - 2 * x
        rot_h = bb_h - 2 * y
        # ======================================

        # Top-left corner
        top = y + mer[0,1]
        left= x + mer[0,0]

        # Bottom-right corner
        bottom = np.round(top + rot_h)
        right = np.round(left + rot_w)

        return np.array([[left,top],
                        [right,top],
                        [right,bottom],
                        [left,bottom]]).astype(np.int32)

    def MER(self, poly, im_h, im_w):
        left = np.min(poly[:,0])
        right = np.max(poly[:,0])
        top = np.min(poly[:,1])
        bottom = np.max(poly[:,1])

        left = max(left,0)
        right = min(right, im_w)
        top = max(top, 0)
        bottom = min(bottom, im_h)

        return np.array([[left,top],
                        [right,top],
                        [right,bottom],
                        [left,bottom]])

    def show_MER(self, enclosing):
        polygons = [Polygon(enclosing)]
        p = PatchCollection(polygons, facecolor='none', edgecolors=(1,0,0), linewidths=2)
        self.ax.add_collection(p)

    # returns the cropped image and ratio of new h/w to old h/w
    def crop_to_poly(self, poly, im_h, im_w, im_tensor):
        left = round(poly[0,0])
        right = round(poly[1,0])
        top = round(poly[0,1])
        bottom = round(poly[2,1])


        return im_tensor[top:bottom,left:right,:]

    def clip_poly(self,poly, im_h, im_w):

        poly[:,0] = np.where(poly[:,0]>im_w,im_w,poly[:,0])
        poly[:,0] = np.where(poly[:,0]<0,0,poly[:,0])
        poly[:,1] = np.where(poly[:,1]>im_h,im_h,poly[:,1])
        poly[:,1] = np.where(poly[:,1]<0,0,poly[:,1])

        return poly

    def show_annotation(self, poly):
        color = (np.random.random((1, 3))*0.6+0.4).tolist()[0]
        polygons = [Polygon(poly)]
        # inside shading
        p = PatchCollection(polygons, facecolor=color, linewidths=0, alpha=0.4)
        self.ax.add_collection(p)
        # bordering lines
        p = PatchCollection(polygons, facecolor='none', edgecolors=color, linewidths=2)
        self.ax.add_collection(p)

    def test_image(self, image, poly, theta):
        resize_to = 32
        angle = get_angle(self.args)
        theta = theta*180/np.pi
        h,w = image.shape[:2]
        cx,cy = w/2,h/2
        mer = self.MER(poly,*image.shape[:2])
        I = rotate_im(image,theta)
        mer_rot = np.round(rotate_box(mer,theta,cx,cy,h,w).reshape((4,2)))
        mir = self.MIR(theta*np.pi/180, mer[2,1]-mer[0,1], mer[1,0]-mer[0,0], self.MER(mer_rot, *I.shape[:2]))
        I = I[mir[0,1]:mir[2,1],mir[0,0]:mir[2,0]]
        I = transforms.ToPILImage()(I)
        I = transforms.Resize((resize_to,resize_to))(I)
        I = transforms.functional.affine(I,angle,(0,0),1,0)
        I = transforms.ToTensor()(I)
        image_normalized = transforms.Normalize((1,1,1), (.5,.5,.5))(I)
        return True


    def get_image(self, index):
        ID = self.imgIds[index]
        img = self.coco.loadImgs(ID)[0]
        I = io.imread('%s/images/%s/%s'%(self.dataDir,self.dataType,img['file_name']))

        annIds = self.coco.getAnnIds(imgIds=img['id'], catIds=self.catIds, iscrowd=None)
        try:
            turtle_body, animal_head = self.coco.loadAnns(annIds)
        except Exception:
            # print(self.coco.loadAnns(annIds))
            print(len(self.coco.loadAnns(annIds)))
            print("Error loading image")
            exit(1)

        return (I,animal_head['segmentation'],animal_head['theta'])


    def preprocess_images(self):

        # when loading one image at a time
        # if(os.path.isfile("data/loaded_data_{}_means_stds.p".format(self.dataType))):
        #   print("Pickle file found, loading means and stdevs...")
        #   (self.means,self.stds) = pickle.load(open("data/loaded_data_{}_means_stds.p".format(self.dataType), "rb" ))
        #   return

        # when loading whole dataset
        if(os.path.isfile(self.dataDir+"/loaded_data_{}.p".format(self.dataType))):
            print("Pickle file found, loading data...")
            (self.data, self.means,self.stds) = pickle.load(open(self.dataDir+"/loaded_data_{}.p".format(self.dataType), "rb" ))
            print(self.dataType,len(self.data))
            return



        bar = Bar("Preprocessing",max=len(self.imgIds))
        self.data = []

        N = len(self.imgIds)
        means = [0,0,0]
        stds = [0,0,0]
        np.random.shuffle(self.imgIds)
        for i,ID in enumerate(self.imgIds):


            img = self.coco.loadImgs(ID)[0]
            I = io.imread('%s/images/%s/%s'%(self.dataDir,self.dataType,img['file_name']),False)
            # plt.axis('off')

            # for each channel, sum each mean and variance divided by the dataset size
            if(I.shape[-1]==3):
                for channel in range(3):
                    means[channel] += np.mean(I[:,:,channel])/N
                    stds[channel] += np.std(I[:,:,channel])**2/N


            # plt.imshow(I)
            annIds = self.coco.getAnnIds(imgIds=img['id'], catIds=self.catIds, iscrowd=None)
            try:
                if(self.args.animal in ['mantaray','rightwhale'] ):
                    animal_head = self.coco.loadAnns(annIds)[0]
                else:
                    turtle_body, animal_head = self.coco.loadAnns(annIds)
            except Exception:
                print()
                print('# anns found:',len(self.coco.loadAnns(annIds)))
                continue

            poly = animal_head['segmentation']
            poly = np.array(poly).reshape((5,2))
            poly = poly[:-1,:]

            # test to see if augmentation works on image
            # for filtering out pooly annotated images
            try:
                self.test_image(I,poly,animal_head['theta'])#,animal_head['viewpoint'])
            except Exception:
                print("\nskipped",ID)
                continue

            # h,w = I.shape[:2]
            # if(min(np.min(poly),0)<0 or max(np.max(poly[:,0]),w)>w or max(np.max(poly[:,1]),h)>h):
            #   continue
            self.data.append((I,poly,animal_head['theta']))#,animal_head['viewpoint']))
            bar.next()

        print(len(self.data))

        stds = np.sqrt(stds)
        print()

        self.means = means
        self.stds = stds

        print("Saving binary file...")
        # have the option of loading whole dataset or just means and stdevs
        pickle.dump((self.data,means,stds), open(self.dataDir+"/loaded_data_{}.p".format(self.dataType), "wb" ))
        # pickle.dump((means,stds), open(self.dataDir+"/loaded_data_{}_means_stds.p".format(self.dataType), "wb" ))


        print('\nPlease run the command again')
        exit(1)
