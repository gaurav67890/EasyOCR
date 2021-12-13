# EasyOCR Training



### 1.Convert All Pdf files to Images
```
a) python pdf-image.py

```
### 2. Prepare train, test, val folder that we will use as input in Easy ocr using below script
```
python textract_labels.py
```

### 3. Train the Easyocr model
```
python train_task.py

```

### 4. Dataset Path
```
a) /data/gaurav/all_data.zip : This contains dataset required for training Easyocr
b) /data/gaurav/total_img.zip: This contains images that we converted from pdfs. We use this data to achieve above dataset.

```
