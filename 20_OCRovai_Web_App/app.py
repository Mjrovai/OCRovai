
# Import Libraries and setup
from flask import Flask, request, render_template
import pyperclip
import os
import numpy as np
from PIL import Image
import pytesseract

# Functions

def filter_img(img):
    img = binarize_image(img, threshold=127)
    return img

def binarize_image(image, threshold):
    """Binarize an image."""
    image = image.convert('L')  # convert image to monochrome
    npimage = np.array(image)
    npimage = binarize_array(npimage, threshold)
    image = Image.fromarray(npimage)
    return image


def binarize_array(np_array, threshold):
    """Binarize a np array."""
    up = np_array > threshold
    new_arr = np.zeros_like(np_array)
    new_arr[up] = 255
    return new_arr


def ocr_image(imagePath, filename, filter, lang):
    img = Image.open(imagePath)
    if filter == 'on':
        img = filter_img(img)
    img.save('static/input_image.png')
    try:
        txt = pytesseract.image_to_string(img, lang=lang)
        prediction = "SUCCESS"
    except:
        txt = " pytesseract did not work properly with language: "+lang
        prediction = "FAILURE"
    txt_name = filename.split('.')[0]
    txt_path = 'static/text/recognized_text.txt'
    with open(txt_path, 'w') as f:
        f.write(txt)

    with open(txt_path, 'r') as f:
        content = f.readlines()

    cont = ''.join(content)
    #pyperclip.copy(cont)
    os.remove(imagePath)
    return prediction, content

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'])

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

filename='MJRoBot.png'
image_name = filename
prediction='STARTING'
language='unselected'
filter = 'off'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def hello_world():
	return render_template('index.html', )
    
@app.route("/query", methods=["POST"])
def query():
    if request.method == 'POST':
        # RECIBIR DATA DEL POST
        if 'file' not in request.files:
            return render_template('index.html', prediction='INCONCLUSIVE', filename='no image', image='static/MJRoBot.png')
        file = request.files['file']
        language = request.form["language"]
        filter = request.form["filter"]
        print(language, filter)
        # image_data = file.read()
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('index.html', prediction='INCONCLUSIVE', filename='no image')
        if file and allowed_file(file.filename):

            filename = str(file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(img_path)
            image_name = filename

            # ocr
            try:
                prediction, content = ocr_image(img_path, filename, filter=filter, lang=language)
                content = ''.join(content).split('\n')

                return render_template('index.html', prediction=prediction, filename=image_name, filter=filter, lang=language, image='static/input_image.png', text = content)
            except:
                return render_template('index.html', prediction='INCONCLUSIVE', filename=image_name, image=img_path)
        else:
            return render_template('index.html', prediction='FILE NOT ALOWED', filename=image_name, image=img_path)

# No caching at all for API endpoints.

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(host= '0.0.0.0')
