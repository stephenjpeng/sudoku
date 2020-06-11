#!/usr/bin/python3

import cv2
import numpy as np
import imgaug as ia
import imgaug.augmenters as iaa
import pickle

def generate_dataset(saveprefix='train', n=5000, use_jpgs=False):
    seq = iaa.Sequential([
        iaa.Crop(percent=(0,0.01), sample_independently=False),
        ])
    
    if use_jpgs:
        numbers = []
        for i in range(1,10):
            im = cv2.imread('%d_nyt.jpg' % i)
            # imresize = cv2.resize(im, (24, 24))
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) / 255
            im = 1 - np.array(im > 0.5, np.uint8)
            numbers += [im]
        labels = np.arange(1, 10)
    else:
        with open('../../test_x.pkl', 'rb') as f:
            numbers = np.array(pickle.load(f))[np.array([3, 4, 5, 25, 24, 27, 7, 9, 18, 21, 1, 11, 2, 8, 6, 14, 0, 10])]
        labels = np.array([9,6,7,1,1,2,8,4,7,4,9,6,2,7,8,5,8,4,5,9,7,1,6,9,3,2,8,3,7,1,9,8,5,3,4,1,8,6])[np.array([3, 4, 5, 25, 24, 27, 7, 9, 18, 21, 1, 11, 2, 8, 6, 14, 0, 10])]
            
    
    train_set = []
    train_labels = []
    for num, label in zip(numbers, labels):
        train_set += [num]
        train_labels += [label]
        for j in range(n // labels.shape[0]):
            shift = np.array((np.random.rand(1, 2)*3), np.uint8)[0]
            aug = np.roll(num, shift)
            train_set += [aug]
            train_labels += [label]

    train_set = seq(images=train_set)
    for i, t in enumerate(train_set):
        train_set[i] = cv2.resize(t, (28, 28))
    cv2.imwrite('check.png', train_set[int(np.random.rand()*len(train_set))]*255)

    #for i, t in enumerate(train_set):
    #    train_set[i] = t.flatten()

    train_set = np.array(train_set)
    train_labels = np.array(train_labels)

    with open('./%s_numbers.pkl' % saveprefix, 'wb') as f:
        pickle.dump(train_set, f)
    with open('./%s_labels.pkl' % saveprefix, 'wb') as f:
        pickle.dump(train_labels, f)

if __name__=='__main__':
    generate_dataset(saveprefix='train', n=2000)
    generate_dataset(saveprefix='val', n=50)#, use_jpgs=True)