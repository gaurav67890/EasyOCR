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
