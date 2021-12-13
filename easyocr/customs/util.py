import numpy as np

def get_area(bbox):
    x11,x12,y11,y12=bbox[:4]
    return abs((x12-x11)*(y12-y11))


def get_bbox_overlap(bbox1,bbox2):
    x11,x12,y11,y12=bbox1[:4]
    x21,x22,y21,y22=bbox2[:4]
    # If one rectangle is on left side of other
    if(x11 >= x22 or x21 >= x12):
        return [0,0,0,0]
 
    # If one rectangle is above other
    if(y12 <= y21 or y22 <= y11):
        return [0,0,0,0]
    overlap_x1=max(x11,x21)
    overlap_x2=min(x12,x22)
    overlap_y1=max(y11,y21)
    overlap_y2=min(y12,y22)
    return [overlap_x1,overlap_x2,overlap_y1,overlap_y2]

def check_overlap(bbox1,bbox2,thresh=0.9):

    overlap=get_bbox_overlap(bbox1,bbox2)
    if min(get_area(bbox1),get_area(bbox2))==0:
        return False
    # if get_area(overlap) /min(get_area(bbox1),get_area(bbox2))>0:
    #     print('get_area(overlap) /min(get_area(bbox1),get_area(bbox2)',get_area(overlap) /min(get_area(bbox1),get_area(bbox2)))
    if get_area(overlap) /min(get_area(bbox1),get_area(bbox2)) > thresh:
        return True
    
    return False

def check_bbox_in_group(list_group,bboxes,index):
    for grouped in list_group:
        if index in grouped:
            return True
        for m in grouped:
            if check_overlap(bboxes[index],bboxes[m]):
                grouped.append(index)
                return True 
    return False

def fiter_overlap_bbox(bboxes):
    list_group=[]
    for i in range(len(bboxes)-1,-1,-1):
        if check_bbox_in_group(list_group,bboxes,i):
            continue

        group_id=[i]
        for j in range(len(bboxes)-1,-1,-1):
            if i==j :
                continue
            if check_overlap(bboxes[i],bboxes[j]):
                group_id.append(j)

        if len(group_id) >1:
            list_group.append(group_id)

    pop_list=[]
    for group_id in list_group:
        if len(group_id) ==2:
            merge_x1= min(bboxes[group_id[0]][0],bboxes[group_id[-1]][0])
            merge_x2= max(bboxes[group_id[0]][1],bboxes[group_id[-1]][1])
            merge_y1= min(bboxes[group_id[0]][2],bboxes[group_id[-1]][2])
            merge_y2= max(bboxes[group_id[0]][3],bboxes[group_id[-1]][3])
            bboxes[min(group_id)]=[merge_x1,merge_x2,merge_y1,merge_y2, 0.5*(merge_y1+merge_y2), merge_y2-merge_y1]
            # bboxes[min(group_id)]=[merge_x1,merge_x2,merge_y1,merge_y2]
            pop_list.append(max(group_id))
        
        if len(group_id) >3 :
            group_id = sorted(group_id, key=lambda id: get_area(bboxes[id][:4]))
            
            max_bbox=bboxes[group_id[-1]]
            max_w=max_bbox[1] -max_bbox[0]
            max_h= max_bbox[1] -max_bbox[0]

            remain_w= [(bboxes[id][1]- bboxes[id][0]) for id in group_id[:-1]]
            remain_h= [(bboxes[id][3]- bboxes[id][2]) for id in group_id[:-1]]

            if max_h/np.mean(remain_h) >1.3 and  max_w/np.mean(remain_w)>1.3:
                pop_list.append(group_id[-1])
    pop_list = sorted(pop_list, key=lambda id:id,reverse=True)

    for pop_id in pop_list:
        bboxes.pop(pop_id)
    return bboxes

def correct_bboxes(bboxes):
    for i,bbox1 in enumerate(bboxes):
        bbox1_h= bbox1[3] -bbox1[2]
        for j,bbox2 in enumerate(bboxes):
            bbox2_h= bbox2[3] -bbox2[2]
            if bbox2_h==0:
                continue 

            if int(np.floor(bbox1_h/bbox2_h+ 0.5)) != 2:
                continue

            bbox11=[bbox1[0],bbox1[1],bbox1[2],int(bbox1[2] + 0.5*bbox1_h)]
            bbox12=[bbox1[0],bbox1[1],int(bbox1[2] + 0.5*bbox1_h),bbox1[3]]

            ovelap_112=get_bbox_overlap(bbox2,bbox11)
            ovelap_122=get_bbox_overlap(bbox2,bbox12)
            
            
            if (ovelap_122[3] -ovelap_122[2])/bbox2_h < 0.5 and (ovelap_112[3] -ovelap_112[2])/bbox2_h < 0.5:
                continue 
                
            if get_area(ovelap_112) > get_area(ovelap_122):
                
                bboxes[i] =bbox12

                merge_x1= min(bbox2[0],bbox11[0])
                merge_x2= max(bbox2[1],bbox11[1])
                merge_y1= min(bbox2[2],bbox11[2])
                merge_y2= max(bbox2[3],bbox11[3])
                bboxes[j] = [merge_x1,merge_x2,merge_y1,merge_y2]  
            else:
                bboxes[i] =bbox11
                merge_x1= min(bbox2[0],bbox12[0])
                merge_x2= max(bbox2[1],bbox12[1])
                merge_y1= min(bbox2[2],bbox12[2])
                merge_y2= max(bbox2[3],bbox12[3])
                bboxes[j] = [merge_x1,merge_x2,merge_y1,merge_y2]  
                
    return   bboxes      

        