# import module
from pdf2image import convert_from_path
import glob

paths=glob.glob('total_pdf/*.pdf')

# Store Pdf with convert_from_path function
n=0
for path in paths:
    images = convert_from_path(path)

    for i in range(len(images)):
        n=n+1
        # Save pages as images in the pdf
        images[i].save('total_img/page' + str(n) + '.jpg', 'JPEG')
