import numpy as np 
import pytesseract
from .util import check_overlap,get_area,correct_bboxes

def ocr_text_from_page(img):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(img, lang='deu', config='--psm 6', output_type='dict')
    left = data['left']
    top = data['top']
    width = data['width']
    height = data['height']

    blocks=[]
    for text,left,top,width,height in zip (data['text'],data['left'],data['top'], data['width'], data['height']):
        if text=='':
            continue 
        if (width <10  or height <10 ) and (max(width,height)/min(width,height) >10):
            continue  
        blocks.append(np.asarray([left,left+width,int(top-0.1*height),int(top+height +0.1*height)],dtype=np.int32))

    return blocks

def  filter_by_tenssract(img,bboxes):
    blocks_tens=ocr_text_from_page(img)
    get_block=[]
    remove_bbox=[]

    for k,block in enumerate(blocks_tens):
        h_block= block[3]-block[2]
        inter_block_num=[]
        for m in range(len(bboxes[0])):
            bbox=bboxes[0][m]
            h_bbox=bbox[3]-bbox[2]

            if check_overlap(block,bboxes[0][m],thresh=0.7):
                if abs(h_block-h_bbox)/max(h_block,h_bbox) <0.27:
                    inter_block_num.append(m)
        
        if len(inter_block_num) >1:
            get_block.append(block)
            remove_bbox.extend(inter_block_num)

    remove_bbox = sorted(remove_bbox, key=lambda id:id,reverse=True)

    for rm in remove_bbox:
        bboxes[0].pop(rm)

    for bbox in get_block:
        bboxes[0].append(bbox)

    print('remove_bbox',remove_bbox)
    print('get_block_tensor',get_block)

    bboxes=split_large_bbox(bboxes,blocks_tens)
    bboxes[0]=correct_bboxes(bboxes[0])
    return bboxes

def check_subline(line_box,sub_inter):
    adding_bbox=[]
    w_line = abs(line_box[1] -line_box[0])
    sub_inter = sorted(sub_inter, key=lambda bbox:bbox[0])
    sub_inter.append([line_box[1],line_box[1]+10,line_box[2],line_box[3]])
    start_bbox=line_box
    for i in range(len(sub_inter)-1):
        end_bbox= sub_inter[i]
        if start_bbox[0] - end_bbox[0] >10 :
            continue 

        if (end_bbox[0] -start_bbox[0])/ w_line >0.3:
            adding_bbox.append([start_bbox[0],end_bbox[0],line_box[2],line_box[3]])

        start_bbox=[start_bbox[1],None,None,None]
    return adding_bbox

def recheck_block(block,inter_bboxes):

    h_block= block[3]-block[2]
    h_min =int(np.mean([(bbox[3]-bbox[2]) for bbox in inter_bboxes]))

    LINE_NUM=int(np.floor(h_block/h_min+ 0.5))
    adding_bbox=[]
    for line in range(LINE_NUM):
        #format x1x2y1y2 
        if LINE_NUM ==1:
            line_box=block
            sub_inter = inter_bboxes   
        else:
            line_box=[block[0],block[1],block[2] +line*h_min-3 ,block[2] +(line+1)*h_min +3]
            sub_inter = [bbox for bbox in inter_bboxes if check_overlap(line_box,bbox,0.7)]
        adding_bbox.extend(check_subline(line_box,sub_inter))      
    return adding_bbox
            
        

def split_large_bbox(craft_blocks,ten_bboxes):
    get_block=[]
    remove_bbox=[]
    for k,block in enumerate(craft_blocks[0]):
        # h_block= block[3]-block[2]
        inter_block_num=[]
        for m in range(len(ten_bboxes)):
            bbox=ten_bboxes[m]
            # h_bbox=bbox[3]-bbox[2]
            if check_overlap(block,ten_bboxes[m],thresh=0.7) and get_area(block) > get_area(ten_bboxes[m]):
                # if abs(h_block-h_bbox)/max(h_block,h_bbox) <0.27:
                    inter_block_num.append(bbox)
        
        if len(inter_block_num) >1:
            get_block.extend(inter_block_num)
            remove_bbox.append(k)

            # recheck block
            reject_bbox=recheck_block(block,inter_block_num)
            get_block.extend(reject_bbox)
    
    remove_bbox = sorted(remove_bbox, key=lambda id:id,reverse=True)

    for rm in remove_bbox:
        craft_blocks[0].pop(rm)

    for bbox in get_block:
        craft_blocks[0].append(bbox)

    return craft_blocks