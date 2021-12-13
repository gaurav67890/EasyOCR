import glob
import boto3
import cv2
import pathlib
import numpy as np
import pandas as pd
import random
import sys

random.seed(123)

def remove_list(l1,l2):
    l3 = [x for x in l1 if x not in l2]
    return l3

# Amazon Textract client
textract = boto3.client('textract')

imgpath=glob.glob('total_img/*')
random.shuffle(imgpath)
print(imgpath)

val=random.sample(imgpath, int(0.15*len(imgpath)))
traintest=remove_list(imgpath,val)
test=random.sample(traintest, len(val))
train=remove_list(traintest,test)

print(len(imgpath))
print(len(val))
print(len(test))
print(len(train))


modes=['val','test','train']
modes_list=[val,test,train]
b1=0
for mode,impath in zip(modes,modes_list):
    label_data=[]
    pathlib.Path(mode ).mkdir(parents=True, exist_ok=True)
    for documentName in impath:
        img = cv2.imread(documentName)
        h, w = img.shape[:2]
        # Read document content
        with open(documentName, 'rb') as document:
            imageBytes = bytearray(document.read())
        response = textract.detect_document_text(Document={'Bytes': imageBytes})
        # Print detected text
        for e,item in enumerate(response["Blocks"]):
            if item['BlockType']!='LINE':
                continue
            word=item["Text"]
            x1=int(w*item['Geometry']['BoundingBox']['Left'])
            y1=int(h*item['Geometry']['BoundingBox']['Top'])
            wp=int(w*item['Geometry']['BoundingBox']['Width'])
            hp=int(h*item['Geometry']['BoundingBox']['Height'])
            x2=x1+wp
            y2=y1+hp
            imgnew=img.copy()[y1:y2,x1:x2]
            b1=b1+1
            cv2.imwrite(mode+'/'+documentName[:-4].replace('total_img/','')+'_'+str(b1)+'.png',imgnew)
            label_data.append([documentName[:-4].replace('total_img/','')+'_'+str(b1)+'.png',word])
    label_data_csv=np.array(label_data)
    df = pd.DataFrame(label_data_csv, columns=['filename', 'words'])
    df.to_csv(mode+'/'+'labels.csv',index=False)
