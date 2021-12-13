import cv2 as cv
import numpy as np
from .util import check_overlap


def blending(src,ofset=8):
    src2 = src.copy()
    src2 = cv.copyMakeBorder(src2, 0, 0, ofset, 0, cv.BORDER_CONSTANT, None, value = 0)
    h,w=src2.shape[:2]
    src2=src2[0:h,0:w-ofset]
    alpha=0.5
    beta = 0.5
    # dst = cv.addWeighted(src, alpha, src2, beta, 20)
    dst=np.minimum(src,src2)

    src3 = src.copy()
    src3 = cv.copyMakeBorder(src3, 0, 0, 0, ofset, cv.BORDER_CONSTANT, None, value = 0)
    h,w=src3.shape[:2]
    src3=src3[0:h,ofset:w]
    dst=np.minimum(dst,src3)
    # dst = cv.addWeighted(dst, 0.7, src2, 0.3, 20)
    return dst

def get_missing_bbox(blend_bboxes,text_box_list):

    for j in range(len(blend_bboxes)-1,-1,-1):
        bbox1=blend_bboxes[j]
        for bbox in text_box_list[0]:
            if check_overlap([bbox[0],bbox[4],bbox[1],bbox[5]],bbox1,thresh=0.2):
                blend_bboxes.pop(j)
                break
    print('bending', blend_bboxes)
    for bbox in blend_bboxes:
        x1=bbox[0]
        x2=bbox[1]
        y1=bbox[2]
        y2=bbox[3]
        text_box_list[0].append([x1,y1,x2,y1,x2,y2,x1,y2])
        
    
    return text_box_list