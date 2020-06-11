#!/usr/bin/python3
import src.constants as constants
import cv2
import numpy as np
import subprocess

from PIL import Image
import pytesseract


class SudokuDetector():
    def __init__(self, filter=False):
        self.filter = filter
        self.im = None
        self.lines = None

    def grab_image(self):
        subprocess.call(['scrot', '-s', constants.SCROT_PATH])
        self.im = cv2.imread(constants.SCROT_PATH)
        subprocess.call(['rm', '-f', constants.SCROT_PATH])

    def detect_grid(self):
        if self.im is None:
            return False
        else:
            gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray,90,150,apertureSize = 3)
            kernel = np.ones((3,3),np.uint8)
            edges = cv2.dilate(edges,kernel,iterations = 2)
            # cv2.imwrite('canny.jpg',edges)
            kernel = np.ones((7,7),np.uint8)
            edges = cv2.erode(edges,kernel,iterations = 1)
            # cv2.imwrite('canny2.jpg',edges)

            lines = cv2.HoughLines(edges,1,np.pi/90,150)

            if lines is None: 
                print('No lines were found')
                return False

            if self.filter:
                rho_threshold = 15
                theta_threshold = 0.1
                slope_threshold = 5

                # how many lines are similar to a given one
                similar_lines = {i : [] for i in range(len(lines))}
                for i in range(len(lines)):
                    for j in range(len(lines)):
                        if i == j:
                            continue

                        rho_i,theta_i = lines[i][0]
                        rho_j,theta_j = lines[j][0]
                        if abs(rho_i - rho_j) < rho_threshold and abs(theta_i - theta_j) < theta_threshold:
                            similar_lines[i].append(j)

                # ordering the INDECES of the lines by how many are similar to them
                indices = [i for i in range(len(lines))]
                indices.sort(key=lambda x : len(similar_lines[x]))

                # line flags is the base for the filtering
                line_flags = len(lines)*[True]
                for i in range(len(lines) - 1):
                    if not line_flags[indices[i]]: # if we already disregarded the ith element in the ordered list then we don't care (we will not delete anything based on it and we will never reconsider using this line again)
                        continue

                    for j in range(i + 1, len(lines)): # we are only considering those elements that had less similar line
                        if not line_flags[indices[j]]: # and only if we have not disregarded them already
                            continue

                        rho_i,theta_i = lines[indices[i]][0]
                        rho_j,theta_j = lines[indices[j]][0]
                        if abs(rho_i - rho_j) < rho_threshold and abs(theta_i - theta_j) < theta_threshold:
                            line_flags[indices[j]] = False # if it is similar and have not been disregarded yet then drop it now

            # print('number of Hough lines:', len(lines))

            filtered_lines = []
            if filter:
                for i in range(len(lines)): # filtering
                    if line_flags[i]:
                        filtered_lines.append(lines[i])
                # print('Number of filtered lines:', len(filtered_lines))
            else:
                filtered_lines = lines

            line_coords = []
            for line in filtered_lines:
                rho,theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                cv2.line(self.im, (x1, y1), (x2, y2), (0, 0, 255), 2)
                if (np.abs(x1-x2) < slope_threshold) or (np.abs(y1-y2) < slope_threshold):
                    line_coords += [[x1, y1, x2, y2]]

            if len(line_coords) != 20:
                print("%d lines found!" % len(line_coords))
                print(line_coords)
                return False

            self.lines = np.array(line_coords)
            return True

    def extract_numbers(self):
        vertical_lines = self.lines[self.lines[:, 0].argsort()[10:]]
        horizontal_lines = self.lines[self.lines[:, 1].argsort()[:10]]
        to_test = []
        to_save = []
        offset = 6
        for j, vline in enumerate(vertical_lines[:-1]):
            for i, hline in enumerate(horizontal_lines[:-1]):
                digit = self.im[
                    hline[1]+offset:horizontal_lines[i+1][1]-offset,
                    vline[0]+offset:vertical_lines[j+1][0]-offset
                ]
                digit = cv2.cvtColor(digit, cv2.COLOR_BGR2GRAY) / 255
                digit = 1 - np.array(digit > 0.5, np.uint8)
                if np.sum(digit) > constants.CONTENT_CUTOFF:
                    to_save += [digit]
                # digit = cv2.resize(digit, constants.TRAIN_SIZE)
                to_test += [digit]#.flatten()]
        to_test = np.array(to_test)
        def read_images(images):
            for image in images:
                if np.sum(image) < constants.CONTENT_CUTOFF:
                    yield -1
                else:
                    try:
                        val = pytesseract.image_to_string(image,
                            config='--oem 0 --psm 10 -c tessedit_char_whitelist=123456789 -c tessedit_zero_kelvin_rejection=1 -c classify_bln_numeric_mode=1 --tessdata-dir %s' % constants.TESSDATA_DIR,
                            timeout=5.0,
                        )
                        yield int(val) if len(val) else -1
                    except ValueError:
                        yield -1
        # res = np.empty(to_test.shape[0], dtype=np.int8)
        # res = res.reshape(constants.ROWS, constants.COLUMNS).transpose().tolist()
        return read_images(to_test)


if __name__=='__main__':
    detect = SudokuDetector(True)
    detect.grab_image()
    detect.detect_grid()
    detect.extract_numbers()
